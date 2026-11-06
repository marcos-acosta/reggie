from PIL import Image

from display import SIZE

from .geometry import Rect
from .node import Node


def render(root: Node, background: str = "black", size: int = SIZE) -> Image.Image:
    canvas = Image.new("RGB", (size, size), background)
    root.draw(canvas, Rect(0, 0, size, size))
    return canvas
