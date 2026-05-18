"""Write a generated maze to disk in the subject's exact output format.

The output file contains:

1. ``HEIGHT`` lines of ``WIDTH`` hexadecimal digits — one digit per cell.
   Each digit encodes the four walls of the cell (bit 0=N, 1=E, 2=S, 3=W;
   ``1`` means *closed*).
2. An empty line.
3. The entry coordinates as ``x,y``.
4. The exit coordinates as ``x,y``.
5. The shortest path from entry to exit, written as a sequence of the
   letters ``N``, ``E``, ``S``, ``W``.

Every line — including the empty separator — ends with ``\\n``.
"""

from __future__ import annotations

from pathlib import Path

from mazegen import path_to_directions, shortest_path
from mazegen.cell import Cell


class OutputError(Exception):
    """Raised when the output file cannot be written."""


def write_maze(
    output_path: str | Path,
    grid: list[list[Cell]],
    entry: tuple[int, int],
    exit_: tuple[int, int],
) -> str:
    """Render ``grid`` and write it to ``output_path``.

    Args:
        output_path: Destination file path. Existing files are overwritten.
        grid: 2D list of :class:`Cell`, indexed ``grid[y][x]``.
        entry: Entry coordinates as ``(x, y)``.
        exit_: Exit coordinates as ``(x, y)``.

    Returns:
        The full text that was written, useful for debugging or for the
        caller to print it.

    Raises:
        OutputError: If the file cannot be opened or written.
    """
    path_cells = shortest_path(grid, entry, exit_)
    directions = path_to_directions(path_cells)

    rows = ["".join(cell.hex_digit() for cell in row) for row in grid]
    body = "\n".join([
        *rows,
        "",
        f"{entry[0]},{entry[1]}",
        f"{exit_[0]},{exit_[1]}",
        directions,
    ]) + "\n"

    try:
        with open(output_path, "w", encoding="utf-8") as fp:
            fp.write(body)
    except OSError as exc:
        raise OutputError(f"cannot write {output_path}: {exc}") from exc

    return body
