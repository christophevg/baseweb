# TODO

## Coordination with baseweb-demo

The [baseweb-demo](../baseweb-demo) project serves as an end-to-end test case and must be validated after each migration task.

### Workflow

1. **Before starting a task**: Check if baseweb-demo depends on the feature being migrated
2. **During development**: Test against baseweb-demo if applicable
3. **After completing a task**: Run baseweb-demo tests and verify the app runs
4. **Commit together**: Related changes should be committed in both projects

### Task Dependencies

| baseweb Task | baseweb-demo Task | Status |
|--------------|-------------------|--------|
| task-3.1: Core migration | task-1.x, task-2.x | ✅ Complete |
| task-3.2: Remove Flask-RESTful | task-2.x Resource migration | ✅ Complete |
| task-3.3: WebSocket migration | task-3.1: Re-enable SocketIO | ✅ Complete |
| task-3.4: Frontend verification | Frontend tests | ✅ Complete |

---

## Backlog

### Unsorted

- [x] **Resource instantiation flexibility** (2026-05-01)
  - Allow passing class (instantiated per request) or instance (reused)
  - Support dependency injection via instance pattern
  - Add 7 new tests for instantiation patterns
  - Acceptance: All 144 tests pass

- create a migrate skill and expose it as a baseweb plugin
- upgrade frontend to modern Vue+Vuetify

### Phase 2: Architecture Decision



### Phase 3: Flask to Quart Migration

- [x] **task-3.2: Remove Flask-RESTful** (2026-04-30)
  - Removed Flask-RESTful dependency from pyproject.toml
  - Removed `import flask_restful` from __init__.py
  - Removed `self.api = flask_restful.Api(self)` attribute
  - Enabled 13 previously skipped tests
  - Updated migration guide for native Quart routes
  - Acceptance: All tests pass (65 tests, 0 skipped)
  - Summary: reporting/task-3.2/summary.md

- [x] **task-3.3: Migrate WebSocket support** (2026-05-01)
  - Migrated from Flask-SocketIO to python-socketio with ASGI mode
  - Implemented `socketio.AsyncServer(async_mode='asgi')`
  - Created `socketio.ASGIApp(sio, quart_app)` wrapper
  - Updated `authenticated` decorator for SocketIO context
  - Acceptance: WebSocket functionality works with authentication
  - Summary: committed in research/2026-04-30-quart-websocket-options/

- [x] **task-3.4: Frontend integration verification** (2026-05-01)
  - Verified frontend static files served correctly
  - Verified REST API endpoints work with async handlers
  - Verified Socket.IO client initialization and connection
  - Added comprehensive frontend integration tests (13 new tests)
  - Acceptance: All 26 tests pass, frontend works correctly

### Phase 5: Component Consolidation

- [ ] **task-5.1: Unify special page components**
  - Create unified `Page` component with configurable props/slots
  - Support: with_banner, with_status, with_navigation
  - Deprecate existing Page, PageWithBanner, PageWithStatus
  - Create migration guide
  - Add tests for new component
  - Acceptance: Unified component works, old components deprecated

## In Progress

(none)

## Done

- [x] **task-3.4: Frontend integration verification** (2026-05-01)
  - Verified frontend static files served correctly
  - Verified REST API endpoints work with async handlers
  - Verified Socket.IO client initialization and connection
  - Added comprehensive frontend integration tests (13 new tests)
  - Acceptance: All 26 tests pass, frontend works correctly

- [x] **task-3.3: Migrate WebSocket support** (2026-05-01)
  - Migrated from Flask-SocketIO to python-socketio with ASGI mode
  - Implemented `socketio.AsyncServer(async_mode='asgi')`
  - Created `socketio.ASGIApp(sio, quart_app)` wrapper
  - Updated `authenticated` decorator for SocketIO context
  - Acceptance: WebSocket functionality works with authentication

- [x] **task-3.1: Migrate core Baseweb class** (2026-04-30)
  - Changed `from flask import Flask` to `from quart import Quart`
  - Converted all route handlers to async functions
  - Updated `render_template()` calls with `await`
  - Updated `send_from_directory()` calls with `await`
  - Updated authentication decorator for async
  - Added proper MIME types for JS/JSON responses
  - All acceptance criteria met:
    - 52 tests pass
    - 13 tests skipped (Flask-RESTful compatibility - see task-3.2)
    - 82% test coverage
  - Summary: reporting/task-3.1/summary.md

- [x] **task-2.2: Coordinate with hosted-quarts** (2026-04-30)
  - Documented relationship: hosted-quarts serves baseweb as Quart app
  - Confirmed no code dependencies between projects
  - Aligned timeline: parallel development, coordinated production upgrade
  - Created coordination plan: reporting/task-2.2/coordination-plan.md
  - All acceptance criteria met:
    - Dependency matrix documented
    - Migration timeline aligned
    - Shared code/dependencies identified (none)

- [x] **task-2.1: Decide on version strategy** (2026-04-30)
  - Documented decision: single version with major bump to 1.0.0
  - Created migration guide (docs/migration-guide.md)
  - Created CHANGELOG.md with v1.0.0 entry
  - Updated README.md with references to migration guide
  - All acceptance criteria met:
    - Decision documented with rationale
    - Migration guide created for existing users
    - Changelog entry prepared
  - Summary: reporting/task-2.1/summary.md

- [x] **task-0.2: Complete uv migration and fix CI** (2026-04-30)
  - Removed old pyenv management targets from Makefile
  - Updated GitHub Actions workflow to use uv
  - Applied python-project skill best practices
  - Updated Python version support to 3.10, 3.11, 3.12
  - Installed uv system-wide via Homebrew
  - Created .python-version (pinned to 3.12)
  - Generated uv.lock for reproducible builds
  - Added .venv to .gitignore, removed .python-version from gitignore
  - All acceptance criteria met:
    - `uv sync` works
    - `uv run pytest` passes
    - `uv run ruff check src tests` passes
    - Makefile is clean

- [x] **task-0.0: Migrate to standard Python project setup** (2026-04-29)

- [x] **task-0.0: Migrate to standard Python project setup** (2026-04-29)
  - Migrated from setup.py to pyproject.toml with hatchling
  - Moved to src-layout (src/baseweb/)
  - Created py.typed marker file
  - Moved all tool config to pyproject.toml (ruff, pytest, coverage)
  - Removed setup.py, tox.ini, .pypi-template, old requirements files
  - Updated Makefile for new build commands
  - All acceptance criteria met:
    - `pip install -e ".[dev]"` works
    - `make test` passes
    - `make lint` passes
    - `python -m build` succeeds
  - Summary: reporting/task-0.0/development-summary.md

- [x] **task-0.1: Functional analysis**
  - Created analysis/functional.md
  - Documented project overview and technology stack
  - Defined functional requirements for all phases
  - Created risk assessment and success metrics
  - Identified open questions (all answered)
