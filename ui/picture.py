from PIL import Image, ImageOps

from .geometry import Rect, Size
from .node import Node


class Picture(Node):
    """Scales and center-crops the image to fill its rect."""

    def __init__(self, image: Image.Image, *, width: int | None = None, height: int | None = None, flex: int = 0):
        self.image = image.convert("RGB")
        self.width = width
        self.height = height
        self.flex = flex

    def measure(self, available: Size) -> Size:
        return Size(self.width or self.image.width, self.height or self.image.height)

    def draw(self, canvas: Image.Image, rect: Rect) -> None:
        if rect.w and rect.h:
            canvas.paste(ImageOps.fit(self.image, (rect.w, rect.h), Image.LANCZOS), (rect.x, rect.y))
