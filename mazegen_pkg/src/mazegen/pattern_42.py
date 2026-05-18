"""The "42" pixel-art pattern injected into the maze.

The pattern is a small bitmap of fully-closed cells that visually spell out
"42" inside the maze. The bitmap is centred on the grid; the surrounding
cells are carved normally by the Recursive Backtracker so the maze still
flows around the digits.

Bitmap layout: ``X`` marks a closed cell, ``.`` marks a normal (carve-able)
cell. The character pair ``4`` (4 cells wide) + 1-cell gap + ``2`` (4 cells
wide) yields a 9x6 figure that fits comfortably inside a 20x15 maze.
"""

from __future__ import annotations


# 9 columns wide, 6 rows tall.
PATTERN_42: tuple[str, ...] = (
    "X..X.XXXX",
    "X..X....X",
    "X..X....X",
    "XXXX...X.",
    "...X..X..",
    "...X.XXXX",
)

PATTERN_WIDTH: int = len(PATTERN_42[0])
PATTERN_HEIGHT: int = len(PATTERN_42)

# Minimum margin we want around the pattern so the maze can flow around it.
_MIN_MARGIN: int = 2


def fits(maze_width: int, maze_height: int) -> bool:
    """Return ``True`` if the maze is large enough to host the pattern."""
    return (
        maze_width >= PATTERN_WIDTH + 2 * _MIN_MARGIN
        and maze_height >= PATTERN_HEIGHT + 2 * _MIN_MARGIN
    )


def pattern_cells(maze_width: int, maze_height: int) -> set[tuple[int, int]]:
    """Return the set of ``(x, y)`` cells covered by the centred pattern.

    The pattern is centred on the grid. If it does not fit
    (see :func:`fits`), an empty set is returned and the caller should
    handle the situation (the subject requires printing an error message
    in that case).
    """
    if not fits(maze_width, maze_height):
        return set()

    offset_x = (maze_width - PATTERN_WIDTH) // 2
    offset_y = (maze_height - PATTERN_HEIGHT) // 2

    cells: set[tuple[int, int]] = set()
    for row_index, row in enumerate(PATTERN_42):
        for col_index, char in enumerate(row):
            if char == "X":
                cells.add((offset_x + col_index, offset_y + row_index))
    return cells
