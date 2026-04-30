# Changelog

All notable changes to Baseweb will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - Unreleased

### Breaking Changes

- **Flask → Quart Migration**: Baseweb now uses Quart instead of Flask for async support
  - All route handlers must be async functions
  - `render_template()` must be awaited
  - `request.get_json()` must be awaited
  - `send_from_directory()` must be awaited
- **Python 3.11+ Required**: Minimum Python version is now 3.11
- **WebSocket**: Flask-SocketIO replaced with python-socketio (ASGI mode)
- **Flask-RESTful Removed**: The `server.api` attribute is no longer available
  - Migrate to native Quart routes with `@server.route()` decorator
  - Consider `quart-schema` for API validation

### Migration Guide

See [Migration Guide](docs/migration-guide.md) for detailed migration instructions.

[1.0.0]: https://github.com/christophevg/baseweb/compare/v0.4.3...v1.0.0