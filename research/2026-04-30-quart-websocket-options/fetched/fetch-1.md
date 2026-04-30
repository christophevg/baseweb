# python-socketio ASGI Documentation

**Source**: https://python-socketio.readthedocs.io/en/stable/server.html
**Fetched**: 2026-04-30T00:10:00Z

---

## Running python-socketio as an ASGI Application

### Setting Up AsyncServer

Create an asyncio-compatible server using the `AsyncServer` class:

```python
import socketio

sio = socketio.AsyncServer()
```

For explicit ASGI mode configuration:
```python
sio = socketio.AsyncServer(async_mode='asgi')
```

### ASGI Application Integration

Wrap the server with `ASGIApp` to make it ASGI-compatible:

```python
app = socketio.ASGIApp(sio)
```

To combine with an existing ASGI web application (like FastAPI or Quart):

```python
from mywebapp import app  # a FastAPI or other ASGI application
app = socketio.ASGIApp(sio, app)
```

### Running with Uvicorn

Start the application with:
```bash
uvicorn --port 5000 module:app
```

Or via Gunicorn with Uvicorn worker:
```bash
gunicorn --workers 1 --worker-class uvicorn.workers.UvicornWorker --bind 127.0.0.1:5000
```

### Event Handlers

For asyncio servers, event handlers can be coroutines:

```python
@sio.event
async def my_event(sid, data):
    pass
```

Connect/disconnect handlers:
```python
@sio.event
async def connect(sid, environ, auth):
    username = authenticate_user(environ)
    await sio.save_session(sid, {'username': username})

@sio.event
async def disconnect(sid, reason):
    pass
```

### Emit Methods

Use `await` with emit in async contexts:
```python
await self.emit('my_response', data)
```

For targeted emissions to specific clients:
```python
sio.emit('my event', {'data': 'foobar'}, to=user_sid)
```

### Rooms

Enter/leave rooms (async methods need `await`):
```python
@sio.event
async def begin_chat(sid):
    await sio.enter_room(sid, 'chat_users')
```

### Class-Based Namespaces

For async servers, inherit from `AsyncNamespace`:

```python
class MyCustomNamespace(socketio.AsyncNamespace):
    def on_connect(self, sid, environ):
        pass

    async def on_my_event(self, sid, data):
        await self.emit('my_response', data)

sio.register_namespace(MyCustomNamespace('/test'))
```

### User Sessions

Async session methods are coroutines:
```python
@sio.event
async def connect(sid, environ):
    await sio.save_session(sid, {'username': username})

@sio.event
async def message(sid, data):
    session = await sio.get_session(sid)
```

Or use async context manager:
```python
async with sio.session(sid) as session:
    session['username'] = username
```

### Authentication Patterns

Reject connections by returning `False` or raising `ConnectionRefusedError`:

```python
from socketio.exceptions import ConnectionRefusedError

@sio.event
def connect(sid, environ, auth):
    raise ConnectionRefusedError('authentication failed')
```

The `auth` argument receives authentication details passed by the client.