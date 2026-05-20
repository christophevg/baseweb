// Service Worker for baseweb PWA
const CACHE_NAME = 'baseweb-v1';
const STATIC_ASSETS = [
  '/',
  // Core JS files
  '/static/js/app.js',
  '/static/js/store.js',
  '/static/js/router.js',
  '/static/js/common.js',
  '/static/js/socketio.js',
  // Components
  '/static/js/components/Page.js',
  '/static/js/components/CollectionView.js',
  '/static/js/components/NotificationSnackbar.js',
  '/static/js/components/VuetifyFormGenerator.js',
  '/static/js/components/LineChart.js',
  '/static/js/components/NavigationDrawer.js',
  '/static/js/components/ProcessDiagram.js',
  // Vendor JS - Core
  '/static/vendor/js/vue.js',
  '/static/vendor/js/vuex.js',
  '/static/vendor/js/vue-router.js',
  '/static/vendor/js/socket.io.slim.js',
  '/static/vendor/js/Chart.min.js',
  '/static/vendor/js/jquery.min.js',
  '/static/vendor/js/bootstrap.min.js',
  '/static/vendor/js/moment.min.js',
  '/static/vendor/js/bootstrap-datetimepicker.min.js',
  '/static/vendor/js/highlight.min.js',
  '/static/vendor/js/vue-multiselect.min.js',
  // Vendor JS - Vuetify (both v3 and v4 for different templates)
  '/static/vendor/js/vuetify-labs.v3.js',
  '/static/vendor/js/vuetify-labs.v4.js',
  // Vendor CSS
  '/static/vendor/css/roboto.css',
  '/static/vendor/css/mdi.min.css',
  '/static/vendor/css/vue-multiselect.min.css',
  '/static/vendor/css/bootstrap-datetimepicker.css',
  '/static/vendor/css/highlight.js.github.css',
  // Vendor CSS - Vuetify (both v3 and v4)
  '/static/vendor/css/vuetify-labs.v3.css',
  '/static/vendor/css/vuetify-labs.v4.css',
  // Core CSS
  '/static/css/main.css',
  '/static/css/process_diagram.css',
  // PWA manifest
  '/manifest.json'
  // TODO: Consider bundling all static files into a single JS/CSS file
  // for optimal caching and to avoid hardcoding vendor versions.
  // See: https://github.com/christophevg/baseweb/issues/XXX
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

// Handle push event
self.addEventListener('push', (event) => {
  if (!event.data) return;

  try {
    const payload = event.data.json();
    const title = payload.title || 'New Notification';
    const options = {
      body: payload.body || 'You have a new update.',
      data: { url: payload.url }
    };

    event.waitUntil(
      self.registration.showNotification(title, options)
    );
  } catch (e) {
    console.error('Error handling push event:', e);
  }
});

// Handle notification click event
self.addEventListener('notificationclick', (event) => {
  event.waitUntil(
    clients.matchAll({ type: 'window', includeUncontrolled: true }).then((clientList) => {
      const urlToOpen = event.notification.data?.url;

      // Security check: Validate URL starts with https://
      if (urlToOpen && urlToOpen.startsWith('https://')) {
        // If a window is already open, focus it and navigate
        for (const client of clientList) {
          if (client.url === urlToOpen && 'focus' in client) {
            return client.focus();
          }
        }
        // Otherwise open a new window
        if (clients.openWindow) {
          return clients.openWindow(urlToOpen);
        }
      } else {
        // Fallback to app root if URL is invalid or missing
        if (clients.openWindow) {
          return clients.openWindow('/');
        }
      }
    })
  );
});
