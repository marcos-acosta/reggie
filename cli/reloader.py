import importlib
import sys
from pathlib import Path
from types import ModuleType

ROOT = Path(__file__).resolve().parent.parent
RELOADABLE_PACKAGES = ("ui", "screens")


def _snapshot() -> dict[Path, float]:
    return {
        path: path.stat().st_mtime
        for package in RELOADABLE_PACKAGES
        for path in (ROOT / package).rglob("*.py")
    }


class Watcher:
    def __init__(self):
        self.sync()

    def sync(self) -> None:
        self.state = _snapshot()

    def changed(self) -> bool:
        current = _snapshot()
        changed, self.state = current != self.state, current
        return changed


def fresh_import(name: str) -> ModuleType:
    for module in list(sys.modules):
        if module.split(".")[0] in RELOADABLE_PACKAGES:
            del sys.modules[module]
    return importlib.import_module(name)
