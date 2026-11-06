from PIL import Image, ImageDraw

from .geometry import Insets, InsetsLike, Rect, Size
from .node import Node


class Box(Node):
    """Margin sits outside the background, padding inside it."""

    def __init__(
        self,
        child: Node | None = None,
        *,
        padding: InsetsLike = 0,
        margin: InsetsLike = 0,
        background: str | None = None,
        width: int | None = None,
        height: int | None = None,
        flex: int = 0,
    ):
        self.child = child
        self.padding = Insets.of(padding)
        self.margin = Insets.of(margin)
        self.background = background
        self.width = width
        self.height = height
        self.flex = flex

    def measure(self, available: Size) -> Size:
        inner_available = available.shrink(self.margin).shrink(self.padding)
        inner = self.child.measure(inner_available) if self.child else Size(0, 0)
        content = inner.grow(self.padding)
        sized = Size(
            content.w if self.width is None else self.width,
            content.h if self.height is None else self.height,
        )
        return sized.grow(self.margin)

    def draw(self, canvas: Image.Image, rect: Rect) -> None:
        outer = rect.inset(self.margin)
        if self.background and outer.w and outer.h:
            ImageDraw.Draw(canvas).rectangle(outer.corners, fill=self.background)
        if self.child:
            self.child.draw(canvas, outer.inset(self.padding))
