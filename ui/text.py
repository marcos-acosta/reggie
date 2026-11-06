from functools import cached_property

from PIL import Image, ImageDraw

from .fonts import DEFAULT_FONT, FontLike, resolve_font
from .geometry import Rect, Size
from .node import Node


class Text(Node):
    """Width ends at the last lit pixel; height is the font's full line height."""

    def __init__(self, content: str, *, color: str = "white", font: FontLike = DEFAULT_FONT, flex: int = 0):
        self.content = content
        self.color = color
        self.font = resolve_font(font)
        self.flex = flex

    @cached_property
    def _size(self) -> Size:
        _, top, _, bottom = self.font.getbbox(self.content)
        ink = self.font.getmask(self.content).getbbox()
        return Size(ink[2] if ink else 0, bottom - top)

    def measure(self, available: Size) -> Size:
        return self._size

    def draw(self, canvas: Image.Image, rect: Rect) -> None:
        if not rect.w or not rect.h:
            return
        layer = Image.new("RGBA", (rect.w, rect.h))
        ImageDraw.Draw(layer).text((0, 0), self.content, fill=self.color, font=self.font)
        canvas.paste(layer, (rect.x, rect.y), layer)
