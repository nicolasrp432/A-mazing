#!/usr/bin/env python3
"""A-Maze-ing — entry point.

Usage:

    python3 a_maze_ing.py config.txt

The script reads ``config.txt``, generates the corresponding maze, writes
its hexadecimal representation to the configured output file, and finally
opens an interactive terminal menu that lets the user regenerate the
maze, toggle the shortest-path overlay, or rotate the colour scheme.

All errors are caught and reported as a single one-line message on
``stderr``; the program never raises an unhandled exception during a
normal run.
"""

from __future__ import annotations

import sys
from pathlib import Path


# --- Make the local mazegen package importable without prior installation.
_REPO_ROOT = Path(__file__).resolve().parent
_LOCAL_PKG = _REPO_ROOT / "mazegen_pkg" / "src"
if _LOCAL_PKG.is_dir() and str(_LOCAL_PKG) not in sys.path:
    sys.path.insert(0, str(_LOCAL_PKG))


from mazegen import MazeGenerator  # noqa: E402

from src import menu  # noqa: E402
from src.config_parser import Config, ConfigError, parse_config  # noqa: E402
from src.output_writer import OutputError, write_maze  # noqa: E402


def main(argv: list[str]) -> int:
    """Program entry point. Return a Unix-style exit code."""
    if len(argv) != 2:
        print(f"usage: {argv[0]} <config.txt>", file=sys.stderr)
        return 2

    try:
        config = parse_config(argv[1])
        generator = _build_generator(config)
        generator.generate()
        write_maze(
            config.output_file,
            generator.grid,
            config.entry,
            config.exit,
        )
        menu.run(config, generator)
    except ConfigError as exc:
        print(f"configuration error: {exc}", file=sys.stderr)
        return 1
    except OutputError as exc:
        print(f"output error: {exc}", file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        print()  # newline so the shell prompt is on its own line
        return 130  # conventional "interrupted" exit code
    return 0


def _build_generator(config: Config) -> MazeGenerator:
    """Instantiate ``MazeGenerator`` from a validated :class:`Config`."""
    return MazeGenerator(
        width=config.width,
        height=config.height,
        seed=config.seed,
        perfect=config.perfect,
    )


if __name__ == "__main__":
    sys.exit(main(sys.argv))
