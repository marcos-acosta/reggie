import time
from abc import ABC, abstractmethod

import numpy as np
from PIL import Image, ImageOps

SIZE = 64
SHAPE = (SIZE, SIZE, 3)

Pixels = np.ndarray


def fit(img: Image.Image) -> Image.Image:
    return ImageOps.fit(img.convert("RGB"), (SIZE, SIZE), Image.LANCZOS)


class Display(ABC):
    def __init__(self, brightness: int):
        self.level = brightness

    def show(self, img: Image.Image) -> None:
        self.show_pixels(np.asarray(fit(img)))

    def show_pixels(self, pixels: Pixels) -> None:
        """pixels: (64, 64, 3) uint8 RGB array, row-major from the top-left."""
        if pixels.shape != SHAPE or pixels.dtype != np.uint8:
            raise ValueError(f"Expected uint8 array of shape {SHAPE}, got {pixels.dtype} {pixels.shape}")
        self._send(pixels)

    @abstractmethod
    def _send(self, pixels: Pixels) -> None: ...

    @abstractmethod
    def _apply_brightness(self, level: int) -> None: ...

    def brightness(self, level: int) -> None:
        self.level = max(0, min(255, level))
        self._apply_brightness(self.level)

    def on(self) -> None:
        self._apply_brightness(self.level)

    def off(self) -> None:
        self._apply_brightness(0)

    def sleep(self, seconds: float) -> None:
        time.sleep(seconds)

    def hold(self) -> None:
        """Keep the current image visible until the user closes the display, if that applies."""
