# baseweb

[![PyPI](https://img.shields.io/pypi/v/baseweb.svg)](https://pypi.org/project/baseweb/)
[![Python](https://img.shields.io/pypi/pyversions/baseweb.svg)](https://pypi.org/project/baseweb/)
![CI](https://github.com/christophevg/baseweb/actions/workflows/test.yaml/badge.svg)
[![Docs](https://readthedocs.org/projects/baseweb/badge/?version=latest)](https://baseweb.readthedocs.io/)
[![Coverage](https://coveralls.io/repos/github/christophevg/baseweb/badge.svg?branch=master)](https://coveralls.io/github/christophevg/baseweb?branch=master)

> A Pythonic base for building interactive web applications

## Important: Async/Quart Migration in Progress

> **Warning:** Baseweb is being migrated from Flask (synchronous) to Quart (asynchronous).
>
> - **Version 1.0.0** will be a **breaking change** - it will only support async/Quart.
> - **Versions < 1.0.0** (current sync/Flask releases) will no longer be actively maintained.
> - If you're starting a new project, consider waiting for 1.0.0.
> - Existing applications will need to update their code to use async patterns.
>
> See [Functional Analysis](analysis/functional.md) for migration details and timeline.

## Installation

```bash
pip install baseweb
```

## Quick Start

```bash
# Install baseweb and a WSGI server
pip install baseweb gunicorn eventlet

# Run the stock baseweb application
gunicorn -k eventlet -w 1 baseweb:server
```

Visit [http://localhost:8000](http://localhost:8000) to see baseweb in action.

## Features

| Feature | Description |
|---------|-------------|
| Flask Integration | Pre-configured Flask application with sensible defaults |
| Vue.js + Vuetify | Modern frontend stack ready to use |
| REST API | Flask-RESTful for building REST APIs |
| WebSocket Support | Flask-SocketIO for real-time communication |
| Authentication | Built-in authentication/authorization hooks |
| PWA Support | Progressive Web App capabilities |

## Usage

### Basic Application

```python
from baseweb import Baseweb

app = Baseweb(__name__)

if __name__ == "__main__":
  app.run()
```

### With REST API

```python
from baseweb import Baseweb
from flask_restful import Api

app = Baseweb(__name__)
api = Api(app)

api.add_resource(MyResource, "/api/my-resource")
```

### With WebSockets

```python
from baseweb import Baseweb
from flask_socketio import emit

app = Baseweb(__name__)

@app.socketio.on("connect")
def handle_connect():
  emit("connected", {"data": "Connected"})
```

For more examples, see the [documentation](https://baseweb.readthedocs.io/).

## Documentation

Full documentation available at [Read the Docs](https://baseweb.readthedocs.io/):

- [Getting Started](https://baseweb.readthedocs.io/en/latest/getting-started.html)
- [Building Your First App](https://baseweb.readthedocs.io/en/latest/building-your-first-baseweb-app.html)
- [Adding Security](https://baseweb.readthedocs.io/en/latest/adding-security.html)
- [Contributing](https://baseweb.readthedocs.io/en/latest/contributing.html)

## Development

### Prerequisites

- Python 3.10, 3.11, or 3.12
- [uv](https://docs.astral.sh/uv/) for dependency management

### Setup

```bash
git clone https://github.com/christophevg/baseweb.git
cd baseweb
uv sync --all-extras
```

### Testing

```bash
# Run tests
uv run pytest

# Run linting
uv run ruff check src tests

# Or use Makefile
make test      # run tests
make check     # run all checks
```

### Multi-Version Testing

```bash
# Install all Python versions (one-time setup)
make install-pythons

# Run tests on all versions
uv run tox
```

### Project Structure

| Directory | Purpose |
|-----------|---------|
| `src/baseweb/` | Main package source |
| `tests/` | Test suite |
| `docs/` | Sphinx documentation |

## Contributing

See [Contributing](https://baseweb.readthedocs.io/en/latest/contributing.html) for guidelines.

## Changelog

See [GitHub Releases](https://github.com/christophevg/baseweb/releases) for version history.

## License

[MIT](LICENSE)