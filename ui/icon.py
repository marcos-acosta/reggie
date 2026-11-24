from functools import cache
from pathlib import Path

from PIL import Image

from .geometry import Rect, Size
from .node import Node

ICONS = Path(__file__).parent / "assets" / "icons"
OPAQUE_THRESHOLD = 128


@cache
def load_icon(name: str) -> Image.Image:
    path = ICONS / f"{name}.png"
    if not path.exists():
        available = ", ".join(sorted(p.stem for p in ICONS.glob("*.png"))) or "none"
        raise ValueError(f"Unknown icon {name!r}; available: {available}")
    with Image.open(path) as image:
        if not image.has_transparency_data:
            raise ValueError(f"Icon {name!r} needs a transparent background")
        alpha = image.convert("RGBA").getchannel("A")
    return alpha.point(lambda a: 255 if a >= OPAQUE_THRESHOLD else 0)


class Icon(Node):
    """Fills the opaque pixels of assets/icons/<name>.png with a single color."""

    def __init__(self, name: str, *, color: str = "white", flex: int = 0):
        self.mask = load_icon(name)
        self.color = color
        self.flex = flex

    def measure(self, available: Size) -> Size:
        return Size(*self.mask.size)

    def draw(self, canvas: Image.Image, rect: Rect) -> None:
        mask = self.mask.crop((0, 0, rect.w, rect.h))
        canvas.paste(Image.new("RGB", mask.size, self.color), (rect.x, rect.y), mask)
