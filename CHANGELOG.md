# Changelog

All notable changes to Baseweb will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.5.1] - 2026-05-13

### Fixed

- **Package distribution**: Corrected hatch build configuration to include source files
- **Security**: Added urllib3>=2.7.0 constraint for security advisory

## [0.5.0] - 2026-05-13

### Added

- **Vue 3 + Vuetify 3 Support**: Complete frontend migration
  - Vue 3.5 with Composition API
  - Vuetify 3.12 components
  - Vue Router 4.6
  - Vuex 4.1
  - Updated vendor files (smaller bundle sizes)

- **Baseweb Skills**: Development helper skills
  - `baseweb:create` - Project scaffolding
  - `baseweb:develop` - Development patterns guide
  - `baseweb:migrate` - Flask to Quart migration
  - `baseweb:review` - Code review checklist

### Changed

- **Python 3.10+ Required**: Minimum Python version is now 3.10

- **Flask → Quart Migration**: Full async support
  - All route handlers must be async functions
  - `render_template()` must be awaited
  - `request.get_json()` must be awaited
  - `send_from_directory()` must be awaited

- **Resource Class**: Now fully async
  - All HTTP methods (`get`, `post`, `put`, `delete`, etc.) are async
  - Inherits from Quart patterns

- **WebSocket**: python-socketio (ASGI mode) replaces Flask-SocketIO

- **NavigationDrawer**: Updated for Vuetify 3

### Removed

- **Flask-RESTful**: The `server.api` attribute is no longer available
  - Migrate to native Quart routes with `@server.route()` decorator
  - Use the `Resource` class from `baseweb` instead

### Migration Guide

See [Migration Guide](docs/migration-guide.md) for detailed migration instructions.

## [0.4.3] - 2025-04-XX

### Fixed

- Various bug fixes and stability improvements

[0.5.0]: https://github.com/christophevg/baseweb/compare/v0.4.3...v0.5.0
[0.4.3]: https://github.com/christophevg/baseweb/compare/v0.4.2...v0.4.3