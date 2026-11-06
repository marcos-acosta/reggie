import os

from config import display_config

from .base import SIZE, Display

__all__ = ["DISPLAY_KINDS", "SIZE", "Display", "default_kind", "open_display"]

DISPLAY_KINDS = ("matrix", "sim")


def default_kind() -> str:
    return os.environ.get("RGB64_DISPLAY", "matrix")


def open_display(kind: str | None = None) -> Display:
    kind = kind or default_kind()
    if kind not in DISPLAY_KINDS:
        raise ValueError(f"Unknown display {kind!r}; expected one of {DISPLAY_KINDS}")

    brightness = display_config(kind).brightness
    if kind == "sim":
        from .simulator import Simulator

        return Simulator(brightness)

    from .matrix import Matrix

    return Matrix(os.environ.get("RGB64_HOST", "matrix.local"), brightness)
