# Baseweb Functional Analysis

**Created:** 2026-04-29
**Status:** Active
**Version:** 0.5.1 (current) -> 1.0.0 (target)

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

### Phase 5: Post-modernization Further Feature Development (COMPLETE)

#### 5.1 Create Minimal Hello World Example

**Rationale:** A minimal example application demonstrates core baseweb functionality and serves as validation for the Quart migration approach.

**Implementation:**
- Created `examples/hello-world/` with minimal baseweb application
- Uses `uv` for dependency management
- Single page, no authentication, no REST API, no WebSocket
- Validates Quart async patterns work correctly

**Completion Date:** 2026-05-04

**Acceptance Criteria:**
- [x] Minimal Hello World example created
- [x] Uses `uv` for dependency management
- [x] Single page, no authentication, no REST API, no WebSocket
- [x] App starts, HTML served, component registered, Vue 3 initializes

**Dependencies:** Phase 3 (Quart migration)

#### 5.2 Unify Special Page Components

**Rationale:** Multiple page components exist (Page, PageWithBanner, PageWithStatus) with overlapping functionality. A unified component with properties would reduce code duplication and improve maintainability.

**Implementation:**
- Created unified `Page` component with props: `banner`, `status`, `statusTimeout`
- Added slots: default, header, footer
- Registered namespaced Vuex store module `page` with `banner` and `status` state
- **Breaking change**: Removed `PageWithBanner.js` and `PageWithStatus.js`
- Migration: `<PageWithBanner>` → `<Page banner>`, `<PageWithStatus>` → `<Page status>`

**Completion Date:** 2026-05-18

**Acceptance Criteria:**
- [x] Unified `Page` component created
- [x] Support for banner, status props (navigation deferred by design)
- [x] Existing components removed (breaking change, migration guide provided)
- [x] Migration guide for existing usage
- [x] Tests for new component
- [x] Full-page layouts deferred (R78)

**Dependencies:** Phase 3 (Quart migration)

### Phase 6: PWA and Push Notifications (COMPLETE)

#### 6.1 PWA Manifest and Service Worker Foundation

**Rationale:** Progressive Web App support enables offline functionality and mobile app-like experience, critical for modern web applications.

**Implementation:**
- Enhanced manifest.json with 180x180 icon, description, scope fields
- Added iOS Safari meta tags (apple-mobile-web-app-capable, status-bar-style, title, touch-icon)
- Created Service Worker (sw.js) with cache-first strategy for static assets
- Added Service Worker route with correct headers (Service-Worker-Allowed: /)
- Registered Service Worker on window.load when APP_STYLE=pwa
- Generated 9 placeholder icons (72x72 to 512x512)
- Added offline UX indicator (isOnline state, offline badge in app bar)
- Added python-dotenv to hello-world example for .env file loading

**Completion Date:** 2026-05-19

**Acceptance Criteria:**
- [x] PWA manifest enhanced for iOS compatibility
- [x] Service Worker implementation for offline support
- [x] iOS Safari standalone mode support (iOS 16.4+)
- [x] Icon generation and proper paths

**Dependencies:** Phase 5

#### 6.2 Push Notification Backend Infrastructure

**Rationale:** Push notifications enable real-time user engagement, essential for modern web applications.

**Implementation:**
- Implemented VAPID key generation and management (src/baseweb/vapid.py)
- Created push subscription storage with CRUD operations
- Created GET /api/vapid-public-key endpoint (unauthenticated)
- Created POST/GET/DELETE /api/push-subscriptions endpoints (authenticated)
- Created POST /api/push-notifications endpoint (admin only)
- Added rate limiting (10/hour, 50/day per user, 100/min global)
- Added input validation (endpoint URL, keys, payload)
- Added known push service validation (FCM, Mozilla, Apple)
- iOS Safari compatible (VAPID claims with subject and audience)

**Completion Date:** 2026-05-19

**Acceptance Criteria:**
- [x] Backend VAPID key generation and management
- [x] Push subscription storage and retrieval
- [x] Push notification sending functionality
- [x] Security features (VAPID private key from env, subscription validation)

**Dependencies:** 6.1

#### 6.3 Push Notification Frontend Integration

**Rationale:** Frontend integration completes the push notification workflow for end users.

**Implementation:**
- Implemented notification UI component (PushNotificationSettings.js)
- Added standalone PWA mode detection for iOS Safari
- Added HTTPS/localhost security check for Push API
- Pre-fetched VAPID key on page load for Safari user gesture requirement
- Implemented subscribe/unsubscribe flow with permission handling
- Synced subscription state with backend via POST/DELETE endpoints
- Added iOS-specific guidance for non-PWA users
- Service Worker already handles push events (from task-6.1)
- Created testing documentation for ngrok + real iPhone testing

**Completion Date:** 2026-05-20

**Acceptance Criteria:**
- [x] Push API integration with VAPID key support
- [x] Notifications API integration
- [x] User permission prompt triggered by user action
- [x] iOS Safari compatibility documented

**Dependencies:** 6.2

#### 6.4 PWA and Push Notifications Documentation

**Rationale:** Users need comprehensive documentation for PWA installation and push notification setup.

**Implementation:**
- Created comprehensive documentation in docs/push-notifications.md
- Documented iOS Safari PWA installation workflow with step-by-step guide
- Documented developer setup (VAPID keys, API endpoints, integration)
- Documented user-facing permission flow
- Created troubleshooting guide with iOS-specific issues
- Included compatibility matrix (iOS 16.4+ Safari only)

**Completion Date:** 2026-06-07

**Acceptance Criteria:**
- [x] PWA installation workflow documented
- [x] Push notification setup documented
- [x] iOS-specific requirements documented
- [x] Troubleshooting guide included

**Dependencies:** 6.3

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

| Phase | Status | Duration | Completion |
|-------|--------|----------|------------|
| Phase 1: Project Cleanup | COMPLETE | 1-2 weeks | 2026-04-29 |
| Phase 2: Architecture Decision | COMPLETE | 1-2 days | 2026-04-30 |
| Phase 3: Quart Migration | COMPLETE | 2-4 weeks | 2026-05-04 |
| Phase 4: hosted-quarts Coordination | COMPLETE | 1 week | 2026-04-30 |
| Phase 5: Post-modernization | COMPLETE | 1 week | 2026-05-18 |
| Phase 6: PWA and Push Notifications | COMPLETE | 1-2 weeks | 2026-06-07 |
| Phase 7: CLI and Configuration | COMPLETE | 1-2 weeks | 2026-06-07 |
| Phase 8: Plugin System Architecture | PLANNED | 2-3 weeks | - |
| Phase 9: Plugin Implementations | PLANNED | 2-3 weeks | - |
| Phase 10: Performance Optimization | PLANNED | 1-2 weeks | - |

**Completed Duration:** ~8 weeks
**Remaining Duration:** 5-8 weeks

---

---

### Phase 7: CLI and Configuration System (COMPLETE)

#### 7.1 Configuration Infrastructure

**Rationale:** Baseweb relied solely on environment variables for configuration. A modern configuration system using TOML files with Clevis provides better developer experience and aligns with Python packaging standards.

**Implementation:**
- Created `src/baseweb/config.py` with BasewebConfig dataclass
- Implemented TOML configuration file loading via Clevis
- Supported layered configuration (defaults < user-level < project-level < env vars < CLI args)
- Integrated with Baseweb class via constructor parameter
- **Breaking change**: Removed settings dict parameter, now requires BasewebConfig

**Completion Date:** 2026-06-07

**Acceptance Criteria:**
- [x] Configuration loads from TOML files (project and user level)
- [x] Environment variables override TOML configuration (APP_*, GUNICORN_*)
- [x] CLI arguments override environment variables
- [x] `Baseweb(config)` accepts BasewebConfig directly (no .from_config() method)
- [x] Clear error messages for all failure cases

**Dependencies:** Phase 5 (Hello World example validates approach)

#### 7.2 CLI Commands

**Rationale:** A CLI entry point allows users to run baseweb applications without writing Python code, enabling `baseweb serve` workflows and improving developer experience.

**Implementation:**
- Created `src/baseweb/__main__.py` with Clevis command pattern
- Added `baseweb init` command to create default baseweb.toml
- Added `baseweb serve` command to run applications via Gunicorn
- Added `baseweb config` command to display configuration (table or TOML format)
- Added `baseweb version` command
- Added `baseweb check` command to validate configuration without running
- Integrated with Gunicorn via StandaloneApplication wrapper
- Support CLI argument overrides for all configuration fields

**Completion Date:** 2026-06-07

**Acceptance Criteria:**
- [x] `baseweb init` creates baseweb.toml with sensible defaults
- [x] `baseweb serve` runs application from TOML config
- [x] `baseweb config` displays current configuration
- [x] `baseweb version` displays version
- [x] `baseweb check` validates configuration without running
- [x] CLI arguments override configuration (via Clevis)
- [x] Error messages are clear and actionable

**Dependencies:** 7.1 (configuration infrastructure)

#### 7.3 Documentation

**Rationale:** Users need clear documentation for the new configuration system and CLI commands.

**Implementation:**
- Created `docs/configuration.md` with comprehensive configuration reference
- Created `docs/cli.md` with complete CLI command reference
- Updated README.md with Quick Start section
- Documented all configuration options with examples
- Documented configuration priority order
- Documented environment variable mapping
- Documented app-specific configuration via register_app_config()

**Completion Date:** 2026-06-07

**Acceptance Criteria:**
- [x] All configuration options documented
- [x] CLI commands documented with examples
- [x] Migration guide from environment variables to TOML
- [x] Troubleshooting section

**Dependencies:** 7.2 (CLI commands)

---

## Risk Assessment

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