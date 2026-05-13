# baseweb

[![PyPI](https://img.shields.io/pypi/v/baseweb.svg)](https://pypi.org/project/baseweb/)
[![PyPI downloads](https://img.shields.io/pypi/dm/baseweb.svg)](https://pypistats.org/packages/baseweb)
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
> See [Migration Guide](https://baseweb.readthedocs.io/en/latest/migration-guide.html) for migration details.

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

> **Note:** For legacy Flask/synchronous support, use baseweb `< 0.4.0` or see the [legacy support](#legacy-flask-support) section below.

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

If you have an existing Flask-based application, you can:

1. **Pin to legacy version**: Use `baseweb<0.4.0` which supports Flask/Flask-SocketIO
2. **Migrate to Quart**: Follow the [Migration Guide](https://baseweb.readthedocs.io/en/latest/migration-guide.html)

The [baseweb-demo](https://github.com/christophevg/baseweb-demo) repository has a `legacy` tag pointing to the last Flask-compatible commit:

```bash
git clone https://github.com/christophevg/baseweb-demo
cd baseweb-demo
git checkout legacy  # Flask/sync version
```

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
