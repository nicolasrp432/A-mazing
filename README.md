*This project has been created as part of the 42 curriculum by <!-- TODO: login1, login2, login3 -->.*

# A-Maze-ing

> Create your own maze generator and display its result!

## Description

A-Maze-ing is a Python maze generator. It reads a configuration file, builds a
maze (optionally a *perfect* one, i.e. with a single path between entry and
exit), writes it to disk in a compact hexadecimal format, and renders it
interactively in the terminal. The maze always contains a visible **"42"**
pattern drawn with closed cells.

The maze-generation logic is isolated in a standalone, pip-installable module
(`mazegen`) so it can be reused in other projects.

## Instructions

```bash
# 1. Set up the development environment
make install

# 2. Run the program with the default configuration
make run

# 3. Or run it directly
python3 a_maze_ing.py config.txt
```

Lint and tests:

```bash
make lint        # flake8 + mypy with subject-required flags
make lint-strict # flake8 + mypy --strict
make test        # pytest test suite
```

## Configuration file format

The configuration file uses one `KEY=VALUE` pair per line. Lines starting with
`#` are comments and are ignored.

| Key           | Type          | Description                                  | Mandatory |
|---------------|---------------|----------------------------------------------|-----------|
| `WIDTH`       | int (> 0)     | Maze width (number of cells)                 | yes       |
| `HEIGHT`      | int (> 0)     | Maze height (number of cells)                | yes       |
| `ENTRY`       | `x,y`         | Entry cell coordinates (0-indexed)           | yes       |
| `EXIT`        | `x,y`         | Exit cell coordinates (0-indexed)            | yes       |
| `OUTPUT_FILE` | path          | File where the hex maze will be written      | yes       |
| `PERFECT`     | `True`/`False`| If `True`, exactly one path entry→exit       | yes       |
| `SEED`        | int           | Optional. Seed for reproducibility           | no        |

A working `config.txt` is provided at the repository root.

## Algorithm

We chose the **Recursive Backtracker** algorithm (also known as randomized
depth-first search). It is implemented **iteratively** with an explicit stack
to avoid Python's recursion limit on large mazes.

Why this algorithm:

- It naturally produces **perfect mazes** (no cycles) — exactly what `PERFECT=True` requires.
- It is easy to reason about and to defend in a peer review: one stack, one
  visited set, random neighbour selection.
- It produces long, winding corridors that feel like classic mazes.

If `PERFECT=False`, additional walls are removed at random *after* generation,
while guaranteeing no `3x3` fully-open area appears (corridors stay at most 2
cells wide, as required by the subject).

The shortest path from entry to exit is computed with **BFS**, which is
optimal on an unweighted graph.

## Reusable module — `mazegen`

The maze-generation core is shipped as a separate, pip-installable package
called `mazegen`. The built wheel (`mazegen-1.0.0-py3-none-any.whl`) is
located at the root of the repository.

Minimal example:

```python
from mazegen import MazeGenerator

gen = MazeGenerator(width=20, height=15, seed=42, perfect=True)
gen.generate()

print(gen.grid)              # 2D list of Cell objects
print(gen.shortest_path())   # list[tuple[int, int]]
```

See `mazegen_pkg/README.md` for the full module documentation.

## Resources

Classic references on maze generation:

- Jamis Buck — *Mazes for Programmers* (Pragmatic Bookshelf, 2015)
- [Wikipedia: Maze generation algorithm](https://en.wikipedia.org/wiki/Maze_generation_algorithm)
- [Think Labyrinth!](http://www.astrolog.org/labyrnth/algrithm.htm) by Walter Pullen

### AI usage

<!-- TODO: describe honestly which tasks used AI assistance and how the
output was reviewed. Be specific (e.g. "used AI to draft docstrings, then
rewrote every signature manually after reading PEP 257"). -->

## Team and project management

<!-- TODO -->

### Roles

<!-- TODO: one bullet per team member -->

### Planning

<!-- TODO: anticipated planning and how it evolved -->

### What worked well / what could be improved

<!-- TODO -->

### Tools used

<!-- TODO: editor, linters, version control workflow, etc. -->
