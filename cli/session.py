import importlib
import time
from collections.abc import Callable

from rich.console import Console

from config import remote_config
from display import Display

from .control import ControlServer
from .keys import KeyReader
from .picker import pick_screen
from .reloader import Watcher, fresh_import
from .remote import RemoteListener

POLL_INTERVAL = 0.1
RETRY_INTERVAL = 30
BRIGHTNESS_STEP = 25
OFF_SCREEN = "off"
HELP = (
    "[cyan]r[/] reload  [cyan]w[/] toggle watch  [cyan]s[/] switch screen  [cyan]n[/]/[cyan]p[/] next/prev  "
    "[cyan]+[/]/[cyan]-[/] brightness  [cyan]o[/] on/off  [cyan]q[/] quit"
)
KEY_COMMANDS = {"r": "reload", "o": "toggle", "n": "next", "p": "prev", "+": "brightness_up", "-": "brightness_down"}


def available_screens() -> list[str]:
    return sorted(fresh_import("screens").discover())


def load_screen(name: str):
    registry = fresh_import("screens").discover()
    if name not in registry:
        raise KeyError(f"Unknown screen {name!r}; available: {', '.join(sorted(registry))}")
    return registry[name]


class Session:
    def __init__(self, display: Display, console: Console, screen: str, watch: bool = True):
        self.display = display
        self.console = console
        self.screen = screen
        self.resume_screen: str | None = None
        self.watch = watch
        self.watcher = Watcher()
        self.keys = KeyReader()
        self.control = ControlServer.bind()
        self.remote_config = remote_config()
        self.remote = RemoteListener.bind(self.remote_config.port)
        self.key_actions = {"w": self.toggle_watch, "s": self.switch}
        self.commands: dict[str, Callable[[], str]] = {
            "on": self.power_on,
            "off": self.power_off,
            "toggle": self.toggle_power,
            "next": lambda: self.cycle_screen(1),
            "prev": lambda: self.cycle_screen(-1),
            "reload": self.reload,
            "brightness_up": lambda: self.adjust_brightness(BRIGHTNESS_STEP),
            "brightness_down": lambda: self.adjust_brightness(-BRIGHTNESS_STEP),
        }
        self.current = None
        self.next_render_at: float | None = None

    def run(self) -> None:
        self.display.on()
        self.reload()
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
                elif self._refresh_due():
                    self.render(quiet=True)
                self.display.sleep(POLL_INTERVAL)

    def run_command(self, name: str) -> str:
        handler = self.commands.get(name)
        return handler() if handler else f"error: unknown command {name!r}"

    def show_screen(self, name: str) -> str:
        self.screen = name
        return self.reload()

    def reload(self) -> str:
        self.watcher.sync()
        try:
            self.current = load_screen(self.screen)
        except Exception:
            self.console.print_exception(max_frames=4)
            return f"error: could not load {self.screen!r}"
        if not self.render():
            return f"error: could not render {self.screen!r}"
        self.console.print(f"[green]●[/] [bold]{self.screen}[/] [dim]{self._watch_label()}[/]")
        return self.screen

    def render(self, quiet: bool = False) -> bool:
        refresh = self.current.refresh
        try:
            self.display.show(importlib.import_module("ui").render(self.current.build()))
        except Exception as error:
            if quiet:
                self.console.print(f"[red]✗[/] {type(error).__name__}: {error}")
            else:
                self.console.print_exception(max_frames=4)
            self._schedule_render(refresh and min(refresh, RETRY_INTERVAL))
            return False
        self._schedule_render(refresh)
        return True

    def power_off(self) -> str:
        if self.screen != OFF_SCREEN:
            self.resume_screen = self.screen
            return self.show_screen(OFF_SCREEN)
        return OFF_SCREEN

    def power_on(self) -> str:
        if self.screen != OFF_SCREEN:
            return self.screen
        if not self.resume_screen:
            return "error: no screen to turn back on to"
        return self.show_screen(self.resume_screen)

    def toggle_power(self) -> str:
        return self.power_on() if self.screen == OFF_SCREEN else self.power_off()

    def cycle_screen(self, step: int) -> str:
        screens = [name for name in available_screens() if name != OFF_SCREEN]
        current = self.resume_screen if self.screen == OFF_SCREEN else self.screen
        index = screens.index(current) if current in screens else -1
        return self.show_screen(screens[(index + step) % len(screens)])

    def adjust_brightness(self, step: int) -> str:
        self.display.brightness(self.display.level + step)
        return f"brightness {self.display.level}"

    def toggle_watch(self) -> None:
        self.watch = not self.watch
        self.console.print(f"[dim]{self._watch_label()}[/]")

    def switch(self) -> None:
        with self.keys.paused():
            name = pick_screen(self.console, available_screens(), current=self.screen)
        self.show_screen(name)

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
        if not self.control:
            self.console.print("[yellow]Another session owns the control port; --on/--off won't reach this one[/]")
        if not self.remote:
            self.console.print(f"[yellow]Port {self.remote_config.port} is busy; IR remote presses won't reach this one[/]")

    def _schedule_render(self, delay: float | None) -> None:
        self.next_render_at = time.monotonic() + delay if delay else None

    def _refresh_due(self) -> bool:
        return self.next_render_at is not None and time.monotonic() >= self.next_render_at

    def _watch_label(self) -> str:
        return "watching for changes" if self.watch else "not watching (r to reload)"
