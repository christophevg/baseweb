-include ~/.claude/Makefile

.PHONY: install sync test test-all pytest coverage \
        typecheck lint format format-check check \
        build publish publish-test dist dist-clean \
        clean clean-all run docs help

# colors

GREEN=\033[0;32m
RED=\033[0;31m
BLUE=\033[0;34m
NC=\033[0m

## environment management

env-dev:
	uv sync --extra dev

env-run:
	uv sync

## Testing

### Run all tests with linting and formatting checks
test: env-dev format-check lint pytest

### Run tests against all supported Python versions
test-all: env-dev(3.10, 3.11, 3.12)
	uv run tox

### Run tests with pytest
pytest: env-dev
	@echo "👷‍♂️ $(BLUE)running tests$(NC)"
	@uv run pytest -v

### Run tests with coverage reporting
coverage: env-dev
	@echo "👷‍♂️ $(BLUE)running tests with coverage$(NC)"
	@uv run pytest --cov=src --cov-report=term --cov-report=html --cov-report=lcov

## Code Quality

typecheck: env-dev ## Run mypy type checking
	@echo "👷‍♂️ $(BLUE)running type checking$(NC)"
	@uv run mypy src

fix-lint: env-dev
	@uv run ruff check --fix src tests

lint: env-dev ## Run ruff linting
	@echo "👷‍♂️ $(BLUE)running linter$(NC)"
	@uv run ruff check src tests

format: env-dev  ## Format code with ruff
	@echo "👷‍♂️ $(BLUE)formatting$(NC)"
	@uv run ruff format src tests

format-check: env-dev ## Check formatting without making changes
	@echo "👷‍♂️ $(BLUE)checking formatting$(NC)"
	@uv run ruff format --check src tests

check: lint typecheck pytest ## Run all checks (lint, typecheck, test)

## Build & Publish

build: dist ## Build package distributions

publish: env-dev dist ## Build and publish to PyPI (requires credentials)
	@echo "👷‍♂️ $(BLUE)publishing to PyPI$(NC)"
	uv run twine upload dist/*

publish-test: env-dev dist ## Build and publish to TestPyPI (requires credentials)
	@echo "👷‍♂️ $(BLUE)publishing to TestPyPI$(NC)"
	uv run twine upload --repository testpypi dist/*

dist: env-dev dist-clean ## Build distributions
	@echo "👷‍♂️ $(BLUE)building distribution$(NC)"
	uv build

dist-clean: ## Clean build artifacts
	@rm -rf dist build *.egg-info

## Cleanup

clean: ## Remove build artifacts and cache files
	@find . -type f -name "*.backup" -delete
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@rm -rf .pytest_cache .ruff_cache .mypy_cache .coverage coverage.lcov htmlcov

clean-all: clean dist-clean clean-venv ## Deep clean (removes venv, build artifacts, caches)

## Development

run: env-run ## Run the example hello-world app
	@echo "👷‍♂️ $(BLUE)starting hello-world example$(NC)"
	cd examples/hello-world && uv run gunicorn -k uvicorn.workers.UvicornWorker app:asgi_app --reload

docs: env-dev ## Build and open documentation
	@echo "👷‍♂️ $(BLUE)building documentation$(NC)"
	cd docs && uv run sphinx-build -M html . _build
	@open docs/_build/html/index.html

## Help

help: ## Show this help message
	@echo "Usage: make [target]"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' Makefile | sort | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

# include optional a personal/local touch

-include Makefile.mak
