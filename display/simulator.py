import sys
import time
import tkinter as tk

import numpy as np
from PIL import Image, ImageDraw, ImageTk

from .base import SHAPE, SIZE, Display, Pixels

FRAME_INTERVAL = 1 / 60


def led_mask(scale: int) -> Image.Image:
    cell = Image.new("L", (scale, scale), 0)
    inset = max(1, scale // 8)
    ImageDraw.Draw(cell).ellipse((inset, inset, scale - inset - 1, scale - inset - 1), fill=255)
    mask = Image.new("L", (SIZE * scale, SIZE * scale))
    for y in range(SIZE):
        for x in range(SIZE):
            mask.paste(cell, (x * scale, y * scale))
    return mask


class Simulator(Display):
    def __init__(self, brightness: int, scale: int = 10):
        super().__init__(brightness)
        self.scale = scale
        self.mask = led_mask(scale)
        self.pixels = np.zeros(SHAPE, dtype=np.uint8)
        self.applied_level = self.level

        self.root = tk.Tk()
        self.root.title("rgb64 simulator")
        self.root.resizable(False, False)
        self.root.protocol("WM_DELETE_WINDOW", sys.exit)
        self.label = tk.Label(self.root, bg="black", borderwidth=0)
        self.label.pack()
        self._render()

    def _send(self, pixels: Pixels) -> None:
        self.pixels = pixels
        self._render()

    def _apply_brightness(self, level: int) -> None:
        self.applied_level = level
        self._render()

    def sleep(self, seconds: float) -> None:
        deadline = time.monotonic() + seconds
        while (remaining := deadline - time.monotonic()) > 0:
            self.root.update()
            time.sleep(min(remaining, FRAME_INTERVAL))

    def hold(self) -> None:
        self.root.mainloop()

    def _render(self) -> None:
        dimmed = Image.fromarray((self.pixels.astype(np.uint16) * self.applied_level // 255).astype(np.uint8))
        size = (SIZE * self.scale, SIZE * self.scale)
        leds = Image.new("RGB", size)
        leds.paste(dimmed.resize(size, Image.NEAREST), mask=self.mask)

        self.photo = ImageTk.PhotoImage(leds)
        self.label.configure(image=self.photo)
        self.root.update()
