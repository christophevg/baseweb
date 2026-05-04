# Baseweb Functional Analysis

**Created:** 2026-04-29
**Status:** Draft
**Version:** 0.4.3 (current) -> 1.0.0 (target)

---

## Project Overview

Baseweb is a Pythonic base framework for building interactive web applications. It provides an integrated stack combining Flask (backend), Vue.js/Vuetify (frontend), Flask-RESTful (API), and Flask-SocketIO (real-time communication).

### Core Value Proposition

Baseweb reduces boilerplate for web application development by providing:
1. Pre-configured Flask application with sensible defaults
2. Integrated Vue 2 + Vuetify 2 frontend stack
3. Component registration and routing system
4. Authentication/authorization hooks
5. WebSocket support via Socket.IO
6. PWA (Progressive Web App) support

### Current Architecture

```
baseweb/
├── __init__.py          # Main Baseweb class (Flask extension)
├── util.py              # Utility functions
├── templates/           # Jinja2 templates (main.html, store.js, manifest.json)
└── static/              # Frontend assets
    ├── css/             # Stylesheets
    ├── js/              # Vue components and app logic
    └── vendor/          # Third-party libraries
```

### Technology Stack (Post-Migration)

| Layer | Technology |
|-------|------------|
| Backend Framework | Quart (async) |
| REST API | Native Quart routes with Resource class |
| WebSocket | python-socketio with ASGI |
| Frontend | Vue 3 + Vuetify 3 |
| Python | 3.10+ |

---

## Functional Requirements

### Phase 1: Project Cleanup

#### 1.1 Remove pypi-template Support

**Rationale:** The `.pypi-template` file was used for project scaffolding but is no longer needed. The project should have a clean, self-contained structure.

**Acceptance Criteria:**
- [ ] `.pypi-template` file is removed
- [ ] `setup.py` is reviewed and simplified if needed
- [ ] All Makefile targets that reference pypi-template are cleaned up
- [ ] Documentation reflects the new structure
- [ ] Build and publish process still works

**Dependencies:** None

#### 1.2 Setup Clean Project Structure with Testing Support

**Rationale:** The project currently has no actual tests (only a test configuration in tox.ini). A proper test infrastructure is essential for safe refactoring and ongoing maintenance.

**Acceptance Criteria:**
- [ ] `tests/` directory exists with proper structure
- [ ] Unit tests exist for core Baseweb class functionality:
  - Application initialization with defaults
  - Configuration loading from environment
  - Component registration
  - Stylesheet registration
  - Script registration
  - Route registration
  - Authentication hooks
- [ ] Integration tests exist for:
  - Basic route handling
  - Template rendering
  - Static file serving
- [ ] `pytest` configuration is complete (pyproject.toml or pytest.ini)
- [ ] Coverage reporting is configured
- [ ] `make test` runs all tests successfully
- [ ] Minimum 80% code coverage achieved

**Dependencies:** None

#### 1.3 Bring Project Up to Standards

**Rationale:** The codebase should follow current best practices for Python packaging and project organization.

**Acceptance Criteria:**
- [ ] Code passes `ruff` linting without errors
- [ ] Type hints are added where appropriate
- [ ] Docstrings are present for all public modules, classes, and functions
- [ ] `pyproject.toml` exists with full project metadata (migrate from setup.py if needed)
- [ ] `.gitignore` is comprehensive
- [ ] `MANIFEST.in` includes all necessary files for distribution
- [ ] GitHub Actions CI/CD is configured and passing

**Dependencies:** 1.2 (testing infrastructure)

---

### Phase 2: Architecture Decision

#### 2.1 Version Strategy Decision

**Rationale:** A critical decision must be made before starting the Flask to Quart migration. This affects how users consume the package and the migration path.

**Options:**

| Option | Pros | Cons |
|--------|------|------|
| **A: Single version (major bump)** | Clean codebase, no maintenance burden, clear async-first direction | Breaking change for users, no gradual migration path |
| **B: Dual packages** | Backward compatibility, gradual migration | Double maintenance effort, code duplication, user confusion |
| **C: Single codebase with compatibility layer** | One codebase to maintain, some backward compatibility | Complex conditional logic, technical debt |

**Recommendation:** Option A - Single version with major bump to 1.0.0

**Acceptance Criteria:**
- [ ] Decision documented with rationale
- [ ] Migration guide created for existing users
- [ ] Changelog entry prepared
- [ ] Any dual-version code paths are planned for removal

**Dependencies:** None (can proceed in parallel with Phase 1)

---

### Phase 3: Flask to Quart Migration

#### 3.1 Core Baseweb Class Migration

**Rationale:** The core `Baseweb` class needs to be converted to async to support modern Python web application patterns.

**Scope:**
- Convert `Baseweb` class from Flask to Quart
- Update all route handlers to async
- Update template rendering to use async patterns
- Update request handling for async

**Acceptance Criteria:**
- [ ] `from flask import Flask` changed to `from quart import Quart`
- [ ] All route handlers are async functions
- [ ] `render_template()` calls use `await`
- [ ] `request.get_json()` calls use `await`
- [ ] `send_from_directory()` calls use `await`
- [ ] Authentication decorator works with async handlers
- [ ] All existing functionality preserved
- [ ] All tests pass

**Dependencies:** 1.2 (testing), 2.1 (decision)

#### 3.2 Flask-RESTful Migration

**Rationale:** The project uses Flask-RESTful for API endpoints. Quart requires a different approach.

**Scope:**
- Add `quart-flask-patch` or equivalent
- Test API functionality with Quart
- Document any API changes required

**Acceptance Criteria:**
- [ ] API endpoints work with Quart
- [ ] Resource classes function correctly
- [ ] All HTTP methods (GET, POST, PUT, DELETE, PATCH) work
- [ ] Request parsing works with async
- [ ] Response formatting is preserved
- [ ] Integration tests pass

**Dependencies:** 3.1

#### 3.3 WebSocket Migration

**Rationale:** Flask-SocketIO does not support async handlers. A decision on WebSocket implementation is needed.

**Options:**

| Option | Description | Async Support | Effort |
|--------|-------------|---------------|--------|
| A | Keep Flask-SocketIO (threaded mode) | No | Low |
| B | Quart native WebSocket | Yes | Medium |
| C | python-socketio with Quart | Yes | Medium |

**Recommendation:** Evaluate based on usage patterns. If simple real-time needs, use Quart native WebSocket.

**Acceptance Criteria:**
- [ ] WebSocket functionality is preserved or improved
- [ ] Connection handling works
- [ ] Event handlers are async (if Option B or C)
- [ ] Socket.IO client compatibility maintained (if Option C)
- [ ] Integration tests for WebSocket functionality pass

**Dependencies:** 3.1

#### 3.4 Frontend Integration Updates

**Rationale:** The frontend JavaScript needs to work seamlessly with the new backend.

**Scope:**
- Update any hardcoded URLs if needed
- Ensure Socket.IO client works with new backend
- Test Vue components with async API responses

**Acceptance Criteria:**
- [ ] Frontend works without changes (ideal)
- [ ] Or minimal documented changes required
- [ ] All Vue components render correctly
- [ ] WebSocket connections established
- [ ] API calls return expected data

**Dependencies:** 3.1, 3.2, 3.3

---

### Phase 4: Coordination with hosted-quarts

#### 4.1 Coordinate Migration with hosted-quarts

**Rationale:** The hosted-quarts project depends on or relates to baseweb. Migration must be coordinated to avoid breaking dependencies.

**Acceptance Criteria:**
- [ ] Dependency matrix documented
- [ ] Migration timeline aligned with hosted-quarts
- [ ] Breaking changes communicated
- [ ] Integration testing with hosted-quarts performed
- [ ] Shared code/dependencies identified and addressed

**Dependencies:** 2.1 (decision on version strategy)

---

### Phase 5: Component Consolidation (Old Backlog)

#### 5.1 Unify Special Page Components

**Rationale:** Multiple page components exist (Page, PageWithBanner, PageWithStatus) with overlapping functionality. A unified component with properties would reduce code duplication and improve maintainability.

**Scope:**
- Create a unified `Page` component with configurable slots/props
- Support: with_banner, with_status, with_navigation, with_google_login
- Maintain backward compatibility during transition

**Acceptance Criteria:**
- [ ] Unified `Page` component created
- [ ] All existing functionality supported via props/slots
- [ ] Migration guide for existing usage
- [ ] Existing components deprecated (not removed immediately)
- [ ] Tests for new component

**Dependencies:** Phase 3 (Quart migration should not be blocked by this)

---

## Risk Assessment

| Risk | Impact | Likelihood | Mitigation |
|------|--------|------------|------------|
| Breaking changes for existing users | High | Medium | Clear migration guide, major version bump |
| WebSocket incompatibility | High | Medium | Test with Option C (python-socketio) as fallback |
| Test coverage gaps | Medium | High | Prioritize test infrastructure first |
| hosted-quarts integration issues | Medium | Low | Early coordination, integration testing |
| Performance regression | Medium | Low | Benchmark before/after migration |

---

## Success Metrics

1. **Code Quality**
   - All ruff checks pass
   - 80%+ test coverage
   - Type hints on public API

2. **Functionality**
   - All existing features work
   - WebSocket connections stable
   - API responses correct

3. **Migration Path**
   - Clear documentation for users
   - Breaking changes documented
   - Migration time estimate for typical app: < 1 hour

---

## Timeline Estimate

| Phase | Duration | Dependencies |
|-------|----------|--------------|
| Phase 1: Project Cleanup | 1-2 weeks | None |
| Phase 2: Architecture Decision | 1-2 days | None |
| Phase 3: Quart Migration | 2-4 weeks | Phase 1, 2 |
| Phase 4: hosted-quarts Coordination | 1 week | Phase 2 |
| Phase 5: Component Consolidation | 1 week | Phase 3 |

**Total Estimated Duration:** 5-8 weeks

---

## Decisions Made

| Decision | Choice | Rationale |
|----------|--------|-----------|
| **Version strategy** | Single version (major bump to 1.0.0) | Clean codebase, clear async-first direction, no maintenance burden |
| **WebSocket implementation** | Quart native WebSocket (Option B) | Fully async, native integration, clean codebase |
| **hosted-quarts relationship** | Consumer/Hosting platform | hosted-quarts hosts baseweb applications. Migration must be coordinated so hosted-quarts can serve migrated async baseweb apps |

## Remaining Questions

None - all decisions made.

---

## Appendix: Key Files Summary

| File | Purpose | Migration Impact |
|------|---------|------------------|
| `baseweb/__init__.py` | Core Baseweb class | Major - Flask to Quart |
| `baseweb/templates/main.html` | Main HTML template | Minor - async template rendering |
| `baseweb/templates/store.js` | Vuex store template | None |
| `baseweb/static/js/app.js` | Vue app initialization | None |
| `baseweb/static/js/components/CollectionView.js` | Data table component | None - frontend only |