# UX/UI Analysis: PWA Manifest and Service Worker Foundation

**Created:** 2026-05-19
**Task:** task-6.1
**Status:** Draft

---

## Executive Summary

This document provides UX/UI analysis for task-6.1: PWA manifest and service worker foundation. The analysis focuses on iOS Safari compatibility (iOS 16.4+), offline support, and user experience considerations for Progressive Web App installation and usage.

---

## Current State Analysis

### Existing PWA Infrastructure

**Manifest Template** (`src/baseweb/templates/manifest.json`)
- Uses Jinja2 templating with app settings
- `display: "standalone"` - correct for iOS Safari
- Icon sizes: 72, 96, 128, 144, 152, 192, 384, 512
- **Missing:** 180x180 icon (iOS requirement)

**HTML Template** (`src/baseweb/templates/main.html`)
- Conditional manifest link: `{% if app.style == "pwa" %}`
- No Service Worker registration
- No iOS-specific meta tags for PWA

**Backend Configuration** (`src/baseweb/__init__.py`)
- Manifest only served when `settings.style == "pwa"`
- Route: `/manifest.json` endpoint

**Service Worker**
- **Does not exist** - needs implementation

---

## Analysis

### 1. Manifest Enhancement for iOS Compatibility

#### Current Gap Analysis

| Requirement | Current State | Status |
|-------------|---------------|--------|
| `display: "standalone"` | Present | OK |
| 192x192 icon | Present | OK |
| 180x180 icon | Missing | NEEDED |
| `apple-touch-icon` link | Present (favicon_support) | Conditional |
| iOS meta tags | Missing | NEEDED |
| Service Worker scope | Missing | NEEDED |

#### Recommended Manifest Changes

```json
{
  "name": "{{ app.name }}",
  "short_name": "{{ app.short_name }}",
  "description": "{{ app.description }}",
  "start_url": "/",
  "display": "standalone",
  "background_color": "{{ app.background_color }}",
  "theme_color": "{{ app.color }}",
  "orientation": "portrait-primary",
  "scope": "/",
  "icons": [
    { "src": "/images/icons/icon-72x72.png", "type": "image/png", "sizes": "72x72" },
    { "src": "/images/icons/icon-96x96.png", "type": "image/png", "sizes": "96x96" },
    { "src": "/images/icons/icon-128x128.png", "type": "image/png", "sizes": "128x128" },
    { "src": "/images/icons/icon-144x144.png", "type": "image/png", "sizes": "144x144" },
    { "src": "/images/icons/icon-152x152.png", "type": "image/png", "sizes": "152x152" },
    { "src": "/images/icons/icon-180x180.png", "type": "image/png", "sizes": "180x180" },
    { "src": "/images/icons/icon-192x192.png", "type": "image/png", "sizes": "192x192" },
    { "src": "/images/icons/icon-384x384.png", "type": "image/png", "sizes": "384x384" },
    { "src": "/images/icons/icon-512x512.png", "type": "image/png", "sizes": "512x512" }
  ]
}
```

**Key Changes:**
1. Add `180x180` icon entry (iOS requirement)
2. Add `description` field (recommended for app stores)
3. Add `scope` field (defines Service Worker boundary)

#### iOS-Specific HTML Meta Tags

Add to `main.html` within the `<head>` section when `app.style == "pwa"`:

```html
{% if app.style == "pwa" %}
<!-- PWA Manifest -->
<link rel="manifest" href="/manifest.json" />

<!-- iOS Safari PWA Support -->
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
<meta name="apple-mobile-web-app-title" content="{{ app.short_name }}">
<link rel="apple-touch-icon" sizes="180x180" href="/images/icons/icon-180x180.png">
{% endif %}
```

**Purpose of each meta tag:**
- `apple-mobile-web-app-capable`: Enables standalone mode on iOS
- `apple-mobile-web-app-status-bar-style`: Controls status bar appearance (black-translucent for immersive experience)
- `apple-mobile-web-app-title`: Short name shown under home screen icon
- `apple-touch-icon`: Icon used when adding to home screen (180x180 is optimal for iOS)

---

### 2. Service Worker UX

#### User Experience Goals

1. **Offline Resilience:** App should function without network connectivity
2. **Fast Loading:** Cached assets load instantly
3. **Graceful Degradation:** User is informed when offline, not confused
4. **Automatic Updates:** New versions are cached seamlessly

#### Service Worker Scope

```
/                    <- Service Worker scope (root)
├── /                <- Cached: App shell (HTML, CSS, JS)
├── /static/vendor/  <- Cached: Third-party libraries
├── /static/css/     <- Cached: Core stylesheets
├── /static/js/      <- Cached: Core JavaScript
├── /manifest.json    <- Cached: Manifest
└── /api/            <- NOT cached: Dynamic API calls
```

#### Caching Strategy

| Resource Type | Strategy | Reasoning |
|---------------|----------|-----------|
| App Shell (HTML) | Cache-first, fallback to network | Instant load, offline capable |
| Static JS/CSS | Cache-first, fallback to network | Immutable assets, long cache |
| Vendor files | Cache-first, fallback to network | Third-party libraries |
| Images/icons | Cache-first with expiration | Large assets, infrequent changes |
| API calls | Network-first, no cache | Dynamic data must be fresh |
| WebSocket | No caching | Real-time, must be live |

#### Service Worker Template Location

Create: `src/baseweb/static/js/sw.js`

```javascript
// Service Worker for baseweb PWA
const CACHE_NAME = 'baseweb-v1';
const STATIC_ASSETS = [
  '/',
  '/static/js/app.js',
  '/static/js/store.js',
  '/static/js/router.js',
  '/static/js/common.js',
  '/static/js/components/Page.js',
  '/static/js/components/CollectionView.js',
  '/static/js/components/NotificationSnackbar.js',
  '/static/js/components/VuetifyFormGenerator.js',
  '/static/js/components/LineChart.js',
  '/static/js/components/NavigationDrawer.js',
  '/static/js/components/ProcessDiagram.js',
  '/static/vendor/js/vue.js',
  '/static/vendor/js/vuetify-labs.v3.js',
  '/static/vendor/js/vuex.js',
  '/static/vendor/js/vue-router.js',
  '/static/vendor/css/roboto.css',
  '/static/vendor/css/mdi.min.css',
  '/static/vendor/css/vuetify-labs.v3.css',
  '/static/vendor/css/vue-multiselect.min.css',
  '/static/css/main.css',
  '/static/css/process_diagram.css',
  '/manifest.json'
];

// Install event - cache static assets
self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then((cache) => cache.addAll(STATIC_ASSETS))
      .then(() => self.skipWaiting())
  );
});

// Activate event - clean old caches
self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((keys) => {
      return Promise.all(
        keys.filter((key) => key !== CACHE_NAME)
          .map((key) => caches.delete(key))
      );
    }).then(() => self.clients.claim())
  );
});

// Fetch event - cache-first strategy for static assets
self.addEventListener('fetch', (event) => {
  const url = new URL(event.request.url);

  // Skip caching for API calls and WebSocket
  if (url.pathname.startsWith('/api/') ||
      url.pathname.startsWith('/socket.io/')) {
    return;
  }

  event.respondWith(
    caches.match(event.request)
      .then((cachedResponse) => {
        if (cachedResponse) {
          return cachedResponse;
        }
        return fetch(event.request)
          .then((response) => {
            // Don't cache non-successful responses
            if (!response || response.status !== 200) {
              return response;
            }
            // Cache the new response
            const responseClone = response.clone();
            caches.open(CACHE_NAME)
              .then((cache) => cache.put(event.request, responseClone));
            return response;
          })
          .catch(() => {
            // Offline fallback - return cached app shell
            if (event.request.mode === 'navigate') {
              return caches.match('/');
            }
          });
      })
  );
});
```

#### Service Worker Registration

Add to `main.html` after app initialization:

```html
<!-- Service Worker Registration -->
<script>
  if ('serviceWorker' in navigator) {
    window.addEventListener('load', () => {
      navigator.serviceWorker.register('/sw.js')
        .then((registration) => {
          console.log('Service Worker registered:', registration.scope);
        })
        .catch((error) => {
          console.log('Service Worker registration failed:', error);
        });
    });
  }
</script>
```

**UX Consideration:** Register on `window.load` to avoid competing with initial page render for bandwidth.

---

### 3. Installation Flow Recommendations

#### iOS Safari Installation UX

**Current State:** iOS Safari does not show a standard "Add to Home Screen" prompt like Android. Users must manually install via Share menu.

**User Flow:**

```
1. User opens app in Safari
2. User taps Share button (square with up arrow)
3. User scrolls to "Add to Home Screen"
4. User taps "Add" in top-right corner
5. User names the app (pre-filled from manifest)
6. User taps "Add" to confirm
7. App icon appears on home screen
8. User taps icon to launch in standalone mode
```

**Developer Guidance Needed:**
1. Detect iOS Safari and show installation instructions
2. Provide visual cue that app is installable
3. Explain that push notifications require standalone mode

#### Installation Detection

```javascript
// Detect if running as installed PWA
const isStandalone = window.matchMedia('(display-mode: standalone)').matches ||
                     window.navigator.standalone === true;

// Detect iOS Safari
const isIOS = /iPad|iPhone|iPod/.test(navigator.userAgent) && !window.MSStream;
const isSafari = /Safari/.test(navigator.userAgent) && !/Chrome/.test(navigator.userAgent);

// Show install prompt for iOS Safari users not in standalone mode
if (isIOS && isSafari && !isStandalone) {
  // Show "Add to Home Screen" instructions
  showIOSInstallPrompt();
}
```

#### Installation Prompt UI Recommendation

For iOS Safari users not in standalone mode, show a dismissible banner:

```
+----------------------------------------------------------+
| [App Icon]  Add to Home Screen                           |
|             Tap the Share button, then "Add to Home     |
|             Screen" to install this app.                 |
|                                                          |
|             [Maybe Later] [Show Me How]                  |
+----------------------------------------------------------+
```

**Implementation Notes:**
- Show on first visit (store in localStorage)
- Allow dismissal
- Link to help documentation for step-by-step instructions
- Required for task-6.3 (push notification permission requires standalone mode)

---

### 4. iOS-Specific UX Considerations

#### iOS Safari Limitations

| Feature | iOS Safari | Android Chrome |
|---------|------------|-----------------|
| Installation prompt | Manual (Share menu) | Automatic prompt |
| Push notifications | Standalone mode only | Always available |
| Background sync | Not supported | Supported |
| Periodic sync | Not supported | Supported |
| Third-party browsers | No push notifications | Full PWA support |

#### Critical iOS Requirements

1. **Standalone Mode is Mandatory for Push**
   - Push notifications ONLY work when app is installed to home screen
   - Standard Safari tabs cannot receive push notifications
   - Third-party browsers (Chrome, Firefox on iOS) cannot receive push notifications

2. **User Action Required for Permission Prompt**
   - `Notification.requestPermission()` must be triggered by user action (click)
   - Cannot prompt on page load
   - Must provide a "Subscribe" or "Enable Notifications" button

3. **Icon Requirements**
   - 180x180: Required for iOS home screen
   - 192x192: Required for Android
   - Both must be present in manifest

4. **Status Bar Behavior**
   - `black-translucent`: Status bar is transparent, content extends behind
   - `default`: White status bar with black text
   - `black`: Black status bar with white text
   - Recommendation: Use `black-translucent` for immersive experience matching theme

#### Offline User Experience

**When Offline:**
1. App shell loads from cache (instant)
2. API calls fail gracefully
3. Show offline indicator in UI
4. Queue actions for sync when online (future enhancement)

**Offline Indicator UI:**
```
+------------------------------------------+
| [App Title]              [Offline Badge] |
+------------------------------------------+
```

Implementation in app.js or store.js:
```javascript
// Track online/offline status in Vuex store
const store = Vuex.createStore({
  state: {
    isOnline: navigator.onLine,
    // ... other state
  },
  mutations: {
    setOnline(state, isOnline) {
      state.isOnline = isOnline;
    }
  }
});

// Listen for connectivity changes
window.addEventListener('online', () => store.commit('setOnline', true));
window.addEventListener('offline', () => store.commit('setOnline', false));
```

---

## API Dependencies

This task has the following API requirements that need coordination:

### Backend Requirements (for task-6.1)

| Endpoint | Method | Purpose | Priority |
|----------|--------|---------|----------|
| `/sw.js` | GET | Serve Service Worker script | Required |
| `/manifest.json` | GET | Already implemented | Done |

### Service Worker Serving

The Service Worker script (`/sw.js`) must be:
1. Served from the root path (not `/static/`)
2. Served with `Service-Worker-Allowed: /` header if scope is root
3. Served with correct MIME type (`application/javascript`)

**Backend Implementation:**
```python
# In baseweb/__init__.py _setup_routes()
if self.settings.style == "pwa":
    self.route("/sw.js", endpoint="service-worker")(self._serve_service_worker())

async def _serve_service_worker(self):
    sw_path = HERE / "static" / "js" / "sw.js"
    content = await send_from_directory(sw_path.parent, sw_path.name)
    # Set correct headers
    response = Response(content, mimetype="application/javascript")
    response.headers["Service-Worker-Allowed"] = "/"
    return response
```

### Future API Dependencies (task-6.2, task-6.3)

| Endpoint | Method | Purpose | Task |
|----------|--------|---------|------|
| `/api/vapid-public-key` | GET | Get public VAPID key | task-6.2 |
| `/api/push-subscription` | POST | Store push subscription | task-6.2 |
| `/api/push-subscription` | DELETE | Remove push subscription | task-6.2 |

---

## Acceptance Criteria Review

From TODO.md:

| Criteria | Status | Notes |
|----------|--------|-------|
| PWA installs on iOS Home Screen from Safari | Pending | Need 180x180 icon and meta tags |
| App launches in standalone mode | OK | `display: "standalone"` already set |
| Works offline with cached assets | Pending | Need Service Worker implementation |
| Tested on iOS 16.4+ device or simulator | Pending | Requires testing infrastructure |

---

## Implementation Checklist

### Manifest Changes

- [ ] Add 180x180 icon to manifest.json template
- [ ] Add `description` field to manifest.json
- [ ] Add `scope: "/"` to manifest.json
- [ ] Add iOS-specific meta tags to main.html

### Service Worker Implementation

- [ ] Create `src/baseweb/static/js/sw.js`
- [ ] Implement install event handler (cache static assets)
- [ ] Implement activate event handler (clean old caches)
- [ ] Implement fetch event handler (cache-first strategy)
- [ ] Add Service Worker route in backend
- [ ] Register Service Worker in main.html

### Icon Assets

- [ ] Generate 180x180 icon for iOS
- [ ] Ensure all icon sizes are generated from same source

### Testing

- [ ] Test PWA installation on iOS Safari (iOS 16.4+)
- [ ] Test offline functionality
- [ ] Test standalone mode launch
- [ ] Verify manifest served correctly
- [ ] Verify Service Worker registered

---

## Files to Modify/Create

| File | Action | Purpose |
|------|--------|---------|
| `src/baseweb/templates/manifest.json` | Modify | Add 180x180 icon, description, scope |
| `src/baseweb/templates/main.html` | Modify | Add iOS meta tags, Service Worker registration |
| `src/baseweb/static/js/sw.js` | Create | Service Worker implementation |
| `src/baseweb/__init__.py` | Modify | Add Service Worker route |

---

## Risks and Mitigations

| Risk | Impact | Likelihood | Mitigation |
|------|--------|------------|------------|
| iOS 16.4+ requirement limits user base | Medium | High | Document clearly, check version at runtime |
| Service Worker caching breaks updates | High | Medium | Use cache versioning, implement update check |
| Icons not generated for all sizes | Low | Medium | Provide icon generation tool/script |
| Offline mode confuses users | Medium | Low | Show clear offline indicator |

---

## References

- [Apple Developer: Configuring Web Apps](https://developer.apple.com/library/archive/documentation/AppleApplications/Conceptual/SafariWebContent/ConfiguringWebApp/ConfiguringWebApp.html)
- [MDN: Web App Manifest](https://developer.mozilla.org/en-US/docs/Web/Manifest)
- [MDN: Service Worker API](https://developer.mozilla.org/en-US/docs/Web/API/Service_Worker_API)
- [Web.dev: Progressive Web Apps](https://web.dev/progressive-web-apps/)
- [iOS 16.4 Web Push Requirements](https://developer.apple.com/documentation/usernotifications/sending_web_push_notifications_in_safari_and_other_browsers)

---

*Analysis prepared by: UI/UX Designer Agent*
*Date: 2026-05-19*
*Version: 1.0*