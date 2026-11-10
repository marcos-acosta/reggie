import socket
import time

import numpy as np

from .base import SIZE, Display, Pixels

PORT = 7777
ROWS_PER_CHUNK = 8
CHUNK_DELAY = 0.0005


def to_rgb565(pixels: Pixels) -> np.ndarray:
    a = pixels.astype(np.uint16)
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    return (((r >> 3) << 11) | ((g >> 2) << 5) | (b >> 3)).astype("<u2")


class Matrix(Display):
    def __init__(self, host: str, brightness: int):
        super().__init__(brightness)
        self.addr = (socket.gethostbyname(host), PORT)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def _send(self, pixels: Pixels) -> None:
        packed = to_rgb565(pixels)
        for row in range(0, SIZE, ROWS_PER_CHUNK):
            chunk = packed[row : row + ROWS_PER_CHUNK].tobytes()
            self.sock.sendto(b"F" + bytes([row]) + chunk, self.addr)
            time.sleep(CHUNK_DELAY)

    def _apply_brightness(self, level: int) -> None:
        self.sock.sendto(b"B" + bytes([level]), self.addr)
