from functools import cache
from pathlib import Path

from PIL import BdfFontFile, ImageFont

ASSETS = Path(__file__).parent / "assets"
BDF_FONTS = {"tom-thumb": "tom-thumb.bdf", "5x7": "5x7.bdf"}
FONT_NAMES = tuple(BDF_FONTS)
DEFAULT_FONT = "tom-thumb"

Font = ImageFont.ImageFont
FontLike = Font | str


@cache
def load_font(name: str) -> Font:
    if name not in BDF_FONTS:
        raise ValueError(f"Unknown font {name!r}; expected one of {FONT_NAMES}")
    with open(ASSETS / BDF_FONTS[name], "rb") as fp:
        return BdfFontFile.BdfFontFile(fp).to_imagefont()


def resolve_font(font: FontLike) -> Font:
    return load_font(font) if isinstance(font, str) else font
