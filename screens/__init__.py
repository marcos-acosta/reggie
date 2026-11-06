import importlib
import pkgutil
from collections.abc import Callable
from dataclasses import dataclass

from ui import Node

Build = Callable[[], Node]


@dataclass(frozen=True)
class Screen:
    build: Build
    refresh: float | None = None


_registry: dict[str, Screen] = {}


def screen(name: str | None = None, *, refresh: float | None = None) -> Callable[[Build], Build]:
    def register(build: Build) -> Build:
        key = name or build.__name__
        if key in _registry:
            raise ValueError(f"Screen {key!r} is already registered")
        _registry[key] = Screen(build, refresh)
        return build

    return register


def discover() -> dict[str, Screen]:
    for module in pkgutil.iter_modules(__path__):
        importlib.import_module(f"{__name__}.{module.name}")
    return dict(_registry)
