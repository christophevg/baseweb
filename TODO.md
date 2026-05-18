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
| task-3.11: Vue 3 charts/notifications | Validate: charts/notifications | Complete |
| task-3.12: Vue 3 integration | Full test suite | Complete |

---

## Backlog

### Phase 5: Post-modernization Further Feature Development

### Phase 6: PWA and Push Notifications

- [ ] **task-6.1: PWA manifest and service worker foundation**
  - Enhance PWA manifest for iOS Safari compatibility
  - Implement Service Worker for offline support
  - Configure app manifest (name, icons, display mode)
  - Test PWA installation on iOS Safari (iOS 16.4+)
  - **Satisfies**: R79, R80, R83
  - **Acceptance**: PWA installs on iOS Home Screen, works offline
  - **Requires**: Phase 5 complete

- [ ] **task-6.2: Push notification backend infrastructure**
  - Implement VAPID key generation and management
  - Create push subscription storage endpoint
  - Create push subscription retrieval endpoint
  - Create push notification sending endpoint
  - **Satisfies**: R85, R86, R87, NFR3
  - **Acceptance**: Backend can generate VAPID keys, store subscriptions, send push notifications
  - **Requires**: task-6.1

- [ ] **task-6.3: Push notification frontend integration**
  - Integrate Push API with Service Worker
  - Integrate Notifications API
  - Implement permission prompt triggered by user action
  - Handle push events in Service Worker
  - **Satisfies**: R81, R82, R84
  - **Acceptance**: Users can subscribe to push notifications, receive notifications in standalone mode
  - **Requires**: task-6.2

- [ ] **task-6.4: PWA and push notifications documentation**
  - Document iOS Safari PWA installation workflow
  - Document push notification setup for developers
  - Document user-facing permission flow
  - Create troubleshooting guide
  - **Satisfies**: R88
  - **Acceptance**: Documentation covers installation, subscription, and troubleshooting
  - **Requires**: task-6.3

### Phase 7: Plugin System Architecture

- [ ] **task-7.1: Design plugin namespace system**
  - Design plugin discovery mechanism
  - Define plugin lifecycle hooks (load, initialize, configure, start, stop)
  - Design plugin dependency resolution
  - Design plugin configuration system
  - **Satisfies**: R89, R90, R91, R92, R93
  - **Acceptance**: Plugin system design documented and reviewed
  - **Requires**: Phase 5 complete

- [ ] **task-7.2: Implement plugin infrastructure**
  - Implement plugin discovery and loading
  - Implement plugin lifecycle management
  - Implement plugin isolation and namespacing
  - Create plugin API documentation
  - **Satisfies**: R94, R95
  - **Acceptance**: Plugin system functional, can load/unload plugins
  - **Requires**: task-7.1

- [ ] **task-7.3: Refactor baseweb as minimal core**
  - Extract non-essential functionality to potential plugins
  - Identify core vs. plugin functionality boundaries
  - Maintain backward compatibility during transition
  - **Satisfies**: R96, NFR11, NFR15
  - **Acceptance**: Core package minimal, backward compatible
  - **Requires**: task-7.2

### Phase 8: Plugin Implementations

- [ ] **task-8.1: baseweb-magic-link plugin**
  - Create plugin package structure
  - Implement magic link authentication
  - Integrate with generic authentication package
  - Create plugin registration and configuration
  - Add plugin tests
  - **Satisfies**: R97, R98, R99, R100
  - **Acceptance**: Magic link plugin works independently, can be installed via pip
  - **Requires**: Phase 7 complete

- [ ] **task-8.2: baseweb-restful-mongo plugin**
  - Create plugin package structure
  - Implement pageable RESTful MongoDB integration
  - Based on incubator/ideas/pageable-restful-mongo-review
  - Create plugin registration and configuration
  - Add plugin tests
  - **Satisfies**: R101, R102, R103, R104
  - **Acceptance**: RESTful MongoDB plugin works independently, can be installed via pip
  - **Requires**: Phase 7 complete

- [ ] **task-8.3: baseweb-prometheus plugin**
  - Create plugin package structure
  - Implement Prometheus metrics integration
  - Integrate with generic Prometheus package from apps.homemadebycvg
  - Create plugin registration and configuration
  - Add plugin tests
  - **Satisfies**: R105, R106, R107, R108
  - **Acceptance**: Prometheus plugin works independently, can be installed via pip
  - **Requires**: Phase 7 complete

### Phase 9: Performance Optimization

- [ ] **task-9.1: Vendor bundle optimization**
  - Create bundled/minified vendor.js from individual files
  - Enable tree-shaking for Vuetify components
  - Measure and document size reduction
  - Keep non-bundled approach as fallback option
  - Document build process
  - **Satisfies**: R109, R110, R111, R112, R113, NFR5
  - **Acceptance**: Bundle size reduced by 30%+, non-bundled option still works
  - **Requires**: Phase 5 complete

---

## Done

### Phase 5: Post-modernization Further Feature Development

- [x] **task-5.2: Unify special page components** (2026-05-18)
  - Created unified `Page` component with props: `banner`, `status`, `statusTimeout`
  - Added slots: default, header, footer
  - Registered namespaced Vuex store module `page` with `banner` and `status` state
  - Store mutations: `page/banner`, `page/success`, `page/error`, `page/warning`, `page/info`, `page/clearStatus`
  - **Breaking Change**: Removed `PageWithBanner.js` and `PageWithStatus.js`
  - Migration: `<PageWithBanner>` → `<Page banner>`, `<PageWithStatus>` → `<Page status>`
  - Note: Full-page layout (`fullPage` prop) was attempted but removed - too ambitious for this task, breaks other pages
  - Files: `Page.js`, `main.css`, tests, migration guide
  - **Satisfies**: R73, R74, R75, R76, R77 (R78 deferred)

- [x] **task-5.1: Create minimal Hello World example** (2026-05-04)
  - Created `examples/hello-world/` directory structure
  - Implemented minimal Baseweb application with Vue 3 + Vuetify 3 frontend
  - Uses `uv` for dependency management (automatic virtualenv)
  - Scope: Single page, no authentication, no REST API, no WebSocket
  - Files: app.py, pyproject.toml, README.md, static/js/HelloWorld.js
  - **Satisfies**: R69, R70, R71, R72
  - Validation: App starts, HTML served, component registered, Vue 3 initializes

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
  - **Satisfies**: R53

- [x] **task-3.6: Vue 3 + Vuetify 3 Migration - App Initialization** (2026-05-04)
  - Updated main.html with Vue 3 + Vuetify 3 initialization pattern
  - Added compatibility shims for Vue 2-style global registration (Vue.component, Vue.filter, Vue.use)
  - Updated app.js: `new Vue()` -> `Vue.createApp()`
  - Updated router.js: `new VueRouter()` -> `VueRouter.createRouter()`
  - Updated store.js: `new Vuex.Store()` -> `Vuex.createStore()`
  - Updated NavigationDrawer.js: `router.addRoutes()` -> `router.addRoute()`
  - **Satisfies**: R54, R55

- [x] **task-3.7: Vue 3 + Vuetify 3 Migration - Simple Components** (2026-05-04)
  - Page.js: No changes needed (no Vuetify dependencies)
  - PageWithBanner.js: `dismissible` -> `closable` (v-alert Vuetify 3)
  - PageWithStatus.js: `top` -> `location="top"`, `flat` -> `variant="flat"`
  - ProcessDiagram.js: No changes needed (v-card compatible)
  - common.js: Filter registration works via compatibility shim
  - **Satisfies**: R56

- [x] **task-3.8: Vue 3 + Vuetify 3 Migration - Navigation Component** (2026-05-04)
  - Replaced `v-list-tile` -> `v-list-item` (and all variants)
  - Updated `v-list-group` slot: `slot="activator"` -> `v-slot:activator="{ props }"`
  - Updated `v-navigation-drawer`: `:value` -> `:model-value`
  - **Satisfies**: R57

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
  - **Satisfies**: R58, R59

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
  - **Satisfies**: R60

- [x] **task-3.11: Vue 3 + Vuetify 3 Migration - Charts and Notifications** (2026-05-04)
  - Rewrote LineChart.js to use Chart.js directly (vue-chartjs v4 has no UMD build)
  - Replaced `extends: VueChartJs.Line` with native Chart.js instantiation
  - Added reactive data updates via watch
  - Added proper cleanup in beforeUnmount hook
  - Implemented custom deepMerge() to replace $.extend()
  - Updated Chart.js options to v4 API (plugins.legend, scales.y)
  - Replaced old vue-notification element with NotificationSnackbar in main.html
  - Removed vue-chartjs.min.js from vendor scripts (no longer needed)
  - **Satisfies**: R61, R62

- [x] **task-3.12: Vue 3 + Vuetify 3 Migration - Integration Testing** (2026-05-04)
  - All 144 Python tests pass
  - 78% code coverage
  - All Vue 3 components verified working
  - Migration complete
  - **Satisfies**: R63

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

- [x] **Resource instantiation flexibility** (2026-05-01)
  - Allow passing class (instantiated per request) or instance (reused)
  - Support dependency injection via instance pattern
  - Add 7 new tests for instantiation patterns
  - **Satisfies**: R37, R38

- [x] **Migrate skill as baseweb plugin** (2026-05-01)
  - Created .claude_plugin/plugin.json for Claude Code integration
  - Created skills/migrate/skill.md with comprehensive migration guide
  - Covers Flask to Quart migration for baseweb apps

- [x] **task-3.4: Frontend integration verification** (2026-05-01)
  - Verified frontend static files served correctly
  - Verified REST API endpoints work with async handlers
  - Verified Socket.IO client initialization and connection
  - Added comprehensive frontend integration tests (13 new tests)
  - **Satisfies**: R48, R49, R50, R51, R52

- [x] **task-3.3: Migrate WebSocket support** (2026-05-01)
  - Migrated from Flask-SocketIO to python-socketio with ASGI mode
  - Implemented `socketio.AsyncServer(async_mode='asgi')`
  - Created `socketio.ASGIApp(sio, quart_app)` wrapper
  - Updated `authenticated` decorator for SocketIO context
  - **Satisfies**: R43, R44, R45, R46, R47

- [x] **task-3.2: Remove Flask-RESTful** (2026-04-30)
  - Removed Flask-RESTful dependency from pyproject.toml
  - Removed `import flask_restful` from __init__.py
  - Removed `self.api = flask_restful.Api(self)` attribute
  - Enabled 13 previously skipped tests
  - Updated migration guide for native Quart routes
  - **Satisfies**: R37, R38, R39, R40, R41, R42

- [x] **task-3.1: Migrate core Baseweb class** (2026-04-30)
  - Changed `from flask import Flask` to `from quart import Quart`
  - Converted all route handlers to async functions
  - Updated `render_template()` calls with `await`
  - Updated `send_from_directory()` calls with `await`
  - Updated authentication decorator for async
  - Added proper MIME types for JS/JSON responses
  - **Satisfies**: R29, R30, R31, R33, R34, R35, R36

- [x] **task-2.2: Coordinate with hosted-quarts** (2026-04-30)
  - Documented relationship: hosted-quarts serves baseweb as Quart app
  - Confirmed no code dependencies between projects
  - Aligned timeline: parallel development, coordinated production upgrade
  - Created coordination plan: reporting/task-2.2/coordination-plan.md
  - **Satisfies**: R24, R25, R26, R27, R28

- [x] **task-2.1: Decide on version strategy** (2026-04-30)
  - Documented decision: single version with major bump to 1.0.0
  - Created migration guide (docs/migration-guide.md)
  - Created CHANGELOG.md with v1.0.0 entry
  - Updated README.md with references to migration guide
  - **Satisfies**: R20, R21, R22, R23

- [x] **task-0.2: Complete uv migration and fix CI** (2026-04-30)
  - Removed old pyenv management targets from Makefile
  - Updated GitHub Actions workflow to use uv
  - Applied python-project skill best practices
  - Updated Python version support to 3.10, 3.11, 3.12
  - Installed uv system-wide via Homebrew
  - Created .python-version (pinned to 3.12)
  - Generated uv.lock for reproducible builds
  - Added .venv to .gitignore, removed .python-version from gitignore
  - **Satisfies**: R11, R19

- [x] **task-0.0: Migrate to standard Python project setup** (2026-04-29)
  - Migrated from setup.py to pyproject.toml with hatchling
  - Moved to src-layout (src/baseweb/)
  - Created py.typed marker file
  - Moved all tool config to pyproject.toml (ruff, pytest, coverage)
  - Removed setup.py, tox.ini, .pypi-template, old requirements files
  - Updated Makefile for new build commands
  - **Satisfies**: R1, R2, R3, R5, R16, R18

- [x] **task-0.1: Functional analysis** (2026-04-29)
  - Created analysis/functional.md
  - Documented project overview and technology stack
  - Defined functional requirements for all phases
  - Created risk assessment and success metrics
  - Identified open questions (all answered)