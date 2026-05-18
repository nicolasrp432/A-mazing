"""Terminal rendering of a maze using ANSI colours.

Every cell is expanded into a 2x2 block of "pixels", plus one extra row
and column for the outer borders. Each pixel is rendered as two character
columns so the result keeps a roughly square aspect ratio in a typical
terminal font.

The renderer is purely functional: it receives a ``MazeGenerator`` plus
display options and returns the rendered string. No I/O is performed
here.
"""

from __future__ import annotations

from dataclasses import dataclass

from mazegen import MazeGenerator
from mazegen.cell import Direction


ANSI_RESET = "\x1b[0m"


@dataclass(frozen=True)
class ColorScheme:
    """ANSI escape sequences for the different cell categories.

    Each field is the full prefix to emit *before* the block; the suffix
    is always :data:`ANSI_RESET`.
    """

    name: str
    wall: str
    floor: str
    pattern: str
    entry: str
    exit: str
    path: str


# Pre-defined schemes the user can cycle through with menu option 3.
COLOR_SCHEMES: tuple[ColorScheme, ...] = (
    ColorScheme(
        name="classic",
        wall="\x1b[47m",      # white background
        floor="\x1b[40m",     # black background
        pattern="\x1b[100m",  # bright black (grey)
        entry="\x1b[45m",     # magenta
        exit="\x1b[41m",      # red
        path="\x1b[46m",      # cyan
    ),
    ColorScheme(
        name="forest",
        wall="\x1b[42m",      # green
        floor="\x1b[40m",
        pattern="\x1b[43m",   # yellow
        entry="\x1b[45m",
        exit="\x1b[41m",
        path="\x1b[44m",      # blue
    ),
    ColorScheme(
        name="amber",
        wall="\x1b[43m",      # yellow
        floor="\x1b[40m",
        pattern="\x1b[100m",
        entry="\x1b[45m",
        exit="\x1b[41m",
        path="\x1b[46m",
    ),
    ColorScheme(
        name="ocean",
        wall="\x1b[44m",      # blue
        floor="\x1b[40m",
        pattern="\x1b[46m",   # cyan
        entry="\x1b[45m",
        exit="\x1b[41m",
        path="\x1b[47m",      # white
    ),
)


# Width of one "pixel" in character columns. Two columns keep the
# rendered maze visually square in most terminals.
_PIXEL = "  "


def render(
    maze: MazeGenerator,
    entry: tuple[int, int],
    exit_: tuple[int, int],
    *,
    show_path: bool = False,
    scheme: ColorScheme = COLOR_SCHEMES[0],
) -> str:
    """Return the maze as a multi-line, ANSI-coloured string."""
    pixels = _build_pixel_grid(maze, entry, exit_, show_path)
    palette: dict[str, str] = {
        "wall": scheme.wall,
        "floor": scheme.floor,
        "pattern": scheme.pattern,
        "entry": scheme.entry,
        "exit": scheme.exit,
        "path": scheme.path,
    }
    return "\n".join(
        "".join(palette[kind] + _PIXEL + ANSI_RESET for kind in row)
        for row in pixels
    )


def _build_pixel_grid(
    maze: MazeGenerator,
    entry: tuple[int, int],
    exit_: tuple[int, int],
    show_path: bool,
) -> list[list[str]]:
    """Compute the 2D grid of pixel categories ready to be coloured."""
    h, w = maze.height, maze.width
    rows = 2 * h + 1
    cols = 2 * w + 1
    grid: list[list[str]] = [["wall"] * cols for _ in range(rows)]

    for y in range(h):
        for x in range(w):
            cell = maze.grid[y][x]
            cy, cx = 2 * y + 1, 2 * x + 1
            if (x, y) in maze.pattern_cells:
                grid[cy][cx] = "pattern"
            else:
                grid[cy][cx] = "floor"
            if not cell.has_wall(Direction.N):
                grid[cy - 1][cx] = "floor"
            if not cell.has_wall(Direction.W):
                grid[cy][cx - 1] = "floor"
            if not cell.has_wall(Direction.S):
                grid[cy + 1][cx] = "floor"
            if not cell.has_wall(Direction.E):
                grid[cy][cx + 1] = "floor"

    if show_path:
        path = maze.shortest_path(entry, exit_)
        for x, y in path:
            grid[2 * y + 1][2 * x + 1] = "path"

    # Entry & exit always take precedence over path so they remain visible.
    ex, ey = entry
    grid[2 * ey + 1][2 * ex + 1] = "entry"
    xx, xy = exit_
    grid[2 * xy + 1][2 * xx + 1] = "exit"

    return grid
