# Consensus Report: task-6.1 - PWA Manifest and Service Worker Foundation

**Created:** 2026-05-19
**Task:** task-6.1
**Status:** Approved for Implementation

---

## Domain Reviews

### UI/UX Designer Review

**Agent:** c3:ui-ux-designer
**Status:** ✅ Approved
**Analysis:** `analysis/ux-pwa-foundation.md`

**Key Recommendations:**
1. Add 180x180 icon to manifest.json for iOS compatibility
2. Add iOS-specific meta tags to main.html
3. Implement Service Worker with cache-first strategy for static assets
4. Register Service Worker on window.load event
5. Skip caching for /api/ and /socket.io/ routes

**Implementation Checklist:**
- [ ] Add 180x180 icon to manifest
- [ ] Add description field to manifest
- [ ] Add scope field to manifest
- [ ] Add iOS meta tags to main.html
- [ ] Create sw.js Service Worker
- [ ] Add /sw.js backend route
- [ ] Register Service Worker in main.html

---

## Test Strategy

**Agent:** c3:testing-engineer
**Status:** ✅ Test Stubs Created
**Test File:** `tests/test_pwa.py`

**Coverage:** 42 test stubs covering:
- Manifest endpoint (valid JSON, required fields)
- iOS compatibility (180x180 icon, description, scope)
- Service Worker endpoint (headers, content)
- HTML template iOS meta tags
- Service Worker registration
- Conditional PWA behavior

**Skipped Tests:** 3 tests requiring browser automation (offline state management)

---

## Implementation Plan

### Phase 1: Manifest Enhancement

1. **Update manifest.json template**
   - Add 180x180 icon entry
   - Add `description: "{{ app.description }}"`
   - Add `scope: "/"`

### Phase 2: iOS Meta Tags

2. **Update main.html template**
   - Add `apple-mobile-web-app-capable` meta tag
   - Add `apple-mobile-web-app-status-bar-style` meta tag
   - Add `apple-mobile-web-app-title` meta tag
   - Add `apple-touch-icon` link (180x180)

### Phase 3: Service Worker

3. **Create Service Worker**
   - File: `src/baseweb/static/js/sw.js`
   - Cache strategy: Cache-first for static assets
   - Skip: /api/ and /socket.io/ routes

4. **Add Service Worker Route**
   - Endpoint: `/sw.js`
   - Headers: `Service-Worker-Allowed: /`
   - Content-Type: `application/javascript`

5. **Register Service Worker**
   - Add registration code in main.html
   - Trigger on `window.load`
   - Only when `app.style == "pwa"`

---

## Files to Modify/Create

| File | Action | Purpose |
|------|--------|---------|
| `src/baseweb/templates/manifest.json` | Modify | Add 180x180 icon, description, scope |
| `src/baseweb/templates/main.html` | Modify | Add iOS meta tags, SW registration |
| `src/baseweb/static/js/sw.js` | Create | Service Worker implementation |
| `src/baseweb/__init__.py` | Modify | Add Service Worker route |
| `tests/test_pwa.py` | Update | Convert stubs to real tests |

---

## Acceptance Criteria

| Criteria | Verification | Status |
|----------|--------------|--------|
| PWA installs on iOS Home Screen | Manual test on iOS 16.4+ | Pending |
| App launches in standalone mode | `display: "standalone"` in manifest | OK |
| Works offline with cached assets | Service Worker caches assets | Pending |
| 180x180 icon present | Test stub: `test_manifest_contains_180x180_icon` | Pending |
| Service Worker registered | Test stub: `test_html_contains_service_worker_registration` | Pending |

---

## Risks and Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| iOS 16.4+ requirement | Medium | Document clearly in README |
| Service Worker caching breaks updates | High | Use cache versioning |
| No browser automation for offline tests | Low | Manual testing required |

---

## Approval

- **UI/UX Designer:** ✅ Approved
- **Testing Engineer:** ✅ Test stubs created

**Decision:** Proceed to implementation (Phase 4)

---

*Consensus report prepared by: Project Manager Agent*
*Date: 2026-05-19*