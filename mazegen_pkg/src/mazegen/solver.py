"""Shortest-path solver for a generated maze.

The solver implements a plain **breadth-first search**. On a maze viewed
as an unweighted graph (every step between two adjacent cells costs 1),
BFS is guaranteed to return the shortest path — the very first time it
reaches the target.
"""

from __future__ import annotations

from collections import deque

from .cell import Cell, Direction, delta


# Iteration order matters for determinism, not for correctness.
_DIRECTIONS: tuple[Direction, ...] = (
    Direction.N, Direction.E, Direction.S, Direction.W,
)


class PathNotFoundError(Exception):
    """Raised when no path exists between two cells."""


def shortest_path(
    grid: list[list[Cell]],
    start: tuple[int, int],
    end: tuple[int, int],
) -> list[tuple[int, int]]:
    """Return the shortest list of ``(x, y)`` cells from ``start`` to ``end``.

    Args:
        grid: 2D list of :class:`Cell`, indexed as ``grid[y][x]``.
        start: Starting cell coordinates.
        end: Target cell coordinates.

    Returns:
        A list beginning with ``start`` and ending with ``end``. Adjacent
        elements differ by exactly one cell.

    Raises:
        PathNotFoundError: If ``end`` is not reachable from ``start``.
    """
    if start == end:
        return [start]

    height = len(grid)
    width = len(grid[0]) if grid else 0

    queue: deque[tuple[int, int]] = deque([start])
    parent: dict[tuple[int, int], tuple[int, int]] = {start: start}

    while queue:
        x, y = queue.popleft()
        if (x, y) == end:
            return _rebuild_path(parent, end)
        for direction in _DIRECTIONS:
            if grid[y][x].has_wall(direction):
                continue
            dx, dy = delta(direction)
            nx, ny = x + dx, y + dy
            if not (0 <= nx < width and 0 <= ny < height):
                continue
            if (nx, ny) in parent:
                continue
            parent[(nx, ny)] = (x, y)
            queue.append((nx, ny))

    raise PathNotFoundError(f"no path from {start} to {end}")


def path_to_directions(path: list[tuple[int, int]]) -> str:
    """Convert a path of cells into a string of ``N``/``E``/``S``/``W`` moves.

    Args:
        path: A list of consecutive cells (see :func:`shortest_path`).

    Returns:
        One character per move. An empty string if the path has fewer than
        two cells.
    """
    if len(path) < 2:
        return ""
    letters: list[str] = []
    for (x1, y1), (x2, y2) in zip(path, path[1:]):
        dx, dy = x2 - x1, y2 - y1
        letters.append(_STEP_TO_LETTER[(dx, dy)])
    return "".join(letters)


_STEP_TO_LETTER: dict[tuple[int, int], str] = {
    (0, -1): "N",
    (1, 0): "E",
    (0, 1): "S",
    (-1, 0): "W",
}


def _rebuild_path(
    parent: dict[tuple[int, int], tuple[int, int]],
    end: tuple[int, int],
) -> list[tuple[int, int]]:
    """Walk back through ``parent`` to recover the path in start→end order."""
    path: list[tuple[int, int]] = [end]
    while parent[path[-1]] != path[-1]:
        path.append(parent[path[-1]])
    path.reverse()
    return path
