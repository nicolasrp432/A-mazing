"""Cell representation and wall direction helpers.

A maze cell is modelled as a bit-mask of four walls — North, East, South,
West. The bit layout matches the subject's output format exactly, so the
in-memory representation is also the on-disk representation:

    bit 0 -> North
    bit 1 -> East
    bit 2 -> South
    bit 3 -> West

A bit set to ``1`` means the wall is closed; ``0`` means it is open.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import IntFlag


class Direction(IntFlag):
    """The four cardinal directions, packed as a bit-mask."""

    N = 1 << 0   # 0b0001 = 1
    E = 1 << 1   # 0b0010 = 2
    S = 1 << 2   # 0b0100 = 4
    W = 1 << 3   # 0b1000 = 8


ALL_WALLS: int = Direction.N | Direction.E | Direction.S | Direction.W  # 0xF


_OPPOSITE: dict[Direction, Direction] = {
    Direction.N: Direction.S,
    Direction.S: Direction.N,
    Direction.E: Direction.W,
    Direction.W: Direction.E,
}


# (dx, dy) offset associated with each direction.
# Convention: y grows downwards (row index), x grows rightwards (column).
_DELTA: dict[Direction, tuple[int, int]] = {
    Direction.N: (0, -1),
    Direction.E: (1, 0),
    Direction.S: (0, 1),
    Direction.W: (-1, 0),
}


def opposite(direction: Direction) -> Direction:
    """Return the direction facing the opposite cardinal point."""
    return _OPPOSITE[direction]


def delta(direction: Direction) -> tuple[int, int]:
    """Return the ``(dx, dy)`` step associated with ``direction``."""
    return _DELTA[direction]


@dataclass
class Cell:
    """A single maze cell.

    Attributes:
        walls: Bit-mask of currently *closed* walls. See :class:`Direction`.
            A freshly created cell has all four walls closed.
    """

    walls: int = ALL_WALLS

    def has_wall(self, direction: Direction) -> bool:
        """Return ``True`` if the wall in ``direction`` is closed."""
        return bool(self.walls & direction)

    def remove_wall(self, direction: Direction) -> None:
        """Open the wall in ``direction`` (clear the corresponding bit)."""
        self.walls &= ~direction

    def add_wall(self, direction: Direction) -> None:
        """Close the wall in ``direction`` (set the corresponding bit)."""
        self.walls |= direction

    def hex_digit(self) -> str:
        """Return the cell as a single uppercase hexadecimal digit."""
        return format(self.walls, "X")
