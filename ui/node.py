from abc import ABC, abstractmethod

from PIL import Image

from .geometry import Rect, Size


class Node(ABC):
    """A block that reports its natural size and draws itself into the rect it is given."""

    flex: int = 0

    @abstractmethod
    def measure(self, available: Size) -> Size: ...

    @abstractmethod
    def draw(self, canvas: Image.Image, rect: Rect) -> None: ...
