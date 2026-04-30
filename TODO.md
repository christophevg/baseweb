# TODO

## Backlog

### Phase 2: Architecture Decision



### Phase 3: Flask to Quart Migration

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