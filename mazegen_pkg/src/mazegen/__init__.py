"""Reusable maze-generation package.

Typical usage::

    from mazegen import MazeGenerator

    gen = MazeGenerator(width=20, height=15, seed=42, perfect=True)
    gen.generate()

    for row in gen.grid:
        print("".join(cell.hex_digit() for cell in row))

    path = gen.shortest_path(start=(0, 0), end=(19, 14))
"""

from .cell import ALL_WALLS, Cell, Direction, delta, opposite
from .generator import DIRECTIONS, MazeGenerator
from .solver import PathNotFoundError, path_to_directions, shortest_path

__all__ = [
    "ALL_WALLS",
    "Cell",
    "DIRECTIONS",
    "Direction",
    "MazeGenerator",
    "PathNotFoundError",
    "delta",
    "opposite",
    "path_to_directions",
    "shortest_path",
]

__version__ = "1.0.0"
