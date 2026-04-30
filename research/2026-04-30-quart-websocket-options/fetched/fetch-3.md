# Quart Native WebSocket Documentation

**Source**: https://quart.palletsprojects.com/en/stable/how_to_guides/websockets.html
**Fetched**: 2026-04-30T00:25:00Z

---

# Quart WebSocket Support Summary

## Basic Usage
Declare a websocket function using `@app.websocket('/ws')` decorator instead of a route decorator. The `websocket` object is a global similar to `request` with shared attributes like `headers`.

**Core methods:**
- `websocket.receive()` - returns `bytes` or `str` depending on what client sent
- `websocket.send(data)` - sends bytes or strings
- `websocket.accept()` - accepts connection (auto-invoked by receive/send)

## Authentication/Rejection
Reject connections by returning early from the websocket function: "a server can choose to reject a websocket request. To do so just return from the websocket function as you would with a route function." Can check `websocket.authorization.username` and `websocket.authorization.password` or use `abort(403)`.

## Connection Lifecycle
- **Disconnect detection**: "When a client disconnects a `CancelledError` is raised" - must be re-raised in the except block
- **Closing**: Use `await websocket.close(1000)` with appropriate WebSocket error code; closing before acceptance triggers a 403 HTTP response

## Independent Send/Receive
For bidirectional communication, use separate async tasks: "To send and receive independently requires independent tasks" with `asyncio.create_task()` and `asyncio.gather()`. The gather call is critical—"without it the websocket function would return triggering Quart to send a HTTP response."

## Testing
Use `test_client.websocket('/ws/')` as a context manager. A `WebsocketResponseError` is raised if the route returns a response.

## Mixed Routes
"Quart allows for a route to be defined both as for websockets and for http requests" on the same path.

## Not Covered
The documentation does not mention broadcasting to multiple clients or comparisons to Socket.IO.