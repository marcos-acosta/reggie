import os
import select
import sys
import termios
import tty
from collections.abc import Iterator
from contextlib import contextmanager


class KeyReader:
    """Non-blocking single-key input; inert when stdin is not a terminal."""

    def __init__(self):
        self.fd = sys.stdin.fileno() if sys.stdin.isatty() else None
        self.saved: list | None = None

    @property
    def interactive(self) -> bool:
        return self.fd is not None

    def __enter__(self) -> "KeyReader":
        self._enable()
        return self

    def __exit__(self, *_) -> None:
        self._restore()

    def read(self) -> str | None:
        if self.fd is None:
            return None
        ready, _, _ = select.select([self.fd], [], [], 0)
        return os.read(self.fd, 1).decode(errors="ignore") if ready else None

    @contextmanager
    def paused(self) -> Iterator[None]:
        self._restore()
        try:
            yield
        finally:
            self._enable()

    def _enable(self) -> None:
        if self.fd is not None:
            self.saved = termios.tcgetattr(self.fd)
            tty.setcbreak(self.fd)

    def _restore(self) -> None:
        if self.fd is not None and self.saved is not None:
            termios.tcsetattr(self.fd, termios.TCSADRAIN, self.saved)
