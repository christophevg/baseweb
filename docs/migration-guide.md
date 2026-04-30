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

### API Endpoints (Flask-RESTful Removed)

**Breaking Change:** Flask-RESTful has been removed from Baseweb 1.0.0. It is not compatible with Quart's async architecture.

**Option 1: Use the new Resource class (Recommended for RESTful APIs)**

Baseweb 1.0.0 includes a native Resource class that provides the familiar Flask-RESTful pattern:

**Before (Flask-RESTful):**
```python
from baseweb import server
from flask_restful import Resource

class MyResource(Resource):
    def get(self, item_id):
        return {"item": item_id}
    
    def post(self):
        data = request.get_json()
        return {"created": data}, 201

server.api.add_resource(MyResource, '/api/items/<int:item_id>')
```

**After (Baseweb Resource):**
```python
from baseweb import server, Resource

class MyResource(Resource):
    async def get(self, item_id):
        return {"item": item_id}
    
    async def post(self):
        data = await request.get_json()
        return {"created": data}, 201

server.add_resource(MyResource, '/api/items/<int:item_id>')
```

**Resource class features:**
- Familiar Flask-RESTful pattern with async support
- Automatic 405 Method Not Allowed for unimplemented methods
- Support for authentication: `server.add_resource(MyResource, '/api/items', security_scope='api.items')`
- Works alongside regular routes

**Option 2: Use native Quart routes (Simple APIs)**

For simple APIs without resource classes:

**Before:**
```python
server.api.add_resource(MyResource, '/api/my')
```

**After:**
```python
@server.route('/api/my')
async def get_my():
    data = await request.get_json()
    return {"data": data}
```

**Option 3: Use quart-schema (For validation)**

For API validation with schemas:

```bash
pip install quart-schema
```

```python
from baseweb import server
from quart_schema import validate_request, validate_response
from dataclasses import dataclass

@dataclass
class MyInput:
    name: str

@dataclass
class MyOutput:
    id: int
    name: str

@server.post('/api/items')
@validate_request(MyInput)
@validate_response(MyOutput, 201)
async def create_item(data: MyInput) -> MyOutput:
    return MyOutput(id=1, name=data.name)
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