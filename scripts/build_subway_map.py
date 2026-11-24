"""Regenerates services/subway_map.json from the MTA's published track shapes."""

import csv
import io
import json
import zipfile
from pathlib import Path

import numpy as np
import requests
from PIL import Image, ImageDraw

GTFS_URL = "https://rrgtfsfeeds.s3.amazonaws.com/gtfs_subway.zip"
OUTPUT = Path(__file__).resolve().parent.parent / "services" / "subway_map.json"
SIZE = 64
MARGIN = 1
EXCLUDED_ROUTES = {"SI"}
# How far to stretch dense areas apart: 0 is linear, 1 spreads track evenly over the panel.
LON_WARP = 0.3
LAT_WARP = 0.2
KNOTS = 50
SAMPLE_DEGREES = 0.001

NEIGHBORS = [(-1, 0), (-1, 1), (0, 1), (1, 1), (1, 0), (1, -1), (0, -1), (-1, -1)]
ORTHOGONAL = (0, 4, 2, 6)


def load_lines() -> list[np.ndarray]:
    response = requests.get(GTFS_URL, timeout=60)
    response.raise_for_status()
    with zipfile.ZipFile(io.BytesIO(response.content)) as archive:
        def rows(name: str):
            return csv.DictReader(io.TextIOWrapper(archive.open(name), "utf-8-sig"))

        included = {row["shape_id"] for row in rows("trips.txt") if row["route_id"] not in EXCLUDED_ROUTES}
        shapes: dict[str, list[tuple[float, float]]] = {}
        for row in rows("shapes.txt"):
            if row["shape_id"] in included:
                shapes.setdefault(row["shape_id"], []).append((float(row["shape_pt_lon"]), float(row["shape_pt_lat"])))
    return [np.array(points) for points in shapes.values()]


def sample_track(lines: list[np.ndarray]) -> np.ndarray:
    """Evenly spaced points along all track, counting shared track once."""
    cells = set()
    for line in lines:
        for start, end in zip(line[:-1], line[1:]):
            steps = max(1, int(np.hypot(*(end - start)) / SAMPLE_DEGREES * 1.5))
            for point in start + (end - start) * np.linspace(0, 1, steps, endpoint=False)[:, None]:
                cells.add(tuple(np.rint(point / SAMPLE_DEGREES).astype(int)))
    return np.array(list(cells)) * SAMPLE_DEGREES


def axis_curve(values: np.ndarray, samples: np.ndarray, warp: float) -> tuple[np.ndarray, np.ndarray]:
    knots = np.linspace(values.min(), values.max(), KNOTS)
    linear = np.linspace(0, 1, KNOTS)
    density = np.searchsorted(np.sort(samples), knots) / len(samples)
    return knots, MARGIN + ((1 - warp) * linear + warp * density) * (SIZE - 1 - 2 * MARGIN)


def thin(grid: np.ndarray) -> np.ndarray:
    """Reduces lines to one pixel wide without breaking or shortening them."""
    grid = np.pad(grid, 1)
    changed = True
    while changed:
        changed = False
        for side in ORTHOGONAL:
            exposed = grid & ~np.roll(grid, (-NEIGHBORS[side][0], -NEIGHBORS[side][1]), (0, 1))
            for y, x in np.argwhere(exposed):
                around = [grid[y + dy, x + dx] for dy, dx in NEIGHBORS]
                branches = sum(not around[i] and (around[i + 1] or around[(i + 2) % 8]) for i in (0, 2, 4, 6))
                if sum(around) >= 2 and branches == 1:
                    grid[y, x] = False
                    changed = True
    return grid[1:-1, 1:-1]


def main() -> None:
    lines = load_lines()
    points, samples = np.vstack(lines), sample_track(lines)
    lon, x = axis_curve(points[:, 0], samples[:, 0], LON_WARP)
    lat, y = axis_curve(points[:, 1], samples[:, 1], LAT_WARP)
    y = SIZE - 1 - y

    image = Image.new("1", (SIZE, SIZE))
    draw = ImageDraw.Draw(image)
    for line in lines:
        pixels = np.rint(np.c_[np.interp(line[:, 0], lon, x), np.interp(line[:, 1], lat, y)]).astype(int)
        draw.line([tuple(pixel) for pixel in pixels.tolist()], fill=1)
    tracks = thin(np.array(image))

    data = {
        "lon": lon.round(5).tolist(),
        "x": x.round(3).tolist(),
        "lat": lat.round(5).tolist(),
        "y": y.round(3).tolist(),
        "tracks": ["".join(".#"[int(lit)] for lit in row) for row in tracks],
    }
    OUTPUT.write_text(json.dumps(data, indent=1) + "\n")
    print(f"Wrote {OUTPUT} ({tracks.sum()} track pixels)")


if __name__ == "__main__":
    main()
