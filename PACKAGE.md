# baseweb

> A Pythonic base for building interactive web applications

## Overview

Baseweb is a framework for building modern web applications with Quart (async Flask), Vue.js, and Vuetify. It provides a pre-configured foundation with REST APIs, WebSocket support, authentication hooks, and Progressive Web App capabilities out of the box.

Key features:
- **Async-first**: Built on Quart for modern async/await patterns
- **Vue 3 + Vuetify 3**: Modern frontend stack with Composition API
- **REST API**: Built-in Resource class for clean REST endpoints
- **WebSocket**: python-socketio integration for real-time communication
- **Authentication**: Flexible hooks for HTTP and WebSocket auth
- **PWA Support**: Progressive Web App capabilities built-in
- **CLI**: Simple commands for init, config validation, and serving

## Installation

```bash
pip install baseweb
```

For development:
```bash
pip install baseweb gunicorn uvicorn
```

## Quick Start

### Using the CLI (Recommended)

```bash
# Create a new project
mkdir myapp && cd myapp

# Initialize default configuration
baseweb init

# Create a minimal application
cat > app.py << 'EOF'
from baseweb import Baseweb
from baseweb.config import BasewebConfig

config = BasewebConfig(
    name="myapp",
    title="My Application"
)

app = Baseweb(config)
asgi_app = app._asgi_app
EOF

# Validate configuration
baseweb check

# Run the application
baseweb serve
```

Visit http://localhost:8000 to see your application.

### Using Gunicorn Directly

```bash
gunicorn -w 1 -k uvicorn.workers.UvicornWorker "baseweb:server._asgi_app"
```

## Key Components

### BasewebConfig

Configuration dataclass for application settings. Uses layered configuration via Clevis:

```python
from baseweb.config import BasewebConfig

# Programmatic configuration
config = BasewebConfig(
    name="myapp",
    title="My Application",
    style="pwa",  # or "web"
    server={"bind": "0.0.0.0:8000", "workers": 1}
)

# Access nested configuration
config.branding.colors.scheme  # "dark"
config.features.socketio.enabled  # True
config.server.bind  # "0.0.0.0:8000"
```

Configuration priority:
1. CLI arguments (highest)
2. Environment variables (`APP_*`, `GUNICORN_*`)
3. Project-level TOML (`./baseweb.toml`)
4. User-level TOML (`~/.baseweb.toml`)
5. Dataclass defaults (lowest)

**Example baseweb.toml:**
```toml
app_uri = "app:asgi_app"
name = "myapp"
title = "My Application"
style = "web"

[server]
bind = "0.0.0.0:8000"
workers = 1

[features.socketio]
enabled = true
```

### Baseweb

Main application class extending Quart:

```python
from baseweb import Baseweb
from baseweb.config import BasewebConfig

config = BasewebConfig(name="myapp")
app = Baseweb(config)

# ASGI entry point
asgi_app = app._asgi_app
```

**Key features:**
- Pre-configured Quart application
- Socket.IO integration (ASGI mode)
- Template rendering with Jinja2
- Static file serving
- Authentication hooks
- Route registration for app pages

**Methods:**
- `add_resource(resource, route, endpoint=None, security_scope=None)` - Register REST API resources
- `register_component(filename, path, route=None, ...)` - Register Vue components
- `register_stylesheet(filename, path)` - Register CSS files
- `register_app_route(route, endpoint=None, security_scope=None)` - Register app routes
- `authenticated(scope)` - Decorator for protected handlers

### Resource

Base class for RESTful APIs:

```python
from baseweb import Resource
from quart import request

class UserResource(Resource):
    async def get(self, user_id):
        # Handle GET /users/<user_id>
        return {"user": user_id}

    async def post(self):
        # Handle POST /users
        data = await request.get_json()
        return {"created": data}, 201

    async def put(self, user_id):
        # Handle PUT /users/<user_id>
        data = await request.get_json()
        return {"updated": user_id, "data": data}

    async def delete(self, user_id):
        # Handle DELETE /users/<user_id>
        return None, 204

# Register the resource
app.add_resource(UserResource, "/users/<int:user_id>")
app.add_resource(UserResource, "/users", endpoint="users_list")
```

**Supported methods:** GET, POST, PUT, DELETE, PATCH, OPTIONS, HEAD
**Default response:** 405 Method Not Allowed for unimplemented methods

### WebSocket

Socket.IO integration for real-time communication:

```python
from baseweb import Baseweb

app = Baseweb(config)

@app.socketio.on("connect")
async def handle_connect(sid, environ):
    await app.socketio.emit("connected", {"data": "Connected"})

@app.socketio.on("message")
async def handle_message(sid, data):
    # Echo back to sender
    return {"echo": data}

@app.socketio.on("broadcast")
async def handle_broadcast(sid, data):
    # Broadcast to all clients
    await app.socketio.emit("broadcast", data)

# Client-side (JavaScript):
# socket.emit("message", {text: "hello"})
# socket.on("connected", data => console.log(data))
```

### Authentication

Flexible authentication hooks for HTTP and WebSocket:

```python
from baseweb import Baseweb

app = Baseweb(config)

# Sync authenticator
def authenticator(scope, request, *args, **kwargs):
    # Validate request/auth and return True/False
    return request.headers.get("X-API-Key") == "secret"

# Async authenticator
async def async_authenticator(scope, request, *args, **kwargs):
    token = request.headers.get("Authorization")
    return await validate_token(token)

app.authenticator = authenticator

# Protect HTTP routes
@app.route("/protected")
@app.authenticated("app.routes.protected")
async def protected_route():
    return {"status": "authorized"}

# Protect WebSocket handlers
@app.socketio.on("private_event")
@app.authenticated("app.events.private")
async def handle_private(sid, data):
    return {"status": "authorized"}
```

## Common Patterns

### Basic Application

```python
from baseweb import Baseweb
from baseweb.config import BasewebConfig

config = BasewebConfig(
    name="myapp",
    title="My Application"
)

app = Baseweb(config)
asgi_app = app._asgi_app
```

### REST API with Authentication

```python
from baseweb import Baseweb, Resource
from baseweb.config import BasewebConfig
from quart import request

config = BasewebConfig(name="api")
app = Baseweb(config)

# Custom authenticator
async def check_auth(scope, req, *args, **kwargs):
    token = req.headers.get("Authorization")
    return await validate_token(token)

app.authenticator = check_auth

# Protected resource
class ItemsResource(Resource):
    async def get(self):
        return {"items": []}

    async def post(self):
        data = await request.get_json()
        return {"created": data}, 201

app.add_resource(ItemsResource, "/api/items",
                 security_scope="api.items")
```

### PWA Configuration

```python
from baseweb.config import BasewebConfig, FeaturesPWAConfig

config = BasewebConfig(
    name="pwa-app",
    title="PWA Application",
    style="pwa",
    features=FeaturesConfig(
        pwa=FeaturesPWAConfig(
            display="standalone",
            orientation="portrait",
            icons_dir="/static/icons"
        )
    )
)
```

### Custom Branding

```python
from baseweb.config import BasewebConfig, BrandingConfig, BrandingColorsConfig

config = BasewebConfig(
    name="myapp",
    branding=BrandingConfig(
        colors=BrandingColorsConfig(
            scheme="light",
            primary="#1976D2",
            primary_name="blue"
        )
    )
)
```

## Dependencies

### Core Dependencies

- **Quart**: Async web framework (Flask-compatible)
- **python-socketio**: WebSocket support (ASGI mode)
- **python-engineio**: Engine.IO client
- **websocket-client**: WebSocket client
- **clevis**: CLI and configuration management
- **gunicorn**: WSGI/ASGI server
- **uvicorn**: ASGI worker

### Supporting Dependencies

- **dotmap**: Dictionary access via dot notation
- **pyfiglet**: ASCII art banners
- **python-slugify**: URL-friendly slugs
- **tabulate**: Configuration table display
- **urllib3**: HTTP client (>=2.7.0 for security)

### Frontend Stack (included in templates)

- **Vue 3.5**: Progressive JavaScript framework
- **Vuetify 3.12**: Material Design components
- **Vue Router 4.6**: Official router
- **Vuex 4.1**: State management

## Version Notes

**Current Version:** 0.6.0

**Python Support:** 3.10, 3.11, 3.12

### Breaking Changes in 0.5.0+

1. **Async-only (Quart)**: Flask is no longer supported. All route handlers must be async.
2. **Settings dict removed**: Use BasewebConfig dataclass instead of settings dict.
3. **Resource class is async**: All HTTP methods must be async.
4. **Flask-RESTful removed**: Use native Quart routes or Resource class.
5. **Flask-SocketIO replaced**: Use python-socketio with ASGI mode.

**Migration from Flask:**
- Use `baseweb<0.5.0` for Flask/Flask-SocketIO support
- See [Migration Guide](https://baseweb.readthedocs.io/en/latest/migration-guide.html)

### Version 0.6.0

- Unified Page component (consolidates PageWithBanner/PageWithStatus)
- Vuex store module `page` for state management
- Breaking: Removed PageWithBanner and PageWithStatus components

## References

- **Documentation:** https://baseweb.readthedocs.io/
- **Repository:** https://github.com/christophevg/baseweb
- **PyPI:** https://pypi.org/project/baseweb/
- **Issues:** https://github.com/christophevg/baseweb/issues
- **Changelog:** https://github.com/christophevg/baseweb/blob/main/CHANGELOG.md

## CLI Commands

```bash
# Create default baseweb.toml
baseweb init [--force]

# Validate configuration
baseweb check [--app-uri app:app]

# Show current configuration
baseweb config [--format toml]

# Run application
baseweb serve [--server-bind :8080] [--server-workers 4]

# Display version
baseweb version
```

## Development

```bash
# Clone repository
git clone https://github.com/christophevg/baseweb.git
cd baseweb

# Install with uv
uv sync --all-extras

# Run tests
make test

# Run linting
make check

# Multi-version testing
uv run tox
```

## Project Structure

```
src/baseweb/
├── __init__.py      # Baseweb class, Resource, exports
├── __main__.py      # CLI commands
├── config.py        # BasewebConfig and nested configs
├── resource.py      # Resource base class
├── push.py          # Web push notifications
├── vapid.py         # VAPID key support
├── util.py          # Utilities
├── static/          # Vue.js frontend files
└── templates/       # Jinja2 templates
```
