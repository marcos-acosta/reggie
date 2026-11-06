from typing import Literal

from PIL import Image

from .geometry import Rect, Size
from .node import Node

Align = Literal["start", "center", "end", "stretch"]


class Spacer(Node):
    """Fixed gap when given a size, otherwise absorbs leftover space."""

    def __init__(self, size: int = 0, *, flex: int | None = None):
        self.size = size
        self.flex = (0 if size else 1) if flex is None else flex

    def measure(self, available: Size) -> Size:
        return Size(self.size, self.size)

    def draw(self, canvas: Image.Image, rect: Rect) -> None:
        pass


class _Flex(Node):
    horizontal: bool

    def __init__(self, *children: Node, gap: int = 0, align: Align = "stretch", flex: int = 0):
        self.children = children
        self.gap = gap
        self.align = align
        self.flex = flex

    def _main(self, size: Size) -> int:
        return size.w if self.horizontal else size.h

    def _cross(self, size: Size) -> int:
        return size.h if self.horizontal else size.w

    def _rect(self, origin: Rect, main_pos: int, cross_pos: int, main_len: int, cross_len: int) -> Rect:
        if self.horizontal:
            return Rect(origin.x + main_pos, origin.y + cross_pos, main_len, cross_len)
        return Rect(origin.x + cross_pos, origin.y + main_pos, cross_len, main_len)

    def _total_gap(self) -> int:
        return self.gap * max(0, len(self.children) - 1)

    def measure(self, available: Size) -> Size:
        sizes = [child.measure(available) for child in self.children]
        main = sum(self._main(s) for s in sizes) + self._total_gap()
        cross = max(
            (self._cross(s) for child, s in zip(self.children, sizes) if not isinstance(child, Spacer)),
            default=0,
        )
        return Size(main, cross) if self.horizontal else Size(cross, main)

    def draw(self, canvas: Image.Image, rect: Rect) -> None:
        sizes = [child.measure(rect.size) for child in self.children]
        lengths = self._main_lengths(sizes, self._main(rect.size))
        cross_space = self._cross(rect.size)

        position = 0
        for child, size, length in zip(self.children, sizes, lengths):
            cross_len, cross_pos = self._cross_placement(self._cross(size), cross_space)
            child.draw(canvas, self._rect(rect, position, cross_pos, length, cross_len))
            position += length + self.gap

    def _main_lengths(self, sizes: list[Size], space: int) -> list[int]:
        natural = [0 if child.flex else self._main(size) for child, size in zip(self.children, sizes)]
        leftover = max(0, space - sum(natural) - self._total_gap())
        total_flex = sum(child.flex for child in self.children)
        if not total_flex:
            return natural

        lengths, flex_seen, handed_out = [], 0, 0
        for child, length in zip(self.children, natural):
            if child.flex:
                flex_seen += child.flex
                length = leftover * flex_seen // total_flex - handed_out
                handed_out += length
            lengths.append(length)
        return lengths

    def _cross_placement(self, natural: int, space: int) -> tuple[int, int]:
        if self.align == "stretch":
            return space, 0
        length = min(natural, space)
        offset = {"start": 0, "center": (space - length) // 2, "end": space - length}[self.align]
        return length, offset


class Row(_Flex):
    horizontal = True


class Column(_Flex):
    horizontal = False
