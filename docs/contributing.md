# Contributing

Contributions are welcome! This guide will help you get started.

## Development Setup

### Prerequisites

- Python 3.10, 3.11, or 3.12
- [uv](https://docs.astral.sh/uv/) - Fast Python package manager

### Getting Started

1. Fork and clone the repository:
   ```bash
   git clone https://github.com/YOUR_USERNAME/baseweb.git
   cd baseweb
   ```

2. Install dependencies:
   ```bash
   uv sync
   ```
   This creates a `.venv` and installs all dependencies including dev tools.

3. Run tests to verify setup:
   ```bash
   uv run pytest
   ```

## Development Workflow

### Running Tests

```bash
uv run pytest                    # Run all tests
uv run pytest -v                 # Verbose output
uv run pytest --cov=src          # With coverage
```

Or use Makefile:
```bash
make test
```

### Code Quality

```bash
uv run ruff check src tests       # Lint
uv run ruff format src tests      # Format
uv run mypy src                   # Type check
```

Or use Makefile:
```bash
make lint
make format
make typecheck
make check        # All checks
```

### Building Documentation

```bash
cd docs
uv run make html
```

Or:
```bash
make docs
```

## Pull Request Process

1. Create an issue to discuss your change
2. Fork the repository
3. Create a feature branch
4. Make your changes
5. Run tests and linting: `make check`
6. Submit a pull request against `master`

## Code Style

- Follow PEP 8 (enforced by ruff)
- Use 2 spaces for indentation
- Add type hints where appropriate
- Write tests for new functionality

## Questions?

Open an [issue](https://github.com/christophevg/baseweb/issues) if you have questions.