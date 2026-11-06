import socket
import time

import numpy as np
from PIL import Image, ImageOps

SIZE = 64
ROWS_PER_CHUNK = 8
PORT = 7777


def to_rgb565(img: Image.Image) -> np.ndarray:
    """Crop/resize to 64x64; return (64, 64) little-endian RGB565 array."""
    img = ImageOps.fit(img.convert("RGB"), (SIZE, SIZE), Image.LANCZOS)
    a = np.asarray(img, dtype=np.uint16)
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    return (((r >> 3) << 11) | ((g >> 2) << 5) | (b >> 3)).astype("<u2")


class Matrix:
    def __init__(self, host: str = "matrix.local"):
        self.addr = (socket.gethostbyname(host), PORT)  # resolve mDNS once
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.level = 80

    def show(self, img: Image.Image):
        pixels = to_rgb565(img)
        for row in range(0, SIZE, ROWS_PER_CHUNK):
            chunk = pixels[row : row + ROWS_PER_CHUNK].tobytes()
            self.sock.sendto(b"F" + bytes([row]) + chunk, self.addr)
            time.sleep(0.0005)  # don't flood the ESP32's receive queue

    def off(self):
        self._send_brightness(0)

    def on(self):
        self._send_brightness(self.level)

    def brightness(self, level: int):
        self.level = max(min(level, 255), 0)
        self._send_brightness(self.level)

    def _send_brightness(self, level: int):
        self.sock.sendto(b"B" + bytes([max(0, min(255, level))]), self.addr)
