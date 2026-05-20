/**
 * PushNotificationSettings - Component for managing push notification subscriptions.
 *
 * This is a page component for the hello-world example.
 */

function urlBase64ToUint8Array(base64String) {
  const padding = '='.repeat((4 - base64String.length % 4) % 4);
  const base64 = (base64String + padding).replace(/-/g, '+').replace(/_/g, '/');
  const rawData = window.atob(base64);
  const outputArray = new Uint8Array(rawData.length);
  for (let i = 0; i < rawData.length; ++i) {
    outputArray[i] = rawData.charCodeAt(i);
  }
  return outputArray;
}

function arrayBufferToBase64Url(buffer) {
  const bytes = new Uint8Array(buffer);
  let binary = '';
  for (const byte of bytes) binary += String.fromCharCode(byte);
  return window.btoa(binary)
    .replace(/\+/g, '-')
    .replace(/\//g, '_')
    .replace(/=+$/, '');
}

const PushNotificationSettings = {
  navigation: {
    path: '/settings/notifications',
    text: 'Notifications',
    icon: 'mdi-bell',
    index: 10
  },
  template: `
  <page title="Notifications" banner="Manage your push notification settings">
    <v-card variant="outlined" class="pa-4 mb-4">
      <v-card-title class="text-h6">Push Notifications</v-card-title>
      <v-card-text>
        <div v-if="!isSecure" class="text-body-2 mb-4">
          <v-alert type="error" variant="tonal" class="mb-4">
            Push notifications require HTTPS or localhost.
          </v-alert>
          <div class="text-caption">
            You are accessing via HTTP on a network IP. To enable push notifications:
            <ol class="pl-4 mt-2">
              <li class="mb-1">Test on <strong>localhost</strong> directly on this machine, or</li>
              <li class="mb-1">Use an HTTPS tunnel like <strong>ngrok</strong> for mobile testing.</li>
            </ol>
          </div>
        </div>

        <div v-else-if="!isSupported" class="text-body-2 mb-4">
          <v-alert type="info" variant="tonal" class="mb-4">
            Push notifications are only available in the installed app.
          </v-alert>
          <div class="text-caption">
            To receive notifications, please add baseweb to your Home Screen:
            <ol class="pl-4 mt-2">
              <li class="mb-1">Tap the <v-icon size="small">mdi-share-variant</v-icon> button in Safari.</li>
              <li class="mb-1">Select "Add to Home Screen".</li>
              <li class="mb-1">Open the app from your Home Screen.</li>
            </ol>
          </div>
        </div>

        <div v-else>
          <div v-if="status === 'checking'" class="d-flex align-center">
            <v-progress-circular indeterminate color="primary" size="24" class="mr-3"></v-progress-circular>
            <span class="text-body-1">Loading notification settings...</span>
          </div>

          <div v-else-if="status === 'unsubscribed'" class="d-flex align-center justify-space-between">
            <div>
              <div class="text-body-1">Enable Notifications</div>
              <div class="text-caption">Get instant updates about your data and alerts.</div>
            </div>
            <v-btn
              color="primary"
              prepend-icon="mdi-bell-outline"
              @click="subscribe"
            >
              Enable
            </v-btn>
          </div>

          <div v-else-if="status === 'subscribing'" class="d-flex align-center">
            <v-progress-circular indeterminate color="primary" size="24" class="mr-3"></v-progress-circular>
            <span class="text-body-1">Subscribing...</span>
          </div>

          <div v-else-if="status === 'subscribed'">
            <div class="d-flex align-center justify-space-between mb-4">
              <div>
                <div class="text-body-1">Notifications Enabled</div>
                <div class="text-caption">You will receive push updates.</div>
              </div>
              <v-btn
                variant="outlined"
                color="error"
                prepend-icon="mdi-bell-off"
                @click="unsubscribe"
              >
                Disable
              </v-btn>
            </div>
            <v-divider class="mb-4"></v-divider>
            <div class="text-subtitle-2 mb-2">Test Notifications</div>
            <v-btn
              color="primary"
              prepend-icon="mdi-bell-ring"
              @click="sendTestNotification"
              :loading="sendingNotification"
              class="mr-2"
            >
              Send Test Notification
            </v-btn>
            <v-btn
              variant="outlined"
              prepend-icon="mdi-numeric"
              @click="incrementBadge"
              :loading="incrementingBadge"
              class="mr-2"
            >
              Increment Badge
            </v-btn>
            <v-btn
              variant="text"
              prepend-icon="mdi-notification-clear-all"
              @click="clearBadge"
            >
              Clear Badge
            </v-btn>
            <v-snackbar
              v-model="showSnackbar"
              :color="snackbarColor"
              :timeout="3000"
            >
              {{ snackbarMessage }}
            </v-snackbar>
          </div>

          <div v-else-if="status === 'error'" class="d-flex flex-column">
            <v-alert type="error" variant="tonal" class="mb-4">
              {{ errorMessage }}</v-alert>
            <v-btn
              color="primary"
              prepend-icon="mdi-refresh"
              @click="subscribe"
            >
              Try Again
            </v-btn>
          </div>
        </div>
      </v-card-text>
    </v-card>
  </page>
  `,
  data: function() {
    return {
      status: 'checking', // Start with 'checking' while we fetch the key
      errorMessage: '',
      isSupported: true,
      isSecure: true,
      vapidKey: null, // Pre-fetched VAPID key
      sendingNotification: false,
      incrementingBadge: false,
      showSnackbar: false,
      snackbarMessage: '',
      snackbarColor: 'success'
    };
  },
  methods: {
    checkSupport: function() {
      const isIOS = /iPad|iPhone|iPod/.test(navigator.userAgent) && !window.MSStream;
      const isStandalone = window.navigator.standalone === true;
      const isSecure = window.location.protocol === 'https:' || window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1';

      this.isSecure = isSecure;

      // Push API requires HTTPS (or localhost)
      if (!isSecure) {
        this.isSupported = false;
        this.status = 'error';
        this.errorMessage = 'Push notifications require HTTPS or localhost.';
        return;
      }

      if (isIOS && !isStandalone) {
        this.isSupported = false;
      } else if (!('PushManager' in window)) {
        this.isSupported = false;
      }
    },
    async fetchVapidKey() {
      try {
        const response = await fetch('/api/vapid-public-key', { credentials: 'include' });
        if (!response.ok) {
          throw new Error('Failed to fetch VAPID key');
        }
        const data = await response.json();
        this.vapidKey = data.public_key;

        // Store VAPID key for comparison (detects key changes)
        const storedVapidKey = localStorage.getItem('vapidKey');
        if (storedVapidKey && storedVapidKey !== this.vapidKey) {
          // VAPID key changed on server - need to re-subscribe
          console.log('VAPID key changed, will need to re-subscribe');
          this.status = 'unsubscribed';
          // Clear old subscription from browser
          await this.clearOldSubscription();
        }

        this.status = 'unsubscribed'; // Ready for subscription
      } catch (e) {
        console.error('Failed to fetch VAPID key:', e);
        this.status = 'error';
        this.errorMessage = 'Could not load notification settings. Please try again later.';
      }
    },
    async clearOldSubscription() {
      try {
        const registration = await navigator.serviceWorker.ready;
        const subscription = await registration.pushManager.getSubscription();
        if (subscription) {
          // Unsubscribe from push service
          await subscription.unsubscribe();
          console.log('Cleared old subscription (VAPID key changed)');
        }
        // Clear local badge count
        localStorage.setItem('badgeCount', '0');
      } catch (e) {
        console.error('Error clearing old subscription:', e);
      }
    },
    async updateSubscriptionStatus() {
      try {
        const registration = await navigator.serviceWorker.ready;
        const subscription = await registration.pushManager.getSubscription();
        if (subscription) {
          // Subscription exists in browser - sync with server
          const syncResult = await this.syncSubscriptionWithServer(subscription);
          if (syncResult === 'valid') {
            this.status = 'subscribed';
          } else if (syncResult === 'vapid_mismatch') {
            // Server's VAPID key doesn't match - need to re-subscribe
            console.log('VAPID key mismatch, re-subscribing...');
            await subscription.unsubscribe();
            this.status = 'unsubscribed';
          } else {
            // Sync failed - show as unsubscribed, let user re-enable
            this.status = 'unsubscribed';
          }
        }
      } catch (e) {
        console.error('Failed to get subscription status:', e);
      }
    },
    async syncSubscriptionWithServer(subscription) {
      try {
        // Try to sync subscription with server (server may have restarted)
        const syncPayload = {
          endpoint: subscription.endpoint,
          keys: {
            p256dh: arrayBufferToBase64Url(subscription.getKey('p256dh')),
            auth: arrayBufferToBase64Url(subscription.getKey('auth'))
          }
        };

        const response = await fetch('/api/push-subscriptions', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(syncPayload),
          credentials: 'include'
        });

        if (response.status === 201 || response.status === 200 || response.status === 409) {
          // Sync successful - subscription is valid
          localStorage.setItem('vapidKey', this.vapidKey);
          return 'valid';
        } else if (response.status === 400) {
          // Check if it's a VAPID mismatch error
          const error = await response.json();
          if (error.detail && error.detail.includes('VAPID')) {
            return 'vapid_mismatch';
          }
        }
        return 'unknown';
      } catch (e) {
        console.error('Failed to sync subscription with server:', e);
        return 'error';
      }
    },
    async subscribe() {
      // Check if we have the VAPID key
      if (!this.vapidKey) {
        this.status = 'error';
        this.errorMessage = 'Notification settings not loaded. Please refresh the page.';
        return;
      }

      this.status = 'subscribing';
      this.errorMessage = '';

      try {
        // Request permission FIRST (this is the user gesture)
        const permission = await Notification.requestPermission();
        if (permission !== 'granted') {
          this.status = 'error';
          this.errorMessage = 'Notification permission denied.';
          return;
        }

        // Subscribe IMMEDIATELY after permission (still in user gesture context)
        const registration = await navigator.serviceWorker.ready;
        const subscription = await registration.pushManager.subscribe({
          userVisibleOnly: true,
          applicationServerKey: urlBase64ToUint8Array(this.vapidKey)
        });

        if (!subscription || !subscription.endpoint) {
          throw new Error('Browser returned empty subscription endpoint. This usually means the VAPID key was rejected by Apple\'s push service.');
        }

        const syncPayload = {
          endpoint: subscription.endpoint,
          keys: {
            p256dh: arrayBufferToBase64Url(subscription.getKey('p256dh')),
            auth: arrayBufferToBase64Url(subscription.getKey('auth'))
          }
        };

        const syncResponse = await fetch('/api/push-subscriptions', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(syncPayload),
          credentials: 'include'
        });
        if (syncResponse.status === 401) { window.location.href = '/login'; return; }
        if (syncResponse.status === 201 || syncResponse.status === 200 || syncResponse.status === 409) {
          this.status = 'subscribed';
          // Store VAPID key for comparison
          localStorage.setItem('vapidKey', this.vapidKey);
          if (window.notifySuccess) window.notifySuccess('Notifications enabled!');
        } else {
          throw new Error('Failed to register subscription with server.');
        }
      } catch (e) {
        console.error('Subscription error:', e);
        this.status = 'error';
        this.errorMessage = e.message || 'An unexpected error occurred.';
      }
    },
    async unsubscribe() {
      this.status = 'subscribing';
      try {
        const registration = await navigator.serviceWorker.ready;
        const subscription = await registration.pushManager.getSubscription();
        if (subscription) {
          const unsubResponse = await fetch('/api/push-subscriptions', {
            method: 'DELETE',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ endpoint: subscription.endpoint }),
            credentials: 'include'
          });
          if (unsubResponse.status === 401) { window.location.href = '/login'; return; }
          await subscription.unsubscribe();
        }
        // Clear stored VAPID key and badge count
        localStorage.removeItem('vapidKey');
        localStorage.setItem('badgeCount', '0');
        // Clear app badge
        if ('clearAppBadge' in navigator) {
          await navigator.clearAppBadge().catch(() => {});
        }
        this.status = 'unsubscribed';
        if (window.notifySuccess) window.notifySuccess('Notifications disabled.');
      } catch (e) {
        console.error('Unsubscribe error:', e);
        this.status = 'error';
        this.errorMessage = 'Failed to disable notifications.';
      }
    },
    async sendTestNotification() {
      this.sendingNotification = true;
      try {
        const response = await fetch('/api/push-notifications', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            title: 'Test Notification',
            body: 'This is a test push notification from baseweb!',
            url: window.location.origin
          }),
          credentials: 'include'
        });

        if (response.status === 401) {
          window.location.href = '/login';
          return;
        }

        if (!response.ok) {
          const errorData = await response.json();
          throw new Error(errorData.detail || 'Failed to send notification');
        }

        const result = await response.json();
        this.showSnackbar = true;
        this.snackbarMessage = `Notification sent to ${result.sent} device(s)`;
        this.snackbarColor = 'success';
      } catch (e) {
        console.error('Send notification error:', e);
        this.showSnackbar = true;
        this.snackbarMessage = e.message || 'Failed to send notification';
        this.snackbarColor = 'error';
      } finally {
        this.sendingNotification = false;
      }
    },
    async incrementBadge() {
      this.incrementingBadge = true;
      try {
        // Check if Badging API is supported
        if ('setAppBadge' in navigator) {
          // Get current badge count from localStorage
          const currentBadge = await this.getCurrentBadgeCount();
          const newBadge = currentBadge + 1;

          // Set badge and save to localStorage
          await navigator.setAppBadge(newBadge);
          localStorage.setItem('badgeCount', String(newBadge));

          this.showSnackbar = true;
          this.snackbarMessage = `Badge count: ${newBadge}`;
          this.snackbarColor = 'success';
        } else {
          this.showSnackbar = true;
          this.snackbarMessage = 'Badge API not supported on this device';
          this.snackbarColor = 'warning';
        }
      } catch (e) {
        console.error('Badge increment error:', e);
        this.showSnackbar = true;
        this.snackbarMessage = 'Failed to increment badge';
        this.snackbarColor = 'error';
      } finally {
        this.incrementingBadge = false;
      }
    },
    async getCurrentBadgeCount() {
      // Try to get badge count from service worker or default to 0
      // Note: The Badging API doesn't provide a way to read current badge count
      // We track it in localStorage for this demo
      const count = parseInt(localStorage.getItem('badgeCount') || '0', 10);
      return count;
    },
    async clearBadge() {
      try {
        if ('clearAppBadge' in navigator) {
          await navigator.clearAppBadge();
          localStorage.setItem('badgeCount', '0');
          this.showSnackbar = true;
          this.snackbarMessage = 'Badge cleared';
          this.snackbarColor = 'success';
        } else {
          this.showSnackbar = true;
          this.snackbarMessage = 'Badge API not supported';
          this.snackbarColor = 'warning';
        }
      } catch (e) {
        console.error('Clear badge error:', e);
      }
    }
  },
  mounted: function() {
    // Initialize badge count in localStorage if not present
    if (!localStorage.getItem('badgeCount')) {
      localStorage.setItem('badgeCount', '0');
    }
    this.checkSupport();
    this.fetchVapidKey().then(() => {
      // After fetching VAPID key, check if we have an existing subscription
      this.updateSubscriptionStatus();
    });
  }
};

Navigation.add(PushNotificationSettings);