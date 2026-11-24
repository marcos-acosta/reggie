import numpy as np
from PIL import Image, ImageColor

from screens import screen
from services import subway, subway_map
from ui import Node, Picture

BACKGROUND = "black"
TRACK = "#1A1A1A"
BLUE, ORANGE, YELLOW, RED, GREEN = "#0062CF", "#EB6800", "#F6BC26", "#D82233", "#009952"
# The MTA's gray (#7C858C) would disappear into the tracks.
LIGHT_GRAY = "#E0E6EB"
ROUTE_COLORS = {
    **dict.fromkeys("ACE", BLUE),
    **dict.fromkeys("BDFM", ORANGE),
    **dict.fromkeys("NQRW", YELLOW),
    **dict.fromkeys("123", RED),
    **dict.fromkeys("456", GREEN),
    **dict.fromkeys("JZ", "#8E5C33"),
    **dict.fromkeys(("L", "GS", "FS", "H"), LIGHT_GRAY),
    "G": "#799534",
    "7": "#9A38A1",
}
EXCLUDED_ROUTES = {"SI"}


def route_color(route: str) -> str:
    return ROUTE_COLORS.get(route.removesuffix("X"), LIGHT_GRAY)


@screen("subway", refresh=10)
def subway_screen() -> Node:
    trains = [
        train for train in subway.fetch_trains() if train.route not in EXCLUDED_ROUTES
    ]
    pixels = np.empty((*subway_map.TRACKS.shape, 3), dtype=np.uint8)
    pixels[:] = ImageColor.getrgb(BACKGROUND)
    pixels[subway_map.TRACKS] = ImageColor.getrgb(TRACK)
    for pixel, train in subway_map.place_trains(trains).items():
        pixels[pixel] = ImageColor.getrgb(route_color(train.route))
    return Picture(Image.fromarray(pixels))
