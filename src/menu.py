"""Interactive terminal menu loop for the maze generator.

The loop renders the maze, then prompts the user for one of the four
actions required by the subject:

    1. Re-generate a new maze and display it.
    2. Show/Hide the shortest path from entry to exit.
    3. Rotate maze colours.
    4. Quit.

Every action that changes the maze structure also rewrites the configured
output file, so the on-disk hexadecimal representation stays in sync
with what is being displayed.
"""

from __future__ import annotations

import random

from mazegen import MazeGenerator

from .config_parser import Config
from .display import COLOR_SCHEMES, render
from .output_writer import write_maze


# ANSI sequence: clear screen + move cursor to top-left.
_CLEAR_SCREEN = "\x1b[2J\x1b[H"


class MenuSession:
    """Mutable state of the interactive session."""

    def __init__(self, config: Config, generator: MazeGenerator) -> None:
        self.config = config
        self.generator = generator
        self.show_path: bool = False
        self.color_index: int = 0

    @property
    def scheme(self) -> object:
        return COLOR_SCHEMES[self.color_index]


def run(config: Config, generator: MazeGenerator) -> None:
    """Run the interactive menu loop until the user chooses to quit."""
    session = MenuSession(config, generator)
    while True:
        _draw(session)
        try:
            choice = input("Choice? (1-4): ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            return

        if choice == "1":
            _regenerate(session)
        elif choice == "2":
            session.show_path = not session.show_path
        elif choice == "3":
            n_schemes = len(COLOR_SCHEMES)
            session.color_index = (session.color_index + 1) % n_schemes
        elif choice == "4":
            return
        else:
            input(f"Unknown choice {choice!r}. Press Enter to continue.")


def _draw(session: MenuSession) -> None:
    """Clear the screen and render the maze with the current options."""
    print(_CLEAR_SCREEN, end="")
    print(render(
        session.generator,
        entry=session.config.entry,
        exit_=session.config.exit,
        show_path=session.show_path,
        scheme=COLOR_SCHEMES[session.color_index],
    ))
    print()
    print("=== A-Maze-ing ===")
    print("1. Re-generate a new maze")
    print("2. Show/Hide path from entry to exit"
          f" (currently: {'ON' if session.show_path else 'OFF'})")
    current_scheme = COLOR_SCHEMES[session.color_index].name
    print(f"3. Rotate maze colors (current: {current_scheme})")
    print("4. Quit")


def _regenerate(session: MenuSession) -> None:
    """Build a new maze with a fresh random seed and persist it."""
    new_seed = random.randint(0, 2**31 - 1)
    session.generator = MazeGenerator(
        width=session.config.width,
        height=session.config.height,
        seed=new_seed,
        perfect=session.config.perfect,
    )
    session.generator.generate()
    write_maze(
        session.config.output_file,
        session.generator.grid,
        session.config.entry,
        session.config.exit,
    )
