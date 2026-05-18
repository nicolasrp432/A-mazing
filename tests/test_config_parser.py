"""Unit tests for :mod:`src.config_parser`."""

from __future__ import annotations

from pathlib import Path

import pytest

from src.config_parser import Config, ConfigError, parse_config


def _write(tmp_path: Path, body: str) -> Path:
    cfg = tmp_path / "config.txt"
    cfg.write_text(body, encoding="utf-8")
    return cfg


def test_parses_valid_config(tmp_path: Path) -> None:
    cfg = _write(tmp_path, (
        "WIDTH=20\n"
        "HEIGHT=15\n"
        "ENTRY=0,0\n"
        "EXIT=19,14\n"
        "OUTPUT_FILE=maze.txt\n"
        "PERFECT=True\n"
        "SEED=42\n"
    ))
    config = parse_config(cfg)
    assert config == Config(
        width=20, height=15,
        entry=(0, 0), exit=(19, 14),
        output_file="maze.txt",
        perfect=True, seed=42,
    )


def test_comments_and_blank_lines_are_ignored(tmp_path: Path) -> None:
    cfg = _write(tmp_path, (
        "# this is a comment\n"
        "\n"
        "WIDTH=10\n"
        "   # indented comment\n"
        "HEIGHT=10\n"
        "ENTRY=0,0\n"
        "EXIT=9,9\n"
        "OUTPUT_FILE=out.txt\n"
        "PERFECT=False\n"
    ))
    config = parse_config(cfg)
    assert config.width == 10 and config.height == 10
    assert config.perfect is False
    assert config.seed is None


def test_missing_file_raises(tmp_path: Path) -> None:
    with pytest.raises(ConfigError, match="not found"):
        parse_config(tmp_path / "does_not_exist.txt")


def test_missing_required_key(tmp_path: Path) -> None:
    cfg = _write(tmp_path, "WIDTH=10\nHEIGHT=10\nENTRY=0,0\nEXIT=1,1\n")
    with pytest.raises(ConfigError, match="missing required key"):
        parse_config(cfg)


def test_malformed_line(tmp_path: Path) -> None:
    cfg = _write(tmp_path, "WIDTH 10\n")
    with pytest.raises(ConfigError, match="KEY=VALUE"):
        parse_config(cfg)


def test_duplicated_key(tmp_path: Path) -> None:
    cfg = _write(tmp_path, "WIDTH=10\nWIDTH=20\n")
    with pytest.raises(ConfigError, match="duplicated"):
        parse_config(cfg)


def test_non_positive_dimension(tmp_path: Path) -> None:
    cfg = _write(tmp_path, (
        "WIDTH=0\nHEIGHT=10\nENTRY=0,0\nEXIT=1,1\n"
        "OUTPUT_FILE=out.txt\nPERFECT=True\n"
    ))
    with pytest.raises(ConfigError, match="strictly positive"):
        parse_config(cfg)


def test_entry_equals_exit(tmp_path: Path) -> None:
    cfg = _write(tmp_path, (
        "WIDTH=10\nHEIGHT=10\nENTRY=3,3\nEXIT=3,3\n"
        "OUTPUT_FILE=out.txt\nPERFECT=True\n"
    ))
    with pytest.raises(ConfigError, match="different"):
        parse_config(cfg)


def test_coords_out_of_bounds(tmp_path: Path) -> None:
    cfg = _write(tmp_path, (
        "WIDTH=10\nHEIGHT=10\nENTRY=0,0\nEXIT=10,0\n"
        "OUTPUT_FILE=out.txt\nPERFECT=True\n"
    ))
    with pytest.raises(ConfigError, match="outside the maze"):
        parse_config(cfg)


def test_invalid_bool(tmp_path: Path) -> None:
    cfg = _write(tmp_path, (
        "WIDTH=10\nHEIGHT=10\nENTRY=0,0\nEXIT=1,1\n"
        "OUTPUT_FILE=out.txt\nPERFECT=yes\n"
    ))
    with pytest.raises(ConfigError, match="True"):
        parse_config(cfg)
