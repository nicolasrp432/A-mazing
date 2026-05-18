"""Maze generator implementing the iterative *Recursive Backtracker*.

The algorithm is a randomised depth-first search:

1. Initialise the grid with every cell carrying its four walls.
2. Push a starting cell onto a stack and mark it visited.
3. While the stack is not empty:
       * Peek at the top of the stack.
       * Collect its unvisited neighbours.
       * If at least one exists, pick one at random, knock down the wall
         between the two cells, mark the neighbour visited, push it.
       * Otherwise, pop (backtrack).

Because every cell is added exactly once and we knock exactly one wall per
addition, the resulting graph is a spanning tree of the grid — i.e. a
*perfect* maze with one and only one path between any two cells.

The "42" pattern (subject's mandatory feature) is implemented by
pre-marking the pattern cells as *visited*. The DFS therefore never enters
them and never removes any of their walls, so they remain fully closed
and visually spell out "42" in the rendered maze.
"""

from __future__ import annotations

import random
import sys
from typing import Iterator

from . import pattern_42
from .cell import Cell, Direction, delta, opposite
from .solver import shortest_path


# Public, ordered tuple of directions used wherever iteration matters.
DIRECTIONS: tuple[Direction, ...] = (
    Direction.N, Direction.E, Direction.S, Direction.W,
)


class MazeGenerator:
    """Generate a maze using the iterative Recursive Backtracker.

    Args:
        width: Number of cells horizontally (must be > 0).
        height: Number of cells vertically (must be > 0).
        seed: Optional seed for reproducibility. ``None`` => fresh randomness.
        perfect: If ``True``, generation stops at the spanning tree
            (single path between any two cells). If ``False``, additional
            walls will be removed in a later step to create loops.
        with_pattern: If ``True`` (the default), the "42" pattern is added.
            If the maze is too small to host it, the pattern is silently
            skipped after printing an error message on ``stderr``.

    Attributes:
        grid: 2D list of :class:`Cell`, indexed as ``grid[y][x]``.
        pattern_cells: ``(x, y)`` coordinates of the "42" pattern cells.
            Empty if the pattern could not be placed.
    """

    def __init__(
        self,
        width: int,
        height: int,
        seed: int | None = None,
        perfect: bool = True,
        with_pattern: bool = True,
    ) -> None:
        if width <= 0 or height <= 0:
            raise ValueError("width and height must be strictly positive")
        self.width = width
        self.height = height
        self.seed = seed
        self.perfect = perfect
        self.with_pattern = with_pattern
        self._rng = random.Random(seed)
        self.grid: list[list[Cell]] = self._fresh_grid()
        self.pattern_cells: set[tuple[int, int]] = set()

    # -- Public API ----------------------------------------------------------

    def generate(self) -> None:
        """Run the full generation pipeline in-place on ``self.grid``."""
        self.grid = self._fresh_grid()
        self.pattern_cells = self._compute_pattern()
        start = self._first_non_pattern_cell()
        self._carve_passages(start=start, blocked=self.pattern_cells)
        if not self.perfect:
            self._add_loops(fraction=0.15)

    def in_bounds(self, x: int, y: int) -> bool:
        """Return ``True`` if ``(x, y)`` is a valid cell coordinate."""
        return 0 <= x < self.width and 0 <= y < self.height

    def iter_cells(self) -> Iterator[tuple[int, int, Cell]]:
        """Yield ``(x, y, cell)`` for every cell, row by row."""
        for y, row in enumerate(self.grid):
            for x, cell in enumerate(row):
                yield x, y, cell

    def shortest_path(
        self, start: tuple[int, int], end: tuple[int, int],
    ) -> list[tuple[int, int]]:
        """Convenience wrapper around :func:`mazegen.solver.shortest_path`."""
        return shortest_path(self.grid, start, end)

    # -- Internals -----------------------------------------------------------

    def _fresh_grid(self) -> list[list[Cell]]:
        """Return a brand-new grid where every cell has its four walls."""
        return [
            [Cell() for _ in range(self.width)]
            for _ in range(self.height)
        ]

    def _compute_pattern(self) -> set[tuple[int, int]]:
        """Return the centred "42" pattern, or empty if disabled/too small."""
        if not self.with_pattern:
            return set()
        if not pattern_42.fits(self.width, self.height):
            print(
                f"warning: maze is too small ({self.width}x{self.height}) "
                f"to display the '42' pattern; skipping it.",
                file=sys.stderr,
            )
            return set()
        return pattern_42.pattern_cells(self.width, self.height)

    def _first_non_pattern_cell(self) -> tuple[int, int]:
        """Return the top-left-most cell that is not part of the pattern."""
        for y in range(self.height):
            for x in range(self.width):
                if (x, y) not in self.pattern_cells:
                    return (x, y)
        # This is unreachable: the pattern never fills the entire grid.
        raise RuntimeError("no cell available to start carving")

    def _carve_passages(
        self,
        start: tuple[int, int],
        blocked: set[tuple[int, int]],
    ) -> None:
        """Iterative Recursive Backtracker starting from ``start``.

        ``blocked`` is the set of cells the DFS must not enter; they are
        seeded into ``visited`` so neighbours never select them.
        """
        visited: set[tuple[int, int]] = set(blocked)
        visited.add(start)
        stack: list[tuple[int, int]] = [start]

        while stack:
            x, y = stack[-1]
            neighbours = self._unvisited_neighbours(x, y, visited)

            if not neighbours:
                stack.pop()
                continue

            direction, nx, ny = self._rng.choice(neighbours)
            self._open_passage(x, y, direction)
            visited.add((nx, ny))
            stack.append((nx, ny))

    def _unvisited_neighbours(
        self, x: int, y: int, visited: set[tuple[int, int]],
    ) -> list[tuple[Direction, int, int]]:
        """Return every in-bounds, not-yet-visited neighbour of ``(x, y)``."""
        result: list[tuple[Direction, int, int]] = []
        for direction in DIRECTIONS:
            dx, dy = delta(direction)
            nx, ny = x + dx, y + dy
            if self.in_bounds(nx, ny) and (nx, ny) not in visited:
                result.append((direction, nx, ny))
        return result

    def _open_passage(self, x: int, y: int, direction: Direction) -> None:
        """Knock down the wall between ``(x, y)`` and its neighbour."""
        dx, dy = delta(direction)
        nx, ny = x + dx, y + dy
        self.grid[y][x].remove_wall(direction)
        self.grid[ny][nx].remove_wall(opposite(direction))

    def _close_passage(self, x: int, y: int, direction: Direction) -> None:
        """Restore the wall between ``(x, y)`` and its neighbour."""
        dx, dy = delta(direction)
        nx, ny = x + dx, y + dy
        self.grid[y][x].add_wall(direction)
        self.grid[ny][nx].add_wall(opposite(direction))

    # -- Non-perfect-mode helpers --------------------------------------------

    def _add_loops(self, fraction: float) -> None:
        """Remove extra walls to create loops, keeping corridors ≤ 2 cells.

        ``fraction`` is the share of currently-closed interior walls we
        attempt to remove. Pattern walls and walls bordering pattern cells
        are never touched, so the "42" stays visible.
        """
        candidates = self._loop_candidates()
        self._rng.shuffle(candidates)
        budget = int(len(candidates) * fraction)
        removed = 0
        for x, y, direction in candidates:
            if removed >= budget:
                break
            self._open_passage(x, y, direction)
            if self._creates_open_3x3(x, y, direction):
                self._close_passage(x, y, direction)
            else:
                removed += 1

    def _loop_candidates(self) -> list[tuple[int, int, Direction]]:
        """List every interior wall eligible to be removed."""
        result: list[tuple[int, int, Direction]] = []
        for y in range(self.height):
            for x in range(self.width):
                if (x, y) in self.pattern_cells:
                    continue
                # East wall — share with neighbour at (x+1, y).
                if x + 1 < self.width \
                        and (x + 1, y) not in self.pattern_cells \
                        and self.grid[y][x].has_wall(Direction.E):
                    result.append((x, y, Direction.E))
                # South wall — share with neighbour at (x, y+1).
                if y + 1 < self.height \
                        and (x, y + 1) not in self.pattern_cells \
                        and self.grid[y][x].has_wall(Direction.S):
                    result.append((x, y, Direction.S))
        return result

    def _creates_open_3x3(
        self, x: int, y: int, direction: Direction,
    ) -> bool:
        """``True`` if any 3x3 window touching the wall would be all open."""
        dx, dy = delta(direction)
        nx, ny = x + dx, y + dy
        for cx, cy in ((x, y), (nx, ny)):
            for ox in range(max(0, cx - 2), min(self.width - 2, cx) + 1):
                for oy in range(max(0, cy - 2), min(self.height - 2, cy) + 1):
                    if self._is_open_3x3(ox, oy):
                        return True
        return False

    def _is_open_3x3(self, ox: int, oy: int) -> bool:
        """Are all 12 interior walls of the 3x3 block at ``(ox, oy)`` open?"""
        for j in range(3):
            for i in range(3):
                cell = self.grid[oy + j][ox + i]
                if i < 2 and cell.has_wall(Direction.E):
                    return False
                if j < 2 and cell.has_wall(Direction.S):
                    return False
        return True
