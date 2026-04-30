#MODEL=qwen3.5:397b-cloud
#ARGS += --plugin-dir ./
ARGS += --plugin-dir ../c3

-include ~/.claude/Makefile

# colors

GREEN=\033[0;32m
RED=\033[0;31m
BLUE=\033[0;34m
NC=\033[0m

.PHONY: install sync test lint format typecheck check build publish clean run docs coverage dist dist-clean

install:
	uv sync

sync:
	uv sync --frozen

test:
	uv run pytest

lint:
	uv run ruff check src tests

format:
	uv run ruff format src tests

typecheck:
	uv run mypy src

check: lint typecheck test

tox:
	uv run tox

build:
	uv build

publish: build
	uv publish

coverage:
	uv run pytest --cov=src --cov-report=term-missing --cov-report=lcov

# functional targets

run:
	@echo "$(BLUE)running$(GREEN) python -m baseweb$(NC)"
	uv run python -m baseweb

docs:
	cd docs; uv run make html
	open docs/_build/html/index.html

# packaging targets

publish-test: dist
	uv publish --index-url https://test.pypi.org/simple/

dist: dist-clean
	uv build

dist-clean: clean
	rm -rf dist build *.egg-info

clean:
	rm -rf build/ dist/ *.egg-info .tox .pytest_cache .ruff_cache .mypy_cache
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.backup" | xargs rm 2>/dev/null || true

# include optional a personal/local touch

-include Makefile.mak