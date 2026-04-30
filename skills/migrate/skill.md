---
name: baseweb-migrate
description: Migrate Flask-based baseweb apps to async Quart
triggers:
  - when asked to migrate a Flask/baseweb app
  - when modernizing legacy baseweb code
  - when converting sync Flask patterns to async Quart
---

# Baseweb Migrate Skill

Migrate existing Flask-based baseweb applications to the modern async Quart architecture.

## Overview

This skill guides the migration from Flask (sync) to Quart (async) for baseweb applications:

| From | To |
|------|-----|
| Flask | Quart |
| flask_restful.Resource | baseweb.Resource |
| Sync handlers | Async handlers |
| Flask-SocketIO | python-socketio (ASGI) |
| eventlet | uvicorn |

## When to Use

- Migrating existing baseweb `< 0.4.0` apps to `>= 1.0.0`
- Converting sync Flask patterns to async Quart patterns
- Modernizing legacy baseweb codebases

## Migration Steps

### Step 1: Analyze Current Project

First, analyze the existing project structure:

```bash
# Find all Python files
find . -name "*.py" -type f

# Check for Flask imports
grep -r "from flask import" --include="*.py"
grep -r "import flask" --include="*.py"

# Check for Flask-RESTful usage
grep -r "from flask_restful import" --include="*.py"
grep -r "flask_restful" --include="*.py"

# Check for Flask-SocketIO usage
grep -r "from flask_socketio import" --include="*.py"
grep -r "Flask-SocketIO" --include="*.py"
```

### Step 2: Update Dependencies

Update `requirements.txt` or `pyproject.toml`:

```diff
- Flask>=2.0.0
- Flask-RESTful>=0.3.0
- Flask-SocketIO>=5.0.0
- eventlet>=0.30.0

+ quart>=0.18.0
+ python-socketio>=5.0.0
+ gunicorn>=21.0.0
+ uvicorn[standard]>=0.24.0
```

### Step 3: Update Imports

Replace Flask imports with Quart imports:

| Before | After |
|--------|-------|
| `from flask import Flask` | `from quart import Quart` |
| `from flask import request, abort, Response` | `from quart import request, abort, Response` |
| `from flask import render_template` | `from quart import render_template` |
| `from flask import send_from_directory` | `from quart import send_from_directory` |
| `from flask_restful import Resource` | `from baseweb import Resource` |

### Step 4: Convert to Async

Convert sync methods to async:

```python
# Before (sync)
class Hello(Resource):
    def get(self):
        return {"message": "Hello"}

    def post(self):
        data = request.get_json()
        return {"received": data}

# After (async)
class Hello(Resource):
    async def get(self):
        return {"message": "Hello"}

    async def post(self):
        data = await request.get_json()
        return {"received": data}
```

**Key changes:**
- Add `async` keyword to method definitions
- Add `await` to `request.get_json()` calls
- Add `await` to `render_template()` calls (in route handlers)
- Add `await` to `send_from_directory()` calls (in static handlers)

### Step 5: Update Resource Registration

Replace Flask-RESTful pattern with native baseweb pattern:

```python
# Before
from flask_restful import Api
api = Api(server)
api.add_resource(HelloResource, '/api/hello')

# After
server.add_resource(HelloResource, '/api/hello')
```

### Step 6: Migrate Socket.IO Handlers

Convert Flask-SocketIO to python-socketio:

```python
# Before (Flask-SocketIO)
from flask_socketio import emit

@server.socketio.on("connect")
def handle_connect():
    emit("connected", {"status": "ok"})

@server.socketio.on("message")
def handle_message(data):
    return {"echo": data}

# After (python-socketio with ASGI)
@server.socketio.on("connect")
async def handle_connect(sid, environ):
    await server.socketio.emit("connected", {"status": "ok"})

@server.socketio.on("message")
async def handle_message(sid, data):
    return {"echo": data}
```

**Key changes:**
- Add `async` keyword to handler definitions
- Add `sid` as first parameter (session ID)
- Add `environ` as second parameter for connect handlers
- Add `await` to `emit()` calls

### Step 7: Update Authentication Decorator

The `@server.authenticated()` decorator works for both HTTP and Socket.IO:

```python
# HTTP handlers (works the same)
@server.authenticated("app.resource.get")
async def get(self):
    return {"data": "protected"}

# Socket.IO handlers (now supported)
@server.socketio.on("private_event")
@server.authenticated("app.events.private")
async def handle_private(sid, data):
    return {"echo": data}
```

### Step 8: Update Running Configuration

Update how the application is run:

```bash
# Before (WSGI with eventlet)
gunicorn -k eventlet -w 1 module:server

# After (ASGI with uvicorn)
gunicorn -w 1 -k uvicorn.workers.UvicornWorker "module:asgi_app"
```

Create the ASGI entry point:

```python
# module/__init__.py
from baseweb import Baseweb

server = Baseweb("myapp")

# ... configuration ...

# ASGI entry point (for uvicorn/gunicorn)
asgi_app = server._asgi_app
```

### Step 9: Update Tests

Update tests for async:

```python
# Before
def test_endpoint():
    response = client.get('/api/test')
    assert response.status_code == 200

# After
@pytest.mark.asyncio
async def test_endpoint():
    async with app.test_app() as test_app:
        client = test_app.test_client()
        response = await client.get('/api/test')
        assert response.status_code == 200
```

Add `pytest-asyncio` to test dependencies:

```toml
[project.optional-dependencies]
dev = [
    "pytest>=7.0.0",
    "pytest-asyncio>=0.21.0",
]

[tool.pytest.ini_options]
asyncio_mode = "auto"
```

## Migration Checklist

Use this checklist to track migration progress:

- [ ] Update dependencies (Flask → Quart)
- [ ] Update imports (flask → quart, flask_restful → baseweb)
- [ ] Convert sync methods to async
- [ ] Add `await` to `request.get_json()` calls
- [ ] Add `await` to `render_template()` calls
- [ ] Replace `server.api.add_resource()` with `server.add_resource()`
- [ ] Migrate Socket.IO handlers (add `sid`, `async`, `await`)
- [ ] Create `asgi_app` entry point
- [ ] Update run command (gunicorn + uvicorn)
- [ ] Update tests for async
- [ ] Run tests and verify all pass
- [ ] Manual testing of affected features

## Common Issues

| Issue | Cause | Solution |
|-------|-------|----------|
| `RuntimeError: Not within a request context` | Using `request` in Socket.IO handler | Socket.IO handlers don't have request context. Use `sid` for authentication. |
| `SyntaxError: 'await' outside async function` | Missing `async` keyword | Add `async` to function definition |
| `TypeError: object is not awaitable` | Missing `await` keyword | Add `await` before async call |
| 405 Method Not Allowed | Missing async on method | Add `async` to HTTP method |
| Tests fail with "async not supported" | Missing pytest-asyncio | Add pytest-asyncio dependency |

## Examples

### Full Migration Example

**Before (Flask/sync):**

```python
# app/__init__.py
from flask import Flask, request
from flask_restful import Resource, Api
from flask_socketio import SocketIO, emit

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")
api = Api(app)

class Hello(Resource):
    def get(self):
        return {"message": "Hello"}

    def post(self):
        data = request.get_json()
        return {"received": data}, 201

api.add_resource(Hello, '/api/hello')

@socketio.on("connect")
def handle_connect():
    emit("connected", {})

@socketio.on("echo")
def handle_echo(data):
    return data

if __name__ == "__main__":
    socketio.run(app, port=8000)
```

**After (Quart/async):**

```python
# app/__init__.py
from quart import Quart, request
from baseweb import Baseweb, Resource

server = Baseweb("myapp")

class Hello(Resource):
    async def get(self):
        return {"message": "Hello"}

    async def post(self):
        data = await request.get_json()
        return {"received": data}, 201

server.add_resource(Hello, '/api/hello')

@server.socketio.on("connect")
async def handle_connect(sid, environ):
    await server.socketio.emit("connected", {})

@server.socketio.on("echo")
async def handle_echo(sid, data):
    return data

# ASGI entry point
asgi_app = server._asgi_app
```

## Version Compatibility

| baseweb Version | Backend | WebSocket | Running |
|-----------------|---------|-----------|---------|
| `< 0.4.0` | Flask | Flask-SocketIO | eventlet |
| `>= 1.0.0` | Quart | python-socketio | uvicorn |

## See Also

- [Migration Guide](https://github.com/christophevg/baseweb/blob/master/docs/migration-guide.md)
- [baseweb-demo legacy tag](https://github.com/christophevg/baseweb-demo/tree/legacy) - Last Flask-compatible version