from dataclasses import dataclass


@dataclass(frozen=True)
class Size:
    w: int
    h: int

    def grow(self, insets: "Insets") -> "Size":
        return Size(self.w + insets.horizontal, self.h + insets.vertical)

    def shrink(self, insets: "Insets") -> "Size":
        return Size(max(0, self.w - insets.horizontal), max(0, self.h - insets.vertical))


@dataclass(frozen=True)
class Insets:
    top: int = 0
    right: int = 0
    bottom: int = 0
    left: int = 0

    @classmethod
    def of(cls, value: "InsetsLike") -> "Insets":
        """CSS shorthand: n, (vertical, horizontal), or (top, right, bottom, left)."""
        if isinstance(value, Insets):
            return value
        if isinstance(value, int):
            return cls(value, value, value, value)
        if len(value) == 2:
            vertical, horizontal = value
            return cls(vertical, horizontal, vertical, horizontal)
        return cls(*value)

    @property
    def horizontal(self) -> int:
        return self.left + self.right

    @property
    def vertical(self) -> int:
        return self.top + self.bottom


InsetsLike = Insets | int | tuple[int, int] | tuple[int, int, int, int]


@dataclass(frozen=True)
class Rect:
    x: int
    y: int
    w: int
    h: int

    @property
    def size(self) -> Size:
        return Size(self.w, self.h)

    @property
    def corners(self) -> tuple[int, int, int, int]:
        """Inclusive pixel coordinates, as ImageDraw shapes expect."""
        return (self.x, self.y, self.x + self.w - 1, self.y + self.h - 1)

    def inset(self, insets: Insets) -> "Rect":
        return Rect(
            self.x + insets.left,
            self.y + insets.top,
            max(0, self.w - insets.horizontal),
            max(0, self.h - insets.vertical),
        )
