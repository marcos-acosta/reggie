import importlib

from PIL import Image
from rich.console import Console

from display import Display

from .keys import KeyReader
from .picker import pick_screen
from .reloader import Watcher, fresh_import

POLL_INTERVAL = 0.1
HELP = "[cyan]r[/] reload  [cyan]w[/] toggle watch  [cyan]s[/] switch screen  [cyan]q[/] quit"


def available_screens() -> list[str]:
    return sorted(fresh_import("screens").discover())


def render_screen(name: str) -> Image.Image:
    registry = fresh_import("screens").discover()
    if name not in registry:
        raise KeyError(f"Unknown screen {name!r}; available: {', '.join(sorted(registry))}")
    return importlib.import_module("ui").render(registry[name]())


class Session:
    def __init__(self, display: Display, console: Console, screen: str, watch: bool = True):
        self.display = display
        self.console = console
        self.screen = screen
        self.watch = watch
        self.watcher = Watcher()
        self.keys = KeyReader()
        self.actions = {"r": self.reload, "w": self.toggle_watch, "s": self.switch}

    def run(self) -> None:
        self.reload()
        if self.keys.interactive:
            self.console.print(HELP)
        with self.keys:
            while (key := self.keys.read()) != "q":
                if action := self.actions.get(key):
                    action()
                elif self.watch and self.watcher.changed():
                    self.reload()
                self.display.sleep(POLL_INTERVAL)

    def reload(self) -> None:
        self.watcher.sync()
        try:
            self.display.show(render_screen(self.screen))
        except Exception:
            self.console.print_exception(max_frames=4)
            return
        self.console.print(f"[green]●[/] [bold]{self.screen}[/] [dim]{self._watch_label()}[/]")

    def toggle_watch(self) -> None:
        self.watch = not self.watch
        self.console.print(f"[dim]{self._watch_label()}[/]")

    def switch(self) -> None:
        with self.keys.paused():
            self.screen = pick_screen(self.console, available_screens(), current=self.screen)
        self.reload()

    def _watch_label(self) -> str:
        return "watching for changes" if self.watch else "not watching (r to reload)"
