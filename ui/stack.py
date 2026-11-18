from PIL import Image

from .geometry import Rect, Size
from .node import Node


class Stack(Node):
    """Draws each layer over the previous one, all within the same rect."""

    def __init__(self, *layers: Node, flex: int = 0):
        self.layers = layers
        self.flex = flex

    def measure(self, available: Size) -> Size:
        sizes = [layer.measure(available) for layer in self.layers]
        return Size(max((s.w for s in sizes), default=0), max((s.h for s in sizes), default=0))

    def draw(self, canvas: Image.Image, rect: Rect) -> None:
        for layer in self.layers:
            layer.draw(canvas, rect)
