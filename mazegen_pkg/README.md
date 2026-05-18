# mazegen

Reusable maze generator built around an iterative
**Recursive Backtracker** (randomised depth-first search). The package
also provides a BFS shortest-path solver and a small set of helpers to
manipulate cells and walls.

## Installation

```bash
pip install mazegen-1.0.0-py3-none-any.whl
```

Or, from a checkout of this repository:

```bash
cd mazegen_pkg
pip install .
```

## Quick start

```python
from mazegen import MazeGenerator

# Default: a perfect maze with the "42" pattern visible inside.
gen = MazeGenerator(width=20, height=15, seed=42, perfect=True)
gen.generate()

# Print the hexadecimal representation, one cell per character.
for row in gen.grid:
    print("".join(cell.hex_digit() for cell in row))

# Solve it: shortest path from entry to exit.
path = gen.shortest_path(start=(0, 0), end=(19, 14))
```

## Custom parameters

| Parameter      | Type            | Description                                          |
|----------------|-----------------|------------------------------------------------------|
| `width`        | `int`           | Number of cells horizontally (> 0).                  |
| `height`       | `int`           | Number of cells vertically (> 0).                    |
| `seed`         | `int \| None`   | Reproducibility seed. ``None`` => random.            |
| `perfect`      | `bool`          | If ``True``, exactly one path between any 2 cells.   |
| `with_pattern` | `bool`          | If ``True`` (default), inject the "42" pattern.      |

## Accessing the generated structure

* `gen.grid` — 2D list (`grid[y][x]`) of [`Cell`](src/mazegen/cell.py)
  instances. Each cell exposes:
    * `walls` — bit-mask of currently closed walls (bit 0=N, 1=E, 2=S, 3=W).
    * `has_wall(direction)`, `remove_wall(direction)`, `add_wall(direction)`
    * `hex_digit()` — the cell as one uppercase hexadecimal digit.
* `gen.pattern_cells` — the set of `(x, y)` cells forming the "42"
  pattern. Empty if the maze is too small (a warning is printed).
* `gen.shortest_path(start, end)` — BFS solution as a list of cells.
* `mazegen.path_to_directions(path)` — convert a path to a ``N``/``E``/
  ``S``/``W`` string.

## Building from source

```bash
cd mazegen_pkg
python -m build         # produces dist/mazegen-1.0.0.tar.gz and .whl
```

## License

MIT.
