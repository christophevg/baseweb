# GitHub Discussion: Quart Support

**Source**: https://github.com/miguelgrinberg/python-socketio/discussions/777
**Fetched**: 2026-04-30T00:15:00Z

---

## Python-SocketIO with Quart Integration

**Official Stance:** The maintainer (miguelgrinberg) states python-socketio works with "any asyncio web framework, including Quart" but there are no plans for a dedicated Quart extension similar to Flask-SocketIO.

**Solution:** Use the ASGI async mode to integrate both frameworks.

**Code Example (by user hiway):**

```python
import asyncio
import socketio
import uvicorn

from quart import Quart
from quart_cors import cors

CORS_ALLOWED_ORIGINS = "*"

class QuartSIO:
    def __init__(self) -> None:
        self._sio = socketio.AsyncServer(
            async_mode="asgi", cors_allowed_origins=CORS_ALLOWED_ORIGINS
        )
        self._quart_app = Quart(__name__)
        self._quart_app = cors(self._quart_app, allow_origin=CORS_ALLOWED_ORIGINS)
        self._sio_app = socketio.ASGIApp(self._sio, self._quart_app)
        self.route = self._quart_app.route
        self.on = self._sio.on
        self.emit = self._sio.emit

    async def _run(self, host: str, port: int):
        uvconfig = uvicorn.Config(self._sio_app, host=host, port=port)
        server = uvicorn.Server(config=uvconfig)
        await server.serve()

    def run(self, host: str, port: int):
        asyncio.run(self._run(host, port))

app = QuartSIO()

@app.route("/")
async def index():
    return "Hello, world!"

@app.on("connect")
async def on_connect(sid, environ):
    print("Connected")

if __name__ == "__main__":
    app.run("localhost", 3000)
```

**Key Pattern:** Wrap the Quart app inside `socketio.ASGIApp()` along with the AsyncServer to serve both HTTP routes and WebSocket connections through uvicorn.