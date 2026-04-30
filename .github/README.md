# baseweb

> A Pythonic base for building interactive web applications

[![Latest Version on PyPI](https://img.shields.io/pypi/v/baseweb.svg)](https://pypi.python.org/pypi/baseweb/)
[![Supported Implementations](https://img.shields.io/pypi/pyversions/baseweb.svg)](https://pypi.python.org/pypi/baseweb/)
![Build Status](https://github.com/christophevg/baseweb/actions/workflows/test.yaml/badge.svg)
[![Documentation Status](https://readthedocs.org/projects/baseweb/badge/?version=latest)](https://baseweb.readthedocs.io/en/latest/?badge=latest)
[![Coverage Status](https://coveralls.io/repos/github/christophevg/baseweb/badge.svg?branch=master)](https://coveralls.io/github/christophevg/baseweb?branch=master)

## Important: Async/Quart Migration in Progress

> **Warning:** Baseweb is being migrated from Flask (synchronous) to Quart (asynchronous).
>
> - **Version 1.0.0** will be a **breaking change** - it will only support async/Quart.
> - **Versions < 1.0.0** (current sync/Flask releases) will no longer be actively maintained.
> - If you're starting a new project, consider waiting for 1.0.0.
> - Existing applications will need to update their code to use async patterns.
>
> See [Functional Analysis](analysis/functional.md) for migration details and timeline.

## Development

Interested in contributing? Here's how to set up your development environment.

### Prerequisites

- Python 3.10+ (3.10, 3.11, or 3.12)
- [uv](https://docs.astral.sh/uv/) for dependency management

### Quick Start

```bash
# Clone the repository
git clone https://github.com/christophevg/baseweb.git
cd baseweb

# Install dependencies (including dev dependencies)
uv sync

# Run tests
uv run pytest

# Run linting
uv run ruff check src tests

# Or use Makefile targets
make test      # run tests
make lint      # run linting
make check     # run all checks
```

### Multi-Version Testing

Test across all supported Python versions (3.10, 3.11, 3.12):

```bash
# Install all Python versions (one-time setup)
make install-pythons

# Run tests on all versions
uv run tox
```

### Project Structure

- `src/baseweb/` - Main package source
- `tests/` - Test suite
- `docs/` - Documentation (Sphinx)

See [Contributing](https://baseweb.readthedocs.io/en/latest/contributing.html) for more details.

## Documentation

Visit [Read the Docs](https://baseweb.readthedocs.org) for the full documentation, including overviews and several examples.


