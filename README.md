# baseweb

[![PyPI](https://img.shields.io/pypi/v/baseweb.svg)][pypi]
[![Python](https://img.shields.io/pypi/pyversions/baseweb.svg)][pypi]
[![uv](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/uv/main/assets/badge/v0.json)][uv]
[![CI](https://img.shields.io/github/actions/workflow/status/christophevg/baseweb/test.yaml.svg)][ci]
[![Coverage](https://img.shields.io/coveralls/github/christophevg/baseweb.svg)][coveralls]
[![License](https://img.shields.io/github/license/christophevg/baseweb.svg)][license]
[![Agentic](https://img.shields.io/badge/workflow-agentic-blueviolet?style=flat-square)](https://christophe.vg/about/Agentic-Workflow)

> A Pythonic base for building interactive web applications

## Async/Quart Support

**Version 0.5.0+** uses Quart (async) instead of Flask (sync).

- All route handlers must be `async` functions
- `request.get_json()` must be awaited
- `render_template()` must be awaited
- WebSocket uses python-socketio (ASGI mode)

**For legacy Flask support:** Use `baseweb<0.5.0` or see the [Migration Guide](https://baseweb.readthedocs.io/en/latest/migration-guide.html).

## Installation

```bash
pip install baseweb
```

## Quick Start

```bash
# Install baseweb and an ASGI server
pip install baseweb gunicorn uvicorn

# Run the stock baseweb application (with WebSocket support)
gunicorn -w 1 -k uvicorn.workers.UvicornWorker "baseweb:server._asgi_app"
```

Visit [http://localhost:8000](http://localhost:8000) to see baseweb in action.

## Features

| Feature | Description |
|---------|-------------|
| Quart Integration | Pre-configured Quart application with async support |
| Vue.js + Vuetify | Modern frontend stack ready to use |
| REST API | Built-in Resource class for REST APIs |
| WebSocket Support | python-socketio with ASGI for real-time communication |
| Authentication | Built-in authentication/authorization hooks (HTTP + WebSocket) |
| PWA Support | Progressive Web App capabilities |

## Usage

### Basic Application

```python
from baseweb import Baseweb

app = Baseweb(__name__)

# ASGI entry point for running with uvicorn/gunicorn
asgi_app = app._asgi_app
```

Run with: `gunicorn -k uvicorn.workers.UvicornWorker "myapp:asgi_app"`

### With REST API

```python
from baseweb import Baseweb, Resource

app = Baseweb(__name__)

class MyResource(Resource):
    async def get(self):
        return {"message": "Hello, async world!"}

    async def post(self):
        data = await request.get_json()
        return {"received": data}

app.add_resource(MyResource, "/api/my-resource")
```

### With WebSockets

```python
from baseweb import Baseweb

app = Baseweb(__name__)

@app.socketio.on("connect")
async def handle_connect(sid, environ):
    await app.socketio.emit("connected", {"data": "Connected"})

@app.socketio.on("message")
async def handle_message(sid, data):
    # Echo back to the sender
    return {"echo": data}
```

### With Authentication

```python
from baseweb import Baseweb

app = Baseweb(__name__)

def authenticator(scope, request, *args, **kwargs):
    # Validate request/auth and return True/False
    return True

app.authenticator = authenticator

# Use @app.authenticated(scope) decorator for protected handlers
@app.socketio.on("private_event")
@app.authenticated("app.events.private")
async def handle_private(sid, data):
    return {"status": "authorized"}
```

For more examples, see the [documentation](https://baseweb.readthedocs.io/).

## Legacy Flask Support

For Flask-based applications (pre-0.5.0):

1. **Pin to legacy version**: Use `baseweb<0.5.0` for Flask/Flask-SocketIO support
2. **Migrate to Quart**: Follow the [Migration Guide](https://baseweb.readthedocs.io/en/latest/migration-guide.html)

The [baseweb-demo](https://github.com/christophevg/baseweb-demo) repository has a `legacy` tag pointing to the last Flask-compatible commit.

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

See [CHANGELOG.md](CHANGELOG.md) for version history. For released versions, see [GitHub Releases](https://github.com/christophevg/baseweb/releases).

## License

[MIT](LICENSE)

[pypi]: https://pypi.org/project/baseweb/
[uv]: https://docs.astral.sh/uv/
[ci]: https://github.com/christophevg/baseweb/actions
[coveralls]: https://coveralls.io/github/christophevg/baseweb
[license]: https://github.com/christophevg/baseweb/blob/main/LICENSE
