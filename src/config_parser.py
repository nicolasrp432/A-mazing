"""Parser for the A-Maze-ing ``KEY=VALUE`` configuration file.

The parser is intentionally strict: any malformed line, missing key, or
out-of-range value raises a :class:`ConfigError` with a clear, user-facing
message. The rest of the program can therefore treat a :class:`Config`
instance as fully validated input.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


# Keys that MUST be present in the configuration file.
_REQUIRED_KEYS: frozenset[str] = frozenset({
    "WIDTH", "HEIGHT", "ENTRY", "EXIT", "OUTPUT_FILE", "PERFECT",
})


class ConfigError(Exception):
    """Raised when the configuration file is missing, malformed, or invalid."""


@dataclass(frozen=True)
class Config:
    """Validated, immutable representation of the configuration file.

    Attributes:
        width: Maze width in cells (> 0).
        height: Maze height in cells (> 0).
        entry: Entry cell coordinates as ``(x, y)``, inside the maze bounds.
        exit: Exit cell coordinates as ``(x, y)``, different from ``entry``.
        output_file: Path of the file where the hex maze will be written.
        perfect: If ``True``, the maze must have exactly one path entry→exit.
        seed: Optional seed for the random generator. ``None`` means
            "use a random seed each run".
    """

    width: int
    height: int
    entry: tuple[int, int]
    exit: tuple[int, int]
    output_file: str
    perfect: bool
    seed: int | None = None


def parse_config(path: str | Path) -> Config:
    """Read and validate a configuration file, returning a :class:`Config`.

    Args:
        path: Path to the configuration file.

    Returns:
        A fully validated :class:`Config` instance.

    Raises:
        ConfigError: If the file is missing, cannot be read, contains a
            malformed line, is missing a required key, or contains an
            out-of-range value.
    """
    raw = _read_pairs(Path(path))
    _check_required_keys(raw)
    return _build_config(raw)


# ---------------------------------------------------------------------------
# Internals — kept private so the public surface stays small.
# ---------------------------------------------------------------------------

def _read_pairs(path: Path) -> dict[str, str]:
    """Read the file and return the raw ``KEY=VALUE`` mapping.

    Comments (``#``) and empty lines are ignored. Whitespace around the key
    and value is stripped. A duplicate key triggers a :class:`ConfigError`
    so the user is never silently overridden.
    """
    try:
        with path.open("r", encoding="utf-8") as fp:
            lines = fp.readlines()
    except FileNotFoundError as exc:
        raise ConfigError(f"configuration file not found: {path}") from exc
    except OSError as exc:
        raise ConfigError(f"cannot read {path}: {exc}") from exc

    pairs: dict[str, str] = {}
    for line_number, raw_line in enumerate(lines, start=1):
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            raise ConfigError(
                f"line {line_number}: expected 'KEY=VALUE', got {raw_line!r}"
            )
        key, _, value = line.partition("=")
        key, value = key.strip(), value.strip()
        if not key:
            raise ConfigError(f"line {line_number}: empty key")
        if key in pairs:
            raise ConfigError(f"line {line_number}: duplicated key {key!r}")
        pairs[key] = value
    return pairs


def _check_required_keys(pairs: dict[str, str]) -> None:
    """Make sure every mandatory key is present."""
    missing = _REQUIRED_KEYS - pairs.keys()
    if missing:
        joined = ", ".join(sorted(missing))
        raise ConfigError(f"missing required key(s): {joined}")


def _build_config(pairs: dict[str, str]) -> Config:
    """Convert raw string values into the typed :class:`Config` object."""
    width = _parse_positive_int(pairs["WIDTH"], "WIDTH")
    height = _parse_positive_int(pairs["HEIGHT"], "HEIGHT")
    entry = _parse_coords(pairs["ENTRY"], "ENTRY", width, height)
    exit_ = _parse_coords(pairs["EXIT"], "EXIT", width, height)
    if entry == exit_:
        raise ConfigError("ENTRY and EXIT must be different cells")

    output_file = pairs["OUTPUT_FILE"]
    if not output_file:
        raise ConfigError("OUTPUT_FILE must not be empty")

    perfect = _parse_bool(pairs["PERFECT"], "PERFECT")

    seed: int | None = None
    if "SEED" in pairs:
        seed = _parse_int(pairs["SEED"], "SEED")

    return Config(
        width=width,
        height=height,
        entry=entry,
        exit=exit_,
        output_file=output_file,
        perfect=perfect,
        seed=seed,
    )


def _parse_int(value: str, key: str) -> int:
    try:
        return int(value)
    except ValueError as exc:
        raise ConfigError(
            f"{key}: expected an integer, got {value!r}"
        ) from exc


def _parse_positive_int(value: str, key: str) -> int:
    parsed = _parse_int(value, key)
    if parsed <= 0:
        raise ConfigError(f"{key}: must be strictly positive (got {parsed})")
    return parsed


def _parse_bool(value: str, key: str) -> bool:
    lowered = value.lower()
    if lowered == "true":
        return True
    if lowered == "false":
        return False
    raise ConfigError(f"{key}: expected 'True' or 'False', got {value!r}")


def _parse_coords(
    value: str, key: str, width: int, height: int,
) -> tuple[int, int]:
    """Parse ``"x,y"`` and check it falls inside the maze bounds."""
    parts = value.split(",")
    if len(parts) != 2:
        raise ConfigError(
            f"{key}: expected 'x,y', got {value!r}"
        )
    try:
        x, y = int(parts[0]), int(parts[1])
    except ValueError as exc:
        raise ConfigError(
            f"{key}: coordinates must be integers, got {value!r}"
        ) from exc
    if not (0 <= x < width and 0 <= y < height):
        raise ConfigError(
            f"{key}: ({x},{y}) is outside the maze "
            f"(width={width}, height={height})"
        )
    return (x, y)
