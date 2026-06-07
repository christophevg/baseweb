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

### Phase 8: Plugin System Architecture


### Phase 8: Plugin System Architecture

- [ ] **task-8.1: Design plugin namespace system**
  - Design plugin discovery mechanism
  - Define plugin lifecycle hooks (load, initialize, configure, start, stop)
  - Design plugin dependency resolution
  - Design plugin configuration system
  - **Satisfies**: R89, R90, R91, R92, R93
  - **Acceptance**: Plugin system design documented and reviewed
  - **Requires**: Phase 5 complete

- [ ] **task-8.2: Implement plugin infrastructure**
  - Implement plugin discovery and loading
  - Implement plugin lifecycle management
  - Implement plugin isolation and namespacing
  - Create plugin API documentation
  - **Satisfies**: R94, R95
  - **Acceptance**: Plugin system functional, can load/unload plugins
  - **Requires**: task-8.1

- [ ] **task-8.3: Refactor baseweb as minimal core**
  - Extract non-essential functionality to potential plugins
  - Identify core vs. plugin functionality boundaries
  - Maintain backward compatibility during transition
  - **Satisfies**: R96, NFR11, NFR15
  - **Acceptance**: Core package minimal, backward compatible
  - **Requires**: task-8.2

### Phase 9: Plugin Implementations

- [ ] **task-9.1: baseweb-magic-link plugin**
  - Create plugin package structure
  - Implement magic link authentication
  - Integrate with generic authentication package
  - Create plugin registration and configuration
  - Add plugin tests
  - **Satisfies**: R97, R98, R99, R100
  - **Acceptance**: Magic link plugin works independently, can be installed via pip
  - **Requires**: Phase 8 complete

- [ ] **task-9.2: baseweb-restful-mongo plugin**
  - Create plugin package structure
  - Implement pageable RESTful MongoDB integration
  - Based on incubator/ideas/pageable-restful-mongo-review
  - Create plugin registration and configuration
  - Add plugin tests
  - **Satisfies**: R101, R102, R103, R104
  - **Acceptance**: RESTful MongoDB plugin works independently, can be installed via pip
  - **Requires**: Phase 8 complete

- [ ] **task-9.3: baseweb-prometheus plugin**
  - Create plugin package structure
  - Implement Prometheus metrics integration
  - Integrate with generic Prometheus package from apps.homemadebycvg
  - Create plugin registration and configuration
  - Add plugin tests
  - **Satisfies**: R105, R106, R107, R108
  - **Acceptance**: Prometheus plugin works independently, can be installed via pip
  - **Requires**: Phase 8 complete

### Phase 10: Performance Optimization

- [ ] **task-10.1: Vendor bundle optimization**
  - Create bundled/minified vendor.js from individual files
  - Enable tree-shaking for Vuetify components
  - Measure and document size reduction
  - Keep non-bundled approach as fallback option
  - Document build process
  - Update Service Worker STATIC_ASSETS to use bundled files instead of hardcoded list
  - **Satisfies**: R109, R110, R111, R112, R113, NFR5
  - **Acceptance**: Bundle size reduced by 30%+, non-bundled option still works
  - **Requires**: Phase 5 complete

### Phase 11: Code Quality Improvements

- [ ] **task-11.1: Fix rate limiter to use monotonic time**
  - Change `time.time()` to `time.monotonic()` in rate limiter
  - Ensures accurate time intervals even with system clock changes
  - **Satisfies**: Code Review M4
  - **Acceptance**:
    - Rate limiter uses `time.monotonic()`
    - Tests pass
    - No behavior change

- [ ] **task-11.2: Refactor toDict() to use dataclasses.asdict**
  - Replace manual dict construction with `asdict(self)`
  - Add post-processing for computed properties
  - **Satisfies**: Code Review M5
  - **Acceptance**:
    - Uses `asdict()` from dataclasses module
    - All computed properties still included
    - Tests pass

- [ ] **task-11.3: Add file permissions validation**
  - Validate that config files with sensitive data are not world-readable
  - Add warning if permissions are too permissive
  - **Satisfies**: Code Review M6
  - **Acceptance**:
    - `baseweb check` validates file permissions
    - Warning issued for world-readable config files
    - Tests pass

- [ ] **task-11.4: Optimize rate limiter data structure**
  - Replace list with `collections.deque` for O(1) cleanup
  - Add max size limit to prevent memory issues
  - **Satisfies**: Code Review M7
  - **Acceptance**:
    - Uses `deque` with maxlen
    - O(1) append and cleanup operations
    - Tests pass

- [ ] **task-11.5: Remove config mutation in __init__**
  - Create copy of config instead of mutating passed object
  - Document immutability expectations
  - **Satisfies**: Code Review M8
  - **Acceptance**:
    - Passed config is not modified
    - Documentation clarifies immutability
    - Tests pass

- [ ] **task-11.6: Add module-level exports**
  - Add `__all__` to all public modules
  - Document public API explicitly
  - **Satisfies**: Code Review L7
  - **Acceptance**:
    - All public modules have `__all__`
    - Public API documented
    - Tests pass

- [ ] **task-11.7: Consolidate module-level constants**
  - Review usage of `OK` and `HERE` constants
  - Remove unused or document purpose
  - **Satisfies**: Code Review L8
  - **Acceptance**:
    - Unused constants removed
    - Used constants documented
    - Tests pass

### Phase 12: Security Hardening

- [ ] **task-12.1: Add path validation for static files**
  - Add explicit validation in static file handlers
  - Reject paths with `..` or starting with `/`
  - **Satisfies**: Security Review M4
  - **Acceptance**:
    - Path traversal attempts logged and rejected
    - Tests for path traversal prevention
    - Documentation updated

- [ ] **task-12.2: Make rate limits configurable**
  - Move hardcoded rate limits to configuration
  - Allow per-endpoint customization
  - **Satisfies**: Code Review L1
  - **Acceptance**:
    - Rate limits configurable in baseweb.toml
    - Default values match current behavior
    - Tests pass

- [ ] **task-12.3: Document service worker cache strategy**
  - Add documentation for cache invalidation
  - Explain version-based cache updates
  - **Satisfies**: Security Review M5
  - **Acceptance**:
    - docs/pwa.md created or updated
    - Cache strategy documented
    - Version update process explained

- [ ] **task-12.4: Use Enum for style values**
  - Create `AppStyle` enum for "web" and "pwa" values
  - Update configuration to use enum
  - **Satisfies**: Code Review L2
  - **Acceptance**:
    - `AppStyle` enum created
    - Configuration uses enum
    - Backward compatible with string values
    - Tests pass

- [ ] **task-12.5: Make known push services configurable**
  - Move hardcoded `KNOWN_PUSH_SERVICES` to configuration
  - Allow custom push service endpoints
  - **Satisfies**: Code Review L3
  - **Acceptance**:
    - Push services configurable
    - Default list provided
    - Tests pass

### Phase 13: API Enhancements

- [ ] **task-13.1: Add configuration validation**
  - Implement `validate()` method on BasewebConfig
  - Validate PWA requirements when style="pwa"
  - Add `baseweb check --strict` for full validation
  - **Satisfies**: API Architect Recommendation
  - **Acceptance**:
    - `config.validate()` raises `ConfigurationError` for invalid config
    - PWA icon directory validated when style="pwa"
    - Tests pass

- [ ] **task-13.2: Document authentication patterns**
  - Add examples for JWT, OAuth2, Basic Auth
  - Document scope-based authorization
  - Add to docs/adding-security.md
  - **Satisfies**: API Architect Recommendation
  - **Acceptance**:
    - Three authentication patterns documented
    - Code examples for each
    - Best practices explained

- [ ] **task-13.3: Add OpenAPI schema generation**
  - Generate OpenAPI 3.0 spec from Resource classes
  - Expose at `/openapi.json` endpoint
  - **Satisfies**: API Architect Recommendation
  - **Acceptance**:
    - OpenAPI spec generated
    - Available at `/openapi.json`
    - Swagger UI at `/docs` (optional)

- [ ] **task-13.4: Implement API versioning**
  - Document URL path vs header versioning approach
  - Add version to Resource registration
  - **Satisfies**: API Architect Recommendation
  - **Acceptance**:
    - Versioning strategy documented
    - Resources can be versioned
    - Tests pass

- [ ] **task-13.5: Create validation decorators**
  - Add `@validate_body(schema)` decorator
  - Add `@validate_query(schema)` decorator
  - Integrate with pydantic or similar
  - **Satisfies**: API Architect Recommendation
  - **Acceptance**:
    - Decorators work with Resource classes
    - Validation errors return proper HTTP responses
    - Tests pass

### Phase 14: Documentation Improvements

- [ ] **task-14.1: Fix version inconsistency**
  - Update README.md to reflect current version
  - Ensure all docs reference correct version
  - **Satisfies**: Documentation Review
  - **Acceptance**:
    - Version consistent across all docs
    - Badge shows current version

- [ ] **task-14.2: Update async patterns in tutorials**
  - Update building-your-first-baseweb-app.md
  - Ensure all code examples use async patterns
  - **Satisfies**: Documentation Review
  - **Acceptance**:
    - All examples use `async`/`await`
    - No Flask-style sync code

- [ ] **task-14.3: Create deployment guide**
  - Create docs/deployment.md
  - Cover Docker, Kubernetes, Nginx setups
  - Add production checklist
  - **Satisfies**: Documentation Review
  - **Acceptance**:
    - Deployment guide created
    - Docker example provided
    - Kubernetes example provided
    - Production checklist included

- [ ] **task-14.4: Create general troubleshooting guide**
  - Create docs/troubleshooting.md
  - Cover common issues across all features
  - Link from other docs
  - **Satisfies**: Documentation Review
  - **Acceptance**:
    - Troubleshooting guide created
    - Common issues documented
    - Cross-references added

- [ ] **task-14.5: Expand architecture overview**
  - Expand docs/whats-in-the-box.md
  - Add architecture diagram
  - Explain component relationships
  - **Satisfies**: Documentation Review
  - **Acceptance**:
    - Architecture diagram included
    - Component relationships explained
    - Request lifecycle documented

- [ ] **task-14.6: Create API reference**
  - Create docs/api.md
  - Document all public classes and functions
  - Include examples
  - **Satisfies**: Documentation Review
  - **Acceptance**:
    - API reference created
    - All public API documented
    - Code examples included

- [ ] **task-14.7: Add PWA setup guide**
  - Add icon generation guide to configuration.md
  - Document manifest customization
  - Explain theme colors
  - **Satisfies**: Documentation Review
  - **Acceptance**:
    - Icon generation documented
    - Manifest customization explained
    - Theme colors documented

---

## Done

### Phase 7: CLI and Configuration System (COMPLETE - 2026-06-07)

**Design Decisions:**
- No backward compatibility with settings dict (breaking change)
- Configuration loaded via `get_config()` from Clevis (no `.load()` method)
- Baseweb.__init__ accepts BasewebConfig directly (no `.from_config()` method)
- Clevis handles all environment variable mapping automatically
- TOML structure with nested sections: [branding.*], [features.*], [server], [app.*]
- Application-specific config via `register_app_config()` pattern

- [x] **task-7.1: Create configuration module** (2026-06-07)
  - Created `src/baseweb/config.py` with BasewebConfig dataclass
  - Defined nested dataclasses: BrandingConfig, FeaturesConfig, ServerConfig
  - Implemented `register_app_config(name, config_class)` function
  - Implemented configuration validation (icons_dir required when style="pwa")
  - **Satisfies**: R114, R115, R116

- [x] **task-7.2: Integrate configuration with Baseweb class** (2026-06-07)
  - Updated `__init__` to accept BasewebConfig parameter (required, no settings dict)
  - Removed environment variable loading from `__init__` (Clevis handles this)
  - Removed settings dict support (breaking change)
  - Applied configuration from BasewebConfig to application
  - **Satisfies**: R117

- [x] **task-7.3: Implement CLI module** (2026-06-07)
  - Created `src/baseweb/__main__.py` with Clevis command pattern
  - Added `baseweb init` command to create default baseweb.toml
  - Added `baseweb serve` command to run applications via Gunicorn
  - Added `baseweb config` command to display configuration (table or TOML format)
  - Added `baseweb version` command
  - Added `baseweb check` command to validate configuration without running
  - CLI uses `get_config(BasewebConfig, name="baseweb")` for configuration loading
  - All CLI arguments override configuration via Clevis
  - **Satisfies**: R118, R119, R120, R121

- [x] **task-7.4: Add CLI tests** (2026-06-07)
  - Created tests/test_cli.py with 93 comprehensive tests
  - Tested all CLI commands: init, check, config, serve, version
  - Tested argument parsing and command dispatch
  - Tested error handling with clear error messages
  - Tested configuration override via CLI args
  - Tested helper functions: import_app, config_to_toml, print_config_table
  - Tested Gunicorn integration: StandaloneApplication
  - Achieved 94% test coverage for CLI module
  - **Satisfies**: R122

- [x] **task-7.5: Create configuration documentation** (2026-06-07)
  - Created docs/configuration.md with comprehensive configuration reference
  - Documented all configuration options: root, branding, features, server
  - Documented TOML structure with nested sections
  - Documented configuration priority order (defaults < user TOML < project TOML < env vars < CLI args)
  - Documented environment variables (APP_*, GUNICORN_*)
  - Documented environment variable interpolation (${VAR:-default})
  - Documented register_app_config() pattern for app-specific config
  - Added migration guide from environment variables to TOML
  - Added troubleshooting section
  - Updated docs/index.md with link to configuration documentation
  - **Satisfies**: R123

- [x] **task-7.6: Create CLI documentation** (2026-06-07)
  - Created docs/cli.md with complete CLI reference
  - Documented all CLI commands: init, check, config, serve, version
  - Added usage examples for each command
  - Added common workflows section
  - Added troubleshooting guide
  - Updated README.md with Quick Start section
  - Created docs/end-user/DOCUMENTATION.md summary
  - **Satisfies**: R124

### Phase 6: PWA and Push Notifications (COMPLETE - 2026-06-07)

- [x] **task-6.4: PWA and push notifications documentation** (2026-06-07)
  - Created comprehensive documentation in docs/push-notifications.md
  - Documented iOS Safari PWA installation workflow with step-by-step guide
  - Documented developer setup (VAPID keys, API endpoints, integration)
  - Documented user-facing permission flow
  - Created troubleshooting guide with iOS-specific issues
  - Included compatibility matrix (iOS 16.4+ Safari only)
  - **Satisfies**: R88

- [x] **task-6.3: Push notification frontend integration** (2026-05-20)
  - Implemented notification UI component (PushNotificationSettings.js)
  - Added standalone PWA mode detection for iOS Safari
  - Added HTTPS/localhost security check for Push API
  - Pre-fetched VAPID key on page load for Safari user gesture requirement
  - Implemented subscribe/unsubscribe flow with permission handling
  - Synced subscription state with backend via POST/DELETE endpoints
  - Added iOS-specific guidance for non-PWA users
  - Service Worker already handles push events (from task-6.1)
  - Created testing documentation for ngrok + real iPhone testing
  - Files: notifications.js, PushNotificationSettings.js, docs/push-notifications-testing.md
  - **Satisfies**: R81, R82, R84
  - **Note**: iOS Simulator does NOT support Web Push - must test on real device

- [x] **task-6.2: Push notification backend infrastructure** (2026-05-19)
  - Implemented VAPID key generation and management (src/baseweb/vapid.py)
  - Created push subscription storage with CRUD operations
  - Created GET /api/vapid-public-key endpoint (unauthenticated)
  - Created POST/GET/DELETE /api/push-subscriptions endpoints (authenticated)
  - Created POST /api/push-notifications endpoint (admin only)
  - Added rate limiting (10/hour, 50/day per user, 100/min global)
  - Added input validation (endpoint URL, keys, payload)
  - Added known push service validation (FCM, Mozilla, Apple)
  - Added security features (VAPID private key from env, subscription validation)
  - iOS Safari compatible (VAPID claims with subject and audience)
  - Files: vapid.py, push.py, test_push.py (89 tests)
  - **Satisfies**: R85, R86, R87, NFR3

- [x] **task-6.1: PWA manifest and service worker foundation** (2026-05-19)
  - Enhanced manifest.json with 180x180 icon, description, scope fields
  - Added iOS Safari meta tags (apple-mobile-web-app-capable, status-bar-style, title, touch-icon)
  - Created Service Worker (sw.js) with cache-first strategy for static assets
  - Added Service Worker route with correct headers (Service-Worker-Allowed: /)
  - Registered Service Worker on window.load when APP_STYLE=pwa
  - Generated 9 placeholder icons (72x72 to 512x512)
  - Added offline UX indicator (isOnline state, offline badge in app bar)
  - Added python-dotenv to hello-world example for .env file loading
  - Removed python-dotenv from baseweb core dependencies (not needed in framework)
  - Fixed icon paths from /images/icons/ to /static/images/icons/
  - Files: manifest.json, main.html, store.js, sw.js, __init__.py, test_pwa.py
  - Files: scripts/generate_icons.py, static/images/icons/*.png
  - Files: examples/hello-world/app/__init__.py, examples/hello-world/pyproject.toml
  - **Satisfies**: R79, R80, R83

### Phase 5: Post-modernization Further Feature Development (COMPLETE - 2026-05-18)

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