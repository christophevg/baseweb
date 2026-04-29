# TODO

## Backlog

### Phase 2: Architecture Decision

- [ ] **task-2.1: Decide on version strategy**
  - Document decision: single version (major bump) vs dual packages
  - Create migration guide for existing users
  - Prepare changelog entry
  - Acceptance: Decision documented in analysis/functional.md

- [ ] **task-2.2: Coordinate with hosted-quarts**
  - Document dependency matrix between baseweb and hosted-quarts
  - Align migration timeline
  - Identify shared code/dependencies
  - Acceptance: Coordination plan documented

### Phase 3: Flask to Quart Migration

- [ ] **task-3.1: Migrate core Baseweb class**
  - Change `from flask import Flask` to `from quart import Quart`
  - Convert all route handlers to async functions
  - Update `render_template()` calls with `await`
  - Update `request.get_json()` calls with `await`
  - Update `send_from_directory()` calls with `await`
  - Update authentication decorator for async
  - Acceptance: All tests pass, functionality preserved

- [ ] **task-3.2: Migrate Flask-RESTful**
  - Add `quart-flask-patch` or equivalent
  - Test API endpoints with Quart
  - Document any required API changes
  - Acceptance: All API endpoints work, tests pass

- [ ] **task-3.3: Migrate WebSocket support**
  - Evaluate WebSocket usage patterns
  - Choose: Flask-SocketIO (threaded) vs Quart native vs python-socketio
  - Implement chosen solution
  - Create WebSocket integration tests
  - Acceptance: WebSocket functionality works, tests pass

- [ ] **task-3.4: Frontend integration verification**
  - Verify frontend works without changes
  - Test Socket.IO client compatibility
  - Test Vue components with async API responses
  - Document any required frontend changes
  - Acceptance: Frontend works correctly

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