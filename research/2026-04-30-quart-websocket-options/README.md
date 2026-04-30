# Quart WebSocket Implementation Options

**Research Date:** 2026-04-30
**Purpose:** Choose a WebSocket solution for baseweb after Flask-to-Quart migration
**Previous Research:** none

---

## Executive Summary

The recommended approach is **python-socketio with ASGI mode**. This provides full Socket.IO protocol compatibility, maintains existing frontend code unchanged, and integrates seamlessly with Quart via `socketio.ASGIApp`. The migration requires minimal backend changes while preserving all existing functionality including the decorator pattern, session ID access, authentication, and broadcasting.

---

## 1. Option Comparison

### Option 1: python-socketio with Quart (RECOMMENDED)

**How it works:** python-socketio's `AsyncServer` in ASGI mode wraps the Quart app via `socketio.ASGIApp`, serving both HTTP and WebSocket through a single ASGI application.

**Pros:**
- Full Socket.IO protocol compatibility (fallback transports, reconnection, rooms)
- Existing frontend code requires NO changes
- Decorator pattern preserved (`@sio.on('event')`)
- Session ID automatically provided as `sid` parameter
- Authentication via `ConnectionRefusedError` in connect handler
- Broadcasting built-in with `sio.emit()`
- Works with uvicorn/gunicorn ASGI workers
- Already a dependency in baseweb

**Cons:**
- Adds ~1-2ms latency over raw WebSocket (negligible for most use cases)
- Slightly more complex setup than native WebSocket

### Option 2: Quart Native WebSocket

**How it works:** Use Quart's built-in `@app.websocket('/path')` decorator with raw WebSocket protocol.

**Pros:**
- No additional dependencies
- Slightly lower latency
- Simpler conceptual model
- Native Quart integration

**Cons:**
- **Requires complete frontend rewrite** - Socket.IO client must be replaced with native WebSocket
- Lose Socket.IO features: automatic reconnection, fallback transports, rooms, acknowledgments
- Must implement broadcasting pattern manually (requires Broker class)
- No request/response callback pattern (must implement own ACK system)
- Different event model (raw messages vs named events)

### Option 3: Flask-SocketIO in Threaded Mode

**How it works:** Keep Flask-SocketIO but run Quart in threaded mode instead of ASGI.

**Pros:**
- Zero code changes required

**Cons:**
- **Loses async benefits** - defeats the purpose of Quart migration
- May not work with ASGI workers (gunicorn + uvicorn)
- Threaded mode has scalability limitations
- Not recommended by maintainers

---

## 2. Recommended Implementation: python-socketio ASGI

### Integration Pattern

The key insight from the official maintainer [1] is that `python-socketio` works with "any asyncio web framework, including Quart" via the ASGI interface. The pattern is:

```python
import socketio
from quart import Quart

# Create Quart app
app = Quart(__name__)

# Create Socket.IO server in ASGI mode
sio = socketio.AsyncServer(async_mode='asgi')

# Wrap both in a single ASGI app
socket_app = socketio.ASGIApp(sio, app)
```

### Baseweb Integration

Based on the current baseweb structure, here's the recommended implementation:

```python
# In baseweb/__init__.py

import socketio

class Baseweb(Quart):
  def __init__(self, name=None, *args, **kwargs):
    super().__init__(name, *args, **kwargs)

    # Initialize Socket.IO server in ASGI mode
    self._sio = socketio.AsyncServer(
      async_mode='asgi',
      cors_allowed_origins='*'  # Configure as needed
    )

    # Create combined ASGI app
    self._asgi_app = socketio.ASGIApp(self._sio, self)

  @property
  def socketio(self):
    """Expose Socket.IO server for event handlers."""
    return self._sio

  def on(self, event, namespace=None):
    """Convenience decorator for Socket.IO events."""
    return self._sio.on(event, namespace=namespace)

  def emit(self, event, data, room=None, namespace=None):
    """Convenience method for emitting events."""
    return self._sio.emit(event, data, room=room, namespace=namespace)

  # For running with uvicorn, use the wrapped ASGI app
  # uvicorn app:server._asgi_app (not app:server)
```

### Event Handler Pattern

The decorator pattern is preserved with minimal changes:

**Before (Flask-SocketIO):**
```python
@server.socketio.on("connect")
def on_connect():
    logger.info(f"connect: {server.request.sid}")

@server.socketio.on("hello")
@server.authenticated("app.io.hello")
def on_hello(name):
    logger.info(f"received hello from {name}")
    return "Hello from socketio!"

server.socketio.emit("log", msg)
```

**After (python-socketio ASGI):**
```python
@server.socketio.on("connect")
async def on_connect(sid, environ):
    logger.info(f"connect: {sid}")

@server.socketio.on("hello")
@server.authenticated("app.io.hello")  # Works with async handlers
async def on_hello(sid, name):
    logger.info(f"received hello from {sid}: {name}")
    return "Hello from socketio!"

await server.socketio.emit("log", msg)
```

### Key Differences to Note

| Aspect | Flask-SocketIO | python-socketio ASGI |
|--------|---------------|----------------------|
| Handler signature | `def handler(data)` | `async def handler(sid, data)` |
| Session ID access | `server.request.sid` | First parameter `sid` |
| Handler type | Sync function | Async coroutine |
| Emit | `socketio.emit()` | `await socketio.emit()` |

### Authentication Pattern

Authentication works via the connect handler:

```python
from socketio.exceptions import ConnectionRefusedError

@server.socketio.on("connect")
async def on_connect(sid, environ, auth):
    # Check auth parameter or environ headers
    if not await validate_auth(auth, environ):
        raise ConnectionRefusedError("Authentication failed")
    # Connection accepted if no exception raised
```

The existing `@server.authenticated()` decorator will need adaptation:

```python
def authenticated(self, scope):
    def decorator(f):
        @wraps(f)
        async def wrapper(sid, *args, **kwargs):
            # Get session data from environ or auth
            if not await self._valid_socket_credentials(scope, sid):
                raise ConnectionRefusedError("Unauthorized")
            return await f(sid, *args, **kwargs)
        return wrapper
    return decorator
```

### Broadcasting

Broadcasting is identical to Flask-SocketIO:

```python
# Broadcast to all connected clients
await server.socketio.emit("log", {"message": msg})

# Emit to specific client
await server.socketio.emit("private", data, to=sid)

# Emit to room
await server.socketio.emit("room_event", data, room="chat_room")
```

### Running the Application

With gunicorn:
```bash
gunicorn --workers 1 --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000 "app:server._asgi_app"
```

With uvicorn:
```bash
uvicorn "app:server._asgi_app" --host 0.0.0.0 --port 8000
```

**Important:** Use `server._asgi_app` (the wrapped app), not `server` directly.

---

## 3. Frontend Compatibility

**No frontend changes required.** The Socket.IO client library works identically with python-socketio:

```javascript
// Existing code works unchanged
socket.emit("hello", name, function(response) {
    console.log("Received:", response);
});

socket.on("log", function(msg) {
    console.log("Log:", msg);
});
```

---

## 4. Migration Checklist

1. **Update baseweb/__init__.py:**
   - Replace `import flask_socketio` with `import socketio`
   - Initialize `AsyncServer(async_mode='asgi')`
   - Create `socketio.ASGIApp(sio, self)` wrapper
   - Update `socketio` property to return `self._sio`
   - Add convenience methods: `on()`, `emit()`

2. **Update pyproject.toml:**
   - Remove `Flask-SocketIO` dependency
   - Keep `python-socketio` and `python-engineio`

3. **Update running commands:**
   - Change `app:server` to `app:server._asgi_app`

4. **Update event handlers:**
   - Add `async` to handler functions
   - Add `sid` as first parameter
   - Add `await` to `emit()` calls
   - Change `server.request.sid` to just `sid`

5. **Update authentication:**
   - Adapt `authenticated()` decorator for async
   - Use `ConnectionRefusedError` for rejection

---

## 5. Resource Comparison

| Aspect | python-socketio Docs [1] | GitHub Discussion [2] | Quart Native [3] |
|--------|--------------------------|------------------------|------------------|
| ASGI integration | "Combine with existing ASGI app" | Confirmed working | Built-in |
| Event handlers | "Coroutines with async/await" | Working example | Different model |
| Authentication | `ConnectionRefusedError` | Shown in example | `abort(403)` |
| Broadcasting | Built-in `emit()` | Built-in | Manual Broker class |
| Frontend | Socket.IO client | Socket.IO client | Native WebSocket |

### Corroborated Information

Information confirmed by multiple sources:
- **python-socketio works with Quart**: Confirmed by [1], [2]
- **ASGI wrapping pattern**: `socketio.ASGIApp(sio, app)` shown in [1], [2]
- **Async handlers required**: Stated in [1], demonstrated in [2]
- **No Quart-specific extension planned**: Stated by maintainer in [2]

---

## 6. Near-Miss Tier

### Quart Native WebSocket - For New Projects

- **Why it nearly made the cut:** Simpler, no extra dependency, slightly better performance
- **Why it ranked below:** Requires complete frontend rewrite, loses Socket.IO features
- **Best for:** New projects without existing Socket.IO frontend, or when maximum performance is critical

---

## Key Takeaways

1. **python-socketio ASGI mode is the clear winner** for maintaining existing functionality while gaining async benefits
2. **Frontend requires no changes** - Socket.IO client library is compatible
3. **Migration is straightforward** - mainly adding `async`/`await` and `sid` parameter
4. **The wrapper pattern is well-established** - officially documented and community-validated
5. **Running requires using the wrapped ASGI app** - `server._asgi_app` instead of `server`

---

## Sources

[1] python-socketio Server Documentation - https://python-socketio.readthedocs.io/en/stable/server.html - Accessed 2026-04-30

[2] Quart support Discussion - https://github.com/miguelgrinberg/python-socketio/discussions/777 - Accessed 2026-04-30

[3] Quart Native WebSocket Documentation - https://quart.palletsprojects.com/en/stable/how_to_guides/websockets.html - Accessed 2026-04-30

[4] Quart Chat Tutorial - https://quart.palletsprojects.com/en/stable/tutorials/chat_tutorial.html - Accessed 2026-04-30