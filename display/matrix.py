import socket
import time

import numpy as np

from .base import SIZE, Display, DisplayUnreachable, Pixels

PORT = 7777
ROWS_PER_CHUNK = 8
CHUNK_DELAY = 0.0005
LOOKUP_INTERVAL = 30


def to_rgb565(pixels: Pixels) -> np.ndarray:
    a = pixels.astype(np.uint16)
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    return (((r >> 3) << 11) | ((g >> 2) << 5) | (b >> 3)).astype("<u2")


class Matrix(Display):
    def __init__(self, host: str, brightness: int):
        super().__init__(brightness)
        self.host = host
        self.ip: str | None = None
        self.next_lookup_at = 0.0
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def _send(self, pixels: Pixels) -> None:
        packed = to_rgb565(pixels)
        for row in range(0, SIZE, ROWS_PER_CHUNK):
            chunk = packed[row : row + ROWS_PER_CHUNK].tobytes()
            self._transmit(b"F" + bytes([row]) + chunk)
            time.sleep(CHUNK_DELAY)

    def _apply_brightness(self, level: int) -> None:
        self._transmit(b"B" + bytes([level]))

    def _transmit(self, packet: bytes) -> None:
        self._refresh_ip()
        try:
            self.sock.sendto(packet, (self.ip, PORT))
        except OSError as error:
            raise DisplayUnreachable(f"could not send to {self.host}: {error}") from error

    def _refresh_ip(self) -> None:
        if self.ip and time.monotonic() < self.next_lookup_at:
            return
        try:
            self.ip = socket.gethostbyname(self.host)
        except OSError as error:
            if not self.ip:
                raise DisplayUnreachable(f"could not find {self.host}: {error}") from error
        self.next_lookup_at = time.monotonic() + LOOKUP_INTERVAL
