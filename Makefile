# =============================================================================
# A-Maze-ing — Makefile
# =============================================================================
# Targets required by the subject:
#   install, run, debug, clean, lint, lint-strict
# Extra helpful targets:
#   venv, test, package, re
# =============================================================================

PYTHON      := python3
VENV        := .venv
VENV_PY     := $(VENV)/bin/python
VENV_PIP    := $(VENV)/bin/pip
MAIN        := a_maze_ing.py
CONFIG      := config.txt
PKG_DIR     := mazegen_pkg

# Mypy flags exactly as required by the subject (section III.2 "lint").
MYPY_FLAGS  := --warn-return-any --warn-unused-ignores --ignore-missing-imports \
               --disallow-untyped-defs --check-untyped-defs

.PHONY: all install venv run debug clean fclean re lint lint-strict test package help

all: help

# --- Environment ------------------------------------------------------------

venv:
	@test -d $(VENV) || $(PYTHON) -m venv $(VENV)
	@$(VENV_PIP) install --upgrade pip >/dev/null

install: venv
	$(VENV_PIP) install flake8 mypy pytest build

# --- Run --------------------------------------------------------------------

run:
	$(PYTHON) $(MAIN) $(CONFIG)

debug:
	$(PYTHON) -m pdb $(MAIN) $(CONFIG)

# --- Quality ----------------------------------------------------------------

lint:
	flake8 .
	mypy . $(MYPY_FLAGS)

lint-strict:
	flake8 .
	mypy . --strict

test:
	pytest tests/ -v

# --- Packaging --------------------------------------------------------------

package:
	cd $(PKG_DIR) && $(PYTHON) -m build
	cp $(PKG_DIR)/dist/mazegen-*.whl ./
	cp $(PKG_DIR)/dist/mazegen-*.tar.gz ./

# --- Clean ------------------------------------------------------------------

clean:
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type d -name .mypy_cache -exec rm -rf {} +
	find . -type d -name .pytest_cache -exec rm -rf {} +
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	rm -rf $(PKG_DIR)/build $(PKG_DIR)/dist
	rm -f maze.txt

fclean: clean
	rm -rf $(VENV)
	rm -f mazegen-*.whl mazegen-*.tar.gz

re: fclean all

# --- Help -------------------------------------------------------------------

help:
	@echo "A-Maze-ing — available targets:"
	@echo "  make install      Create venv and install dev dependencies"
	@echo "  make run          Run the main script with config.txt"
	@echo "  make debug        Run the main script under pdb"
	@echo "  make lint         flake8 + mypy (subject-required flags)"
	@echo "  make lint-strict  flake8 + mypy --strict"
	@echo "  make test         Run pytest test suite"
	@echo "  make package      Build the reusable mazegen-*.whl package"
	@echo "  make clean        Remove caches and temporary files"
	@echo "  make fclean       clean + remove venv and built artifacts"
	@echo "  make re           fclean + reinstall"
