# Quart Chat Tutorial - Broadcasting Patterns

**Source**: https://quart.palletsprojects.com/en/stable/tutorials/chat_tutorial.html
**Fetched**: 2026-04-30T00:30:00Z

---

## Code Examples and Patterns from Quart Chat Tutorial

### Message Broker Pattern

The in-memory broker manages connections and message distribution:

```python
import asyncio
from typing import AsyncGenerator

class Broker:
    def __init__(self) -> None:
        self.connections = set()

    async def publish(self, message: str) -> None:
        for connection in self.connections:
            await connection.put(message)

    async def subscribe(self) -> AsyncGenerator[str, None]:
        connection = asyncio.Queue()
        self.connections.add(connection)
        try:
            while True:
                yield await connection.get()
        finally:
            self.connections.remove(connection)
```

### Managing Connected Clients

"The `Broker` has a publish-subscibe pattern based interface, with clients expected to publish messages to other clients whilst subscribing to any messages sent."

- Uses a `set()` to track connections
- Each connection is an `asyncio.Queue()`
- Connections added on subscribe, removed in `finally` block

### WebSocket Route with Connection Handling

```python
import asyncio
from quart import websocket
from chat.broker import Broker

broker = Broker()

async def _receive() -> None:
    while True:
        message = await websocket.receive()
        await broker.publish(message)

@app.websocket("/ws")
async def ws() -> None:
    try:
        task = asyncio.ensure_future(_receive())
        async for message in broker.subscribe():
            await websocket.send(message)
    finally:
        task.cancel()
        await task
```

### Broadcasting Pattern

"The `_receive` coroutine must run as a separate task to ensure that sending and receiving run concurrently."

- Receiving runs in separate task via `asyncio.ensure_future()`
- Publishing broadcasts to all connected queues
- Task properly cancelled in `finally` block on disconnect

### JavaScript Client Code

```javascript
const ws = new WebSocket(`ws://${location.host}/ws`);

ws.addEventListener('message', function (event) {
  const li = document.createElement("li");
  li.appendChild(document.createTextNode(event.data));
  document.getElementById("messages").appendChild(li);
});

function send(event) {
  const message = (new FormData(event.target)).get("message");
  if (message) {
    ws.send(message);
  }
  event.target.reset();
  return false;
}
```

### Key Patterns Summary

1. **Concurrent send/receive**: Separate task for receiving ensures both directions work simultaneously
2. **Connection lifecycle**: `try/finally` ensures cleanup on disconnect
3. **Broadcasting**: Iterating through all connections to publish messages
4. **Queue per client**: Each subscriber gets its own queue for message delivery