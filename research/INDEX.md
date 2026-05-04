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

---

### Vuetify Build Requirements

**Folder**: `2026-05-04-vuetify-build-requirements/`
**Date**: 2026-05-04
**Status**: Complete

**Summary**: Research into Vuetify 3 compatibility with baseweb's no-build architecture, evaluating CDN usage, tree shaking limitations, and alternatives like PrimeVue.

**Key Findings**:
- Vuetify 3 CAN be used via CDN without build tools
- CDN loads entire library (~500KB+), no tree shaking
- Vuetify 1.5 and 2.x are NOT compatible with Vue 3
- PrimeVue offers per-component CDN loading (better for no-build)
- Minimal Vite build can enable tree shaking while keeping plain JS components

**Sources**: 6 searches, 1 fetched

**Keywords**: vuetify, vue3, cdn, build-system, tree-shaking, primevue, vite, bundler

---

### Vuetify 4 Evaluation for Baseweb Migration

**Folder**: `2026-05-04-vuetify-4-evaluation/`
**Date**: 2026-05-04
**Status**: Complete

**Summary**: Evaluation of Vuetify 4 for baseweb migration from Vuetify 1.5/Vue 2, comparing Vuetify 3 vs 4, CDN bundle sizes, and migration paths.

**Key Findings**:
- Vuetify 4 released February 23, 2026 (requires Vue 3)
- No direct migration from Vuetify 1.5 -> must go through Vuetify 2 -> 3 -> 4
- Vuetify 3 CDN: ~844 KB, Vuetify 4 CDN: ~1,016 KB (both include all components)
- Major Vuetify 4 changes: CSS cascade layers, MD3 support, grid system overhaul
- Recommend migrating to Vuetify 3 first (smaller, more mature), then to Vuetify 4

**Sources**: 4 searches, 4 fetched

**Keywords**: vuetify, vuetify4, migration, vue3, cdn, bundle-size, material-design