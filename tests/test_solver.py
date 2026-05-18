"""Unit tests for :mod:`mazegen.solver`."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

_PKG_SRC = Path(__file__).resolve().parents[1] / "mazegen_pkg" / "src"
if str(_PKG_SRC) not in sys.path:
    sys.path.insert(0, str(_PKG_SRC))

from mazegen import MazeGenerator  # noqa: E402
from mazegen.cell import Cell, Direction  # noqa: E402
from mazegen.solver import (  # noqa: E402
    PathNotFoundError, path_to_directions, shortest_path,
)


def _open_corridor() -> list[list[Cell]]:
    """Build a 3x1 corridor with all internal walls open."""
    cells = [Cell(walls=15), Cell(walls=15), Cell(walls=15)]
    cells[0].remove_wall(Direction.E)
    cells[1].remove_wall(Direction.W)
    cells[1].remove_wall(Direction.E)
    cells[2].remove_wall(Direction.W)
    return [cells]


def test_path_to_directions_basic() -> None:
    path = [(0, 0), (1, 0), (1, 1), (0, 1)]
    assert path_to_directions(path) == "ESW"


def test_path_to_directions_empty_for_short_path() -> None:
    assert path_to_directions([]) == ""
    assert path_to_directions([(5, 5)]) == ""


def test_start_equals_end() -> None:
    grid = _open_corridor()
    assert shortest_path(grid, (0, 0), (0, 0)) == [(0, 0)]


def test_corridor_path() -> None:
    grid = _open_corridor()
    assert shortest_path(grid, (0, 0), (2, 0)) == [(0, 0), (1, 0), (2, 0)]


def test_unreachable_raises() -> None:
    grid = [[Cell(), Cell()]]  # both fully walled, no connection
    with pytest.raises(PathNotFoundError):
        shortest_path(grid, (0, 0), (1, 0))


def test_path_on_perfect_maze_is_unique_and_walkable() -> None:
    gen = MazeGenerator(width=10, height=8, seed=7, perfect=True)
    gen.generate()
    path = gen.shortest_path((0, 0), (9, 7))
    assert path[0] == (0, 0) and path[-1] == (9, 7)

    # Every step traverses an OPEN wall.
    deltas = {
        (0, -1): Direction.N, (1, 0): Direction.E,
        (0, 1): Direction.S, (-1, 0): Direction.W,
    }
    for (x1, y1), (x2, y2) in zip(path, path[1:]):
        direction = deltas[(x2 - x1, y2 - y1)]
        assert not gen.grid[y1][x1].has_wall(direction)
