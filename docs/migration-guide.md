# Migrating from Baseweb 0.x to 1.0.0

Baseweb 1.0.0 represents a major architecture change: migration from Flask to Quart for async support.

## Breaking Changes

### Python Version

Baseweb 1.0.0 requires Python 3.11 or higher for async/await support.

### Flask → Quart

All route handlers must now be async functions.

**Before (0.x):**
```python
from baseweb import Baseweb

app = Baseweb("myapp")

@app.route("/api/data")
def get_data():
    return {"data": "value"}
```

**After (1.0.0):**
```python
from baseweb import Baseweb

app = Baseweb("myapp")

@app.route("/api/data")
async def get_data():
    return {"data": "value"}
```

### Template Rendering

`render_template()` must now be awaited.

**Before:**
```python
@app.route("/page")
def page():
    return render_template("page.html", title="My Page")
```

**After:**
```python
@app.route("/page")
async def page():
    return await render_template("page.html", title="My Page")
```

### Request JSON

`request.get_json()` must now be awaited.

**Before:**
```python
@app.route("/api/submit", methods=["POST"])
def submit():
    data = request.get_json()
    return {"received": data}
```

**After:**
```python
@app.route("/api/submit", methods=["POST"])
async def submit():
    data = await request.get_json()
    return {"received": data}
```

### Static File Serving

`send_from_directory()` must now be awaited.

**Before:**
```python
from flask import send_from_directory

@app.route("/static/<path:filename>")
def serve_static(filename):
    return send_from_directory("static", filename)
```

**After:**
```python
from quart import send_from_directory

@app.route("/static/<path:filename>")
async def serve_static(filename):
    return await send_from_directory("static", filename)
```

### WebSocket

Flask-SocketIO is replaced with Quart's native WebSocket support.

**Before:**
```python
from flask_socketio import SocketIO, emit

socketio = SocketIO(app)

@socketio.on("message")
def handle_message(data):
    emit("response", {"received": data})
```

**After:**
```python
from quart import websocket

@app.websocket("/ws")
async def ws():
    while True:
        data = await websocket.receive()
        await websocket.send_json({"received": data})
```

### API Endpoints (Flask-RESTful)

If using Flask-RESTful, install `quart-flask-patch` for compatibility:

```bash
pip install quart-flask-patch
```

Resource classes remain largely unchanged, but request parsing must be async:

**Before:**
```python
from flask_restful import Resource

class MyResource(Resource):
    def get(self):
        data = request.get_json()
        return {"data": data}
```

**After:**
```python
from flask_restful import Resource

class MyResource(Resource):
    async def get(self):
        data = await request.get_json()
        return {"data": data}
```

### Authentication Decorators

Custom authentication decorators must be updated to work with async handlers.

**Before:**
```python
def auth_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_authenticated:
            return {"error": "Unauthorized"}, 401
        return f(*args, **kwargs)
    return decorated
```

**After:**
```python
def auth_required(f):
    @wraps(f)
    async def decorated(*args, **kwargs):
        if not current_user.is_authenticated:
            return {"error": "Unauthorized"}, 401
        return await f(*args, **kwargs)
    return decorated
```

## Migration Checklist

- [ ] Update Python to 3.11+
- [ ] Update baseweb to 1.0.0
- [ ] Convert all route handlers to async functions
- [ ] Add `await` to all `render_template()` calls
- [ ] Add `await` to all `request.get_json()` calls
- [ ] Add `await` to all `send_from_directory()` calls
- [ ] Update WebSocket code to Quart native format
- [ ] Run tests and verify all functionality

## Estimated Migration Time

For a typical Baseweb application: **less than 1 hour**.