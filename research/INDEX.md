# Research Index

A collection of research findings organized by topic.

---

### Quart WebSocket Implementation Options

**Folder**: `2026-04-30-quart-websocket-options/`
**Date**: 2026-04-30
**Status**: Complete

**Summary**: Research into WebSocket solutions for baseweb after Flask-to-Quart migration, comparing python-socketio with Quart native WebSocket.

**Key Findings**:
- python-socketio ASGI mode recommended for maintaining Socket.IO frontend compatibility
- Integration uses `socketio.ASGIApp(sio, app)` wrapper pattern
- Event handlers become async with `sid` as first parameter
- Frontend requires no changes
- Running requires using wrapped ASGI app (`server._asgi_app`)

**Sources**: 4 sources (4 fetched, 4 searches)

**Keywords**: websocket, socketio, quart, asgi, migration, flask-socketio, python-socketio