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

          <div v-else-if="status === 'subscribed'" class="d-flex align-center justify-space-between">
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
      vapidKey: null // Pre-fetched VAPID key
    };
  },
  mounted: function() {
    this.checkSupport();
    this.fetchVapidKey();
    this.updateSubscriptionStatus();
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
        this.status = 'unsubscribed'; // Ready for subscription
      } catch (e) {
        console.error('Failed to fetch VAPID key:', e);
        this.status = 'error';
        this.errorMessage = 'Could not load notification settings. Please try again later.';
      }
    },
    async updateSubscriptionStatus() {
      try {
        const registration = await navigator.serviceWorker.ready;
        const subscription = await registration.pushManager.getSubscription();
        if (subscription) {
          this.status = 'subscribed';
        }
      } catch (e) {
        console.error('Failed to get subscription status:', e);
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
        this.status = 'unsubscribed';
        if (window.notifySuccess) window.notifySuccess('Notifications disabled.');
      } catch (e) {
        console.error('Unsubscribe error:', e);
        this.status = 'error';
        this.errorMessage = 'Failed to disable notifications.';
      }
    }
  }
};

Navigation.add(PushNotificationSettings);