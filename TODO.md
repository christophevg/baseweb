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
| task-3.1: Core migration | task-1.x, task-2.x | Complete |
| task-3.2: Remove Flask-RESTful | task-2.x Resource migration | Complete |
| task-3.3: WebSocket migration | task-3.1: Re-enable SocketIO | Complete |
| task-3.4: Frontend verification | Frontend tests | Complete |
| task-3.5: Vue 3 vendor files | Validate: app loads | Complete |
| task-3.6: Vue 3 app init | Validate: navigation works | Complete |
| task-3.7: Vue 3 simple components | Validate: pages load | Complete |
| task-3.8: Vue 3 navigation | Validate: drawer works | Complete |
| task-3.9: Vue 3 form generator | Validate: forms submit | Complete |
| task-3.10: Vue 3 CollectionView | Validate: CRUD works | Complete |
| task-3.11: Vue 3 charts/notifications | Validate: charts/notifications | Pending |
| task-3.12: Vue 3 integration | Full test suite | Pending |

---

## Unsorted

### part of modernization/migration to async

- [x] **add baseweb:develop skill** (2026-05-04)
  - Created skills/develop/skill.md
  - Covers backend development (Resources, Socket.IO, authentication)
  - Covers frontend development (Vue components, Vuex, forms)
  - Includes common patterns and debugging tips

- [x] **add baseweb:create skill** (2026-05-04)
  - Created skills/create/skill.md
  - Guides project creation with questions
  - Supports flavors: minimal, standard, full, pwa, api-only
  - Includes file templates for all project types

- [x] **add baseweb:review skill** (2026-05-04)
  - Created skills/review/skill.md
  - Reviews architecture, security, performance, code quality, frontend
  - Provides checklist for common issues
  - Includes severity levels and report template

- [x] **document all skills** (2026-05-04)
  - Created docs/skills.md with overview of all skills
  - Documents create, develop, migrate, review skills
  - Includes usage examples and version compatibility

### new features after modernization

- add support for alternative top-level frameworks
- introduce restful-mongo (../incubator/ideas/pageable-restful-mongo-review)
- decide if baseweb should get a plugin system, making baseweb simply the pure core package, adding more functionality (e.g. OAuth, restful-mongo,...) as package plugins
- **optimize vendor bundle** (after Vue 3 migration complete and all apps migrated)
  - Create bundled/minified vendor.js from individual files
  - Enable tree-shaking for Vuetify components
  - Measure and document size reduction
  - Keep non-bundled approach as fallback option

## Backlog

### Phase 2: Architecture Decision

### Phase 3: Flask to Quart Migration

- [x] **Update end-user documentation (docs/)** (2026-05-04)
  - Updated getting-started.md: eventlet → uvicorn, Flask → Quart
  - Updated building-your-first-baseweb-app.md: async patterns, Resource, Socket.IO
  - Updated adding-security.md: async handlers, Socket.IO authentication
  - All code examples now use Quart/async patterns

- [x] **task-3.5: Vue 3 + Vuetify 3 Migration - Vendor Files** (2026-05-04)
  - Downloaded Vue 3.5.33 global build (160KB, was 424KB)
  - Downloaded Vue Router 4.6.4 global build (27KB, was 64KB)
  - Downloaded Vuex 4.1.0 global build (15KB, was 25KB)
  - Downloaded Vuetify 3.12.5 JS (557KB, was 1.0MB)
  - Downloaded Vuetify 3.12.5 CSS (494KB, was 210KB)
  - Downloaded Socket.IO Client 4.8.3 (46KB)
  - Downloaded vue-multiselect 3.5.0 (21KB, was 42KB)
  - Created backups in vendor/js.backup/ and vendor/css.backup/
  - Kept vue-chartjs (no v4 UMD build), vue-form-generator, vue-notification (replaced later)
  - Acceptance: All vendor files downloaded and verified
  - Summary: analysis/ux-vue3-migration.md, analysis/vuetify-4-evaluation.md

- [x] **task-3.6: Vue 3 + Vuetify 3 Migration - App Initialization** (2026-05-04)
  - Updated main.html with Vue 3 + Vuetify 3 initialization pattern
  - Added compatibility shims for Vue 2-style global registration (Vue.component, Vue.filter, Vue.use)
  - Updated app.js: `new Vue()` -> `Vue.createApp()`
  - Updated router.js: `new VueRouter()` -> `VueRouter.createRouter()`
  - Updated store.js: `new Vuex.Store()` -> `Vuex.createStore()`
  - Updated NavigationDrawer.js: `router.addRoutes()` -> `router.addRoute()`
  - Acceptance: App initializes, routes work, store works
  - Requires: task-3.5 (vendor files updated)
  - Validate: baseweb-demo navigation works
  - Notes:
    - Vue 3 filters removed - compatibility shim stores filters in $filters global property
    - Templates using filter syntax need updating in task-3.7+
    - Vuetify 2 component names (v-list-tile) need updating to Vuetify 3 names (v-list-item) in task-3.7+

- [x] **task-3.7: Vue 3 + Vuetify 3 Migration - Simple Components** (2026-05-04)
  - Page.js: No changes needed (no Vuetify dependencies)
  - PageWithBanner.js: `dismissible` → `closable` (v-alert Vuetify 3)
  - PageWithStatus.js: `top` → `location="top"`, `flat` → `variant="flat"`
  - ProcessDiagram.js: No changes needed (v-card compatible)
  - common.js: Filter registration works via compatibility shim
  - Acceptance: All simple components render correctly, 144 tests pass
  - Requires: task-3.6 (app initialization)
  - Validate: baseweb-demo pages load

- [x] **task-3.8: Vue 3 + Vuetify 3 Migration - Navigation Component** (2026-05-04)
  - Replaced `v-list-tile` → `v-list-item` (and all variants)
  - Updated `v-list-group` slot: `slot="activator"` → `v-slot:activator="{ props }"`
  - Updated `v-navigation-drawer`: `:value` → `:model-value`
  - Acceptance: Navigation drawer works correctly, 144 tests pass
  - Requires: task-3.7 (simple components)
  - Validate: baseweb-demo navigation drawer works

- [x] **task-3.9: Vue 3 + Vuetify 3 Migration - Form Generator Replacement** (2026-05-04)
  - Created VuetifyFormGenerator component
  - Parses existing vue-form-generator schema format (backward compatible)
  - Renders Vuetify 3 form components dynamically
  - Supported field types: input, text, textarea, select, checkbox, radio, switch, password, number, email, date, url, tel, range, color
  - Supported schema features: label, model, type, inputType, placeholder, hint, required, validator, values, default, disabled, readonly, min, max, step, maxlength, counter, clearable, prependIcon, appendIcon, rows, autoGrow, multiple, visible, attrs, styleClasses
  - Two-way binding via v-model
  - Validation with error messages
  - Hint and counter support
  - Group layout support (schema.groups)
  - Acceptance: Forms work with existing schemas
  - Requires: task-3.8 (navigation)
  - Validate: baseweb-demo forms submit correctly

- [x] **task-3.10: Vue 3 + Vuetify 3 Migration - CollectionView Component** (2026-05-04)
  - Updated v-data-table API:
    - `:pagination.sync` -> `v-model:options`
    - `:total-items` -> `:items-length`
    - Slot syntax: `slot="items" slot-scope="row"` -> `v-slot:item="{ item }"`
    - Pagination: `rowsPerPage` -> `itemsPerPage`
    - Sort: array of objects `{ key, order }` instead of string + boolean
  - Replaced jQuery AJAX with fetch API:
    - Removed jQuery dependency from search() and do_delete()
    - Using native fetch() with async/await
    - Proper error handling with try/catch
  - Replaced vue-notification with Vuetify snackbar:
    - Created store.js with notification module
    - Created NotificationSnackbar component
    - Updated CollectionView to use store.commit('notify_*')
    - Template still uses <notifications> for backward compatibility
  - Integrated VuetifyFormGenerator:
    - Already registered as vue-form-generator component
    - No changes needed, works with existing schema
  - Updated Vuetify 3 button props:
    - `flat` -> `variant="text"`
    - `icon` stays the same
  - Updated v-pagination:
    - `circle` -> `rounded="circle"`
    - `@input` -> `@update:modelValue`
  - Updated v-text-field:
    - `append-icon` -> `append-inner-icon`
    - Added `@click:append-inner` and `@keyup.enter` for search
  - Updated typography classes:
    - `headline` -> `text-h5`
    - `text-xs-center` -> `text-center`
  - Created files:
    - /src/baseweb/static/js/store.js (Vuex store with notification module)
    - /src/baseweb/static/js/components/NotificationSnackbar.js
  - Acceptance: Data tables work, CRUD operations work
  - Requires: task-3.9 (form generator)
  - Validate: baseweb-demo CollectionView works

- [ ] **task-3.11: Vue 3 + Vuetify 3 Migration - Charts and Notifications**
  - Update LineChart.js for vue-chartjs v4
  - Replace vue-notification with Vuetify snackbar (DONE in task-3.10)
  - Update notification calls throughout components (DONE in task-3.10)
  - Test charts render correctly
  - Test notifications appear correctly
  - Acceptance: Charts render, notifications work
  - Requires: task-3.10 (CollectionView)
  - Validate: baseweb-demo charts and notifications work
  - Validate: baseweb-demo charts and notifications work

- [ ] **task-3.12: Vue 3 + Vuetify 3 Migration - Integration Testing**
  - Run full integration test suite
  - Test all existing functionality against backend
  - Test WebSocket connections
  - Test authentication flows
  - Visual comparison with Vue 2 version
  - Benchmark performance vs Vue 2
  - Document any remaining issues
  - Acceptance: All features work, no regressions
  - Requires: task-3.11 (all components)
  - Validate: baseweb-demo full test suite passes

### Phase 5: Post-modernization further feature development

- [ ] **task-5.1: Unify special page components**
  - Create unified `Page` component with configurable props/slots
  - Support: with_banner, with_status, with_navigation
  - Deprecate existing Page, PageWithBanner, PageWithStatus
  - Create migration guide
  - Add tests for new component
  - Acceptance: Unified component works, old components deprecated

## Done

- [x] **Resource instantiation flexibility** (2026-05-01)
  - Allow passing class (instantiated per request) or instance (reused)
  - Support dependency injection via instance pattern
  - Add 7 new tests for instantiation patterns
  - Acceptance: All 144 tests pass

- [x] **Migrate skill as baseweb plugin** (2026-05-01)
  - Created .claude_plugin/plugin.json for Claude Code integration
  - Created skills/migrate/skill.md with comprehensive migration guide
  - Covers Flask→Quart migration for baseweb apps

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

- [x] **task-3.2: Remove Flask-RESTful** (2026-04-30)
  - Removed Flask-RESTful dependency from pyproject.toml
  - Removed `import flask_restful` from __init__.py
  - Removed `self.api = flask_restful.Api(self)` attribute
  - Enabled 13 previously skipped tests
  - Updated migration guide for native Quart routes
  - Acceptance: All tests pass (65 tests, 0 skipped)
  - Summary: reporting/task-3.2/summary.md

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
