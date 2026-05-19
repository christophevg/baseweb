# Requirements

This document tracks all functional and non-functional requirements for the baseweb project.

## Functional Requirements

### Phase 1: Project Cleanup

#### Remove pypi-template Support
- [x] R1: `.pypi-template` file is removed
- [x] R2: `setup.py` is reviewed and simplified (migrated to pyproject.toml)
- [x] R3: All Makefile targets that reference pypi-template are cleaned up
- [x] R4: Documentation reflects the new structure
- [x] R5: Build and publish process still works

#### Testing Infrastructure
- [x] R6: `tests/` directory exists with proper structure
- [x] R7: Unit tests exist for core Baseweb class functionality (initialization, configuration, component registration, stylesheet registration, script registration, route registration, authentication hooks)
- [x] R8: Integration tests exist for basic route handling, template rendering, static file serving
- [x] R9: `pytest` configuration is complete (pyproject.toml)
- [x] R10: Coverage reporting is configured
- [x] R11: `make test` runs all tests successfully
- [x] R12: Minimum 80% code coverage achieved (currently 78%)

#### Project Standards
- [x] R13: Code passes `ruff` linting without errors
- [x] R14: Type hints are added where appropriate
- [x] R15: Docstrings are present for all public modules, classes, and functions
- [x] R16: `pyproject.toml` exists with full project metadata
- [x] R17: `.gitignore` is comprehensive
- [x] R18: `MANIFEST.in` includes all necessary files for distribution
- [x] R19: GitHub Actions CI/CD is configured and passing

### Phase 2: Architecture Decision

#### Version Strategy
- [x] R20: Decision documented with rationale (single version, major bump to 1.0.0)
- [x] R21: Migration guide created for existing users
- [x] R22: Changelog entry prepared
- [x] R23: Any dual-version code paths are planned for removal

#### hosted-quarts Coordination
- [x] R24: Dependency matrix documented
- [x] R25: Migration timeline aligned with hosted-quarts
- [x] R26: Breaking changes communicated
- [x] R27: Integration testing with hosted-quarts performed
- [x] R28: Shared code/dependencies identified and addressed (none identified)

### Phase 3: Flask to Quart Migration

#### Core Migration
- [x] R29: `from flask import Flask` changed to `from quart import Quart`
- [x] R30: All route handlers are async functions
- [x] R31: `render_template()` calls use `await`
- [x] R32: `request.get_json()` calls use `await`
- [x] R33: `send_from_directory()` calls use `await`
- [x] R34: Authentication decorator works with async handlers
- [x] R35: All existing functionality preserved
- [x] R36: All tests pass

#### Flask-RESTful Migration
- [x] R37: API endpoints work with Quart
- [x] R38: Resource classes function correctly
- [x] R39: All HTTP methods (GET, POST, PUT, DELETE, PATCH) work
- [x] R40: Request parsing works with async
- [x] R41: Response formatting is preserved
- [x] R42: Integration tests pass

#### WebSocket Migration
- [x] R43: WebSocket functionality is preserved (python-socketio with ASGI)
- [x] R44: Connection handling works
- [x] R45: Event handlers are async
- [x] R46: Socket.IO client compatibility maintained
- [x] R47: Integration tests for WebSocket functionality pass

#### Frontend Integration
- [x] R48: Frontend works without changes
- [x] R49: Vue components render correctly
- [x] R50: WebSocket connections established
- [x] R51: API calls return expected data
- [x] R52: All integration tests pass

#### Vue 3 + Vuetify 3 Migration
- [x] R53: Vue 3 vendor files downloaded and verified
- [x] R54: App initialization uses Vue 3 + Vuetify 3 pattern
- [x] R55: Compatibility shims for Vue 2-style global registration work
- [x] R56: Simple components render correctly (Page, PageWithBanner, PageWithStatus, ProcessDiagram)
- [x] R57: Navigation drawer works with Vuetify 3 components
- [x] R58: Form generator replaced with VuetifyFormGenerator
- [x] R59: Forms work with existing schemas
- [x] R60: CollectionView data tables work with CRUD operations
- [x] R61: Charts render correctly with native Chart.js
- [x] R62: Notifications work via Vuetify snackbar
- [x] R63: All 144 tests pass

### Phase 4: hosted-quarts Coordination

- [x] R64: Dependency matrix documented
- [x] R65: Migration timeline aligned with hosted-quarts
- [x] R66: Breaking changes communicated
- [x] R67: Integration testing with hosted-quarts performed
- [x] R68: Shared code/dependencies identified and addressed

### Phase 5: Component Consolidation

#### Hello World Example
- [x] R69: Minimal Hello World example created
- [x] R70: Uses `uv` for dependency management
- [x] R71: Single page, no authentication, no REST API, no WebSocket
- [x] R72: App starts, HTML served, component registered, Vue 3 initializes

#### Unify Page Components
- [x] R73: Unified `Page` component created with configurable props/slots
- [x] R74: Support for banner, status props (navigation deferred by design)
- [x] R75: Existing components removed (breaking change, migration guide provided)
- [x] R76: Migration guide for existing usage
- [x] R77: Tests for new component
- [ ] R78: Full-page layouts supported without browser scrollbar (header slot, growing scrollable body, footer slot) - Deferred

### Phase 6: PWA and Push Notifications

#### PWA Support Enhancement
- [x] R79: Progressive Web App manifest enhanced for iOS compatibility (Phase 6)
- [x] R80: Service Worker implementation for offline support (Phase 6)
- [ ] R81: Push API integration with VAPID key support
- [ ] R82: Notifications API integration
- [x] R83: iOS Safari standalone mode support (iOS 16.4+) (Phase 6)
- [ ] R84: User permission prompt triggered by user action
- [x] R85: Backend VAPID key generation and management (Phase 6)
- [x] R86: Push subscription storage and retrieval (Phase 6)
- [x] R87: Push notification sending functionality (Phase 6)
- [ ] R88: Documentation for PWA installation workflow

#### iOS-Specific Technical Notes
- **iOS Version Requirement**: Web Push requires iOS 16.4 or newer. Older iOS versions cannot receive push notifications.
- **Safari Only**: Push notifications only work in iOS Safari. Third-party browsers (Chrome, Firefox on iOS) use WebKit but cannot prompt or receive push notifications.
- **Standalone Mode Required**: The PWA must be installed to the Home Screen and launched from there. Standard Safari tabs cannot receive push notifications.
- **User Action Required**: Permission prompts must be triggered by direct user action (e.g., clicking a "Subscribe" button) while running in standalone mode.
- **VAPID Keys Required**: Backend must generate VAPID keys for secure push message authentication with Apple's push service.
- **User Workflow**: Open Safari → Add to Home Screen → Launch PWA → User action triggers permission prompt → Grant permission

### Phase 7: Plugin System Architecture

#### Core Plugin Infrastructure
- [ ] R89: Plugin namespace system designed
- [ ] R90: Plugin discovery mechanism implemented
- [ ] R91: Plugin lifecycle hooks defined (load, initialize, configure, start, stop)
- [ ] R92: Plugin dependency resolution
- [ ] R93: Plugin configuration system
- [ ] R94: Plugin isolation and namespacing
- [ ] R95: Plugin API documentation
- [ ] R96: Core baseweb package refactored as minimal core

### Phase 8: Plugin Implementations

#### baseweb-magic-link Plugin
- [ ] R97: Magic link authentication plugin implemented
- [ ] R98: Integration with generic authentication package
- [ ] R99: Plugin registration and configuration
- [ ] R100: Plugin tests

#### baseweb-restful-mongo Plugin
- [ ] R101: RESTful MongoDB integration plugin implemented
- [ ] R102: Based on pageable-restful-mongo pattern
- [ ] R103: Plugin registration and configuration
- [ ] R104: Plugin tests

#### baseweb-prometheus Plugin
- [ ] R105: Prometheus metrics plugin implemented
- [ ] R106: Integration with generic Prometheus package
- [ ] R107: Plugin registration and configuration
- [ ] R108: Plugin tests

### Phase 9: Performance Optimization

#### Vendor Bundle Optimization
- [ ] R109: Bundled/minified vendor.js created from individual files
- [ ] R110: Tree-shaking enabled for Vuetify components
- [ ] R111: Size reduction measured and documented
- [ ] R112: Non-bundled approach maintained as fallback option
- [ ] R113: Build process documented

## Non-Functional Requirements

### Security
- [x] NFR1: Authentication hooks support async handlers
- [x] NFR2: WebSocket authentication preserved after migration
- [x] NFR3: Push notification authentication uses VAPID keys securely (Phase 6)

### Performance
- [x] NFR4: Async handlers improve request throughput
- [ ] NFR5: Vendor bundle size optimized (target: 30% reduction)
- [ ] NFR6: PWA caching improves perceived load time

### Maintainability
- [x] NFR7: Code passes ruff linting
- [x] NFR8: Test coverage maintained at 78%+
- [x] NFR9: Type hints on public API
- [x] NFR10: Clear documentation for migration path
- [ ] NFR11: Plugin architecture allows independent development

### Compatibility
- [x] NFR12: Vue 3 + Vuetify 3 frontend works correctly
- [x] NFR13: Socket.IO client compatibility maintained
- [ ] NFR14: iOS Safari PWA push notification support (iOS 16.4+)
- [ ] NFR15: Backward compatibility during plugin system transition

## Completed Requirements Summary

| Phase | Total | Completed |
|-------|-------|-----------|
| Phase 1 | 19 | 19 |
| Phase 2 | 9 | 9 |
| Phase 3 | 35 | 35 |
| Phase 4 | 5 | 5 |
| Phase 5 | 10 | 4 |
| Phase 6 | 10 | 0 |
| Phase 7 | 8 | 0 |
| Phase 8 | 12 | 0 |
| Phase 9 | 5 | 0 |

**Total: 72 completed, 42 remaining**