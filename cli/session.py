import importlib
import time
from collections.abc import Callable

from rich.console import Console

from config import remote_config
from display import Display

from .control import ControlServer
from .keys import KeyReader
from .lineup import Lineup, build_lineup
from .picker import pick_screen
from .reloader import Watcher, fresh_import
from .remote import RemoteListener

POLL_INTERVAL = 0.1
RETRY_INTERVAL = 30
LABEL_SECONDS = 2.0
BRIGHTNESS_STEP = 25
HELP = (
    "[cyan]1-9[/] screen  [cyan]n[/]/[cyan]p[/] next/prev  [cyan]s[/] pick  [cyan]r[/] reload  "
    "[cyan]w[/] watch  [cyan]+[/]/[cyan]-[/] brightness  [cyan]o[/] on/off  [cyan]q[/] quit"
)
KEY_COMMANDS = {
    "r": "reload",
    "o": "toggle",
    "n": "next",
    "p": "prev",
    "+": "brightness_up",
    "-": "brightness_down",
    **{str(number): f"screen {number}" for number in range(1, 10)},
}


def load_lineup() -> tuple[Lineup, dict]:
    registry = fresh_import("screens").discover()
    return build_lineup(registry), registry


class Session:
    def __init__(self, display: Display, console: Console, screen: str, watch: bool = True):
        self.display = display
        self.console = console
        self.screen = screen
        self.powered = True
        self.watch = watch
        self.watcher = Watcher()
        self.keys = KeyReader()
        self.control = ControlServer.bind()
        self.remote_config = remote_config()
        self.remote = RemoteListener.bind(self.remote_config.port)
        self.lineup, self.registry = load_lineup()
        self.content = None
        self.label_until: float | None = None
        self.next_build_at: float | None = None
        self.key_actions = {"w": self.toggle_watch, "s": self.pick}
        self.commands: dict[str, Callable[[], str]] = {
            "on": self.power_on,
            "off": self.power_off,
            "toggle": self.toggle_power,
            "next": lambda: self.show_screen(self.lineup.step(self.screen, 1).id),
            "prev": lambda: self.show_screen(self.lineup.step(self.screen, -1).id),
            "reload": self.reload,
            "brightness_up": lambda: self.adjust_brightness(BRIGHTNESS_STEP),
            "brightness_down": lambda: self.adjust_brightness(-BRIGHTNESS_STEP),
        }

    def run(self) -> None:
        self.display.on()
        self.show_screen(self.screen)
        self._print_startup_notes()
        with self.keys:
            while (key := self.keys.read()) != "q":
                if command := KEY_COMMANDS.get(key):
                    self.run_command(command)
                elif action := self.key_actions.get(key):
                    action()
                self._handle_control()
                self._handle_remote()
                if self.watch and self.watcher.changed():
                    self.reload()
                elif self._due(self.next_build_at):
                    self.build(quiet=True)
                elif self._due(self.label_until):
                    self.label_until = None
                    self.draw()
                self.display.sleep(POLL_INTERVAL)

    def run_command(self, line: str) -> str:
        name, _, argument = line.strip().partition(" ")
        if name == "screen":
            return self.select_screen(argument)
        handler = self.commands.get(name)
        return handler() if handler else f"error: unknown command {name!r}"

    def select_screen(self, key: str) -> str:
        entry = self.lineup.find(key)
        return self.show_screen(entry.id) if entry else f"error: no screen {key!r}"

    def show_screen(self, screen_id: str) -> str:
        self.screen = screen_id
        self.powered = True
        self.label_until = time.monotonic() + LABEL_SECONDS
        return self.reload()

    def reload(self) -> str:
        self.watcher.sync()
        try:
            self.lineup, self.registry = load_lineup()
        except Exception:
            self.console.print_exception(max_frames=4)
            return "error: could not load screens"
        if self.screen not in self.registry:
            return f"error: no screen {self.screen!r}"
        if not self.powered:
            return "off"
        if not self.build():
            return f"error: could not build {self.screen!r}"
        self.console.print(f"[green]●[/] [bold]{self._label()}[/] [dim]{self._watch_label()}[/]")
        return self._label()

    def build(self, quiet: bool = False) -> bool:
        screen = self.registry[self.screen]
        try:
            self.content = screen.build()
            self.draw()
        except Exception as error:
            if quiet:
                self.console.print(f"[red]✗[/] {type(error).__name__}: {error}")
            else:
                self.console.print_exception(max_frames=4)
            self._schedule_build(screen.refresh and min(screen.refresh, RETRY_INTERVAL))
            return False
        self._schedule_build(screen.refresh)
        return True

    def draw(self) -> None:
        if self.content is None:
            return
        ui = importlib.import_module("ui")
        node = self.content
        if self.label_until and (entry := self._entry()):
            label = ui.Box(
                ui.Row(ui.Text(str(entry.number), color="yellow"), ui.Text(entry.name), gap=3),
                padding=1,
                margin=2,
                background="black",
            )
            node = ui.Stack(node, ui.Column(ui.Row(label)))
        self.display.show(ui.render(node))

    def power_off(self) -> str:
        self.powered = False
        self.next_build_at = self.label_until = None
        self.display.clear()
        self.console.print("[dim]○ off[/]")
        return "off"

    def power_on(self) -> str:
        return self._label() if self.powered else self.show_screen(self.screen)

    def toggle_power(self) -> str:
        return self.power_off() if self.powered else self.power_on()

    def adjust_brightness(self, step: int) -> str:
        self.display.brightness(self.display.level + step)
        return f"brightness {self.display.level}"

    def toggle_watch(self) -> None:
        self.watch = not self.watch
        self.console.print(f"[dim]{self._watch_label()}[/]")

    def pick(self) -> None:
        with self.keys.paused():
            entry = pick_screen(self.console, self.lineup, current_id=self.screen)
        self.show_screen(entry.id)

    def _handle_control(self) -> None:
        if not self.control or not (message := self.control.poll()):
            return
        command, sender = message
        self.control.reply(sender, self.run_command(command))

    def _handle_remote(self) -> None:
        if not self.remote or not (press := self.remote.poll()):
            return
        action = self.remote_config.buttons.get(press.command)
        if press.address != self.remote_config.address or not action:
            self.console.print(f"[dim]IR button {press.command} (address {press.address}) is not mapped[/]")
            return
        self.console.print(f"[magenta]IR[/] {action} → {self.run_command(action)}")

    def _print_startup_notes(self) -> None:
        if self.keys.interactive:
            self.console.print(HELP)
        if self.lineup.unknown_ids:
            self.console.print(f"[yellow]config.toml lists unknown screens: {', '.join(self.lineup.unknown_ids)}[/]")
        if not self.control:
            self.console.print("[yellow]Another session owns the control port; --on/--off won't reach this one[/]")
        if not self.remote:
            self.console.print(f"[yellow]Port {self.remote_config.port} is busy; IR remote presses won't reach this one[/]")

    def _entry(self):
        return next((entry for entry in self.lineup.entries if entry.id == self.screen), None)

    def _label(self) -> str:
        entry = self._entry()
        return entry.label if entry else self.screen

    def _schedule_build(self, delay: float | None) -> None:
        self.next_build_at = time.monotonic() + delay if delay else None

    @staticmethod
    def _due(deadline: float | None) -> bool:
        return deadline is not None and time.monotonic() >= deadline

    def _watch_label(self) -> str:
        return "watching for changes" if self.watch else "not watching (r to reload)"
