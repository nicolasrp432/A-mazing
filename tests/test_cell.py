"""Unit tests for :mod:`mazegen.cell`."""

from __future__ import annotations

import sys
from pathlib import Path

# Ensure the reusable package is importable when running tests in-tree.
_PKG_SRC = Path(__file__).resolve().parents[1] / "mazegen_pkg" / "src"
if str(_PKG_SRC) not in sys.path:
    sys.path.insert(0, str(_PKG_SRC))

from mazegen.cell import (  # noqa: E402
    ALL_WALLS, Cell, Direction, delta, opposite,
)


def test_initial_cell_has_all_walls() -> None:
    cell = Cell()
    assert cell.walls == ALL_WALLS
    assert cell.hex_digit() == "F"
    for direction in Direction:
        assert cell.has_wall(direction)


def test_remove_wall_clears_only_one_bit() -> None:
    cell = Cell()
    cell.remove_wall(Direction.N)
    assert not cell.has_wall(Direction.N)
    assert cell.has_wall(Direction.E)
    assert cell.has_wall(Direction.S)
    assert cell.has_wall(Direction.W)
    assert cell.hex_digit() == "E"


def test_add_wall_is_idempotent() -> None:
    cell = Cell(walls=0)
    cell.add_wall(Direction.N)
    cell.add_wall(Direction.N)
    assert cell.walls == Direction.N


def test_opposite() -> None:
    assert opposite(Direction.N) is Direction.S
    assert opposite(Direction.S) is Direction.N
    assert opposite(Direction.E) is Direction.W
    assert opposite(Direction.W) is Direction.E


def test_delta() -> None:
    assert delta(Direction.N) == (0, -1)
    assert delta(Direction.E) == (1, 0)
    assert delta(Direction.S) == (0, 1)
    assert delta(Direction.W) == (-1, 0)


def test_subject_example_walls_value_3() -> None:
    """Subject: '3 (0011) means walls are open to the south and west'."""
    cell = Cell(walls=0b0011)
    assert cell.has_wall(Direction.N)
    assert cell.has_wall(Direction.E)
    assert not cell.has_wall(Direction.S)
    assert not cell.has_wall(Direction.W)


def test_subject_example_walls_value_A() -> None:
    """Subject: 'A (1010) means east and west walls are closed'."""
    cell = Cell(walls=0xA)
    assert not cell.has_wall(Direction.N)
    assert cell.has_wall(Direction.E)
    assert not cell.has_wall(Direction.S)
    assert cell.has_wall(Direction.W)
