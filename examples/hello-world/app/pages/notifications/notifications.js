/**
 * PushNotificationSettings - Component for managing push notification subscriptions.
 *
 * This is a page component for the hello-world example.
 * Uses Vuex store for state management to avoid redundant API calls.
 */

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
              :loading="subscribing"
            >
              Enable
            </v-btn>
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
                :loading="unsubscribing"
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

    <!-- PWA Updates - Only show in standalone mode -->
    <v-card v-if="isStandalone" variant="outlined" class="pa-4">
      <v-card-title class="text-h6">App Updates</v-card-title>
      <v-card-text>
        <div class="d-flex align-center justify-space-between">
          <div>
            <div class="text-body-1">Refresh App</div>
            <div class="text-caption">Reload the app to get the latest version.</div>
          </div>
          <v-btn
            color="primary"
            variant="outlined"
            prepend-icon="mdi-refresh"
            @click="reloadApp"
          >
            Reload
          </v-btn>
        </div>
      </v-card-text>
    </v-card>
  </page>
  `,
  data: function() {
    return {
      // Local UI state
      subscribing: false,
      unsubscribing: false,
      sendingNotification: false,
      incrementingBadge: false,
      showSnackbar: false,
      snackbarMessage: '',
      snackbarColor: 'success',
      isStandalone: false,
      isSupported: true,
      isSecure: true
    };
  },
  computed: {
    // Get state from Vuex store
    status: function() {
      return this.$store.state.push.subscriptionStatus;
    },
    errorMessage: function() {
      return this.$store.state.push.subscriptionError;
    },
    vapidKey: function() {
      return this.$store.state.push.vapidKey;
    }
  },
  methods: {
    checkSupport: function() {
      const isIOS = /iPad|iPhone|iPod/.test(navigator.userAgent) && !window.MSStream;
      const isStandalone = window.navigator.standalone === true;
      const isSecure = window.location.protocol === 'https:' || window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1';

      this.isSecure = isSecure;
      this.isStandalone = isStandalone;

      // Push API requires HTTPS (or localhost)
      if (!isSecure) {
        this.isSupported = false;
        return;
      }

      if (isIOS && !isStandalone) {
        this.isSupported = false;
      } else if (!('PushManager' in window)) {
        this.isSupported = false;
      }
    },
    async subscribe() {
      this.subscribing = true;
      const result = await this.$store.dispatch('push/subscribe');
      this.subscribing = false;

      if (result === 'subscribed') {
        this.showSnackbar = true;
        this.snackbarMessage = 'Notifications enabled!';
        this.snackbarColor = 'success';
      }
    },
    async unsubscribe() {
      this.unsubscribing = true;
      const result = await this.$store.dispatch('push/unsubscribe');
      this.unsubscribing = false;

      if (result === 'unsubscribed') {
        this.showSnackbar = true;
        this.snackbarMessage = 'Notifications disabled.';
        this.snackbarColor = 'success';
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
        this.snackbarMessage = 'Notification sent to ' + result.sent + ' device(s)';
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
        if ('setAppBadge' in navigator) {
          const currentBadge = parseInt(localStorage.getItem('badgeCount') || '0', 10);
          const newBadge = currentBadge + 1;

          await navigator.setAppBadge(newBadge);
          localStorage.setItem('badgeCount', String(newBadge));

          this.showSnackbar = true;
          this.snackbarMessage = 'Badge count: ' + newBadge;
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
    },
    reloadApp() {
      window.location.reload();
    }
  },
  mounted: async function() {
    this.checkSupport();

    // Initialize badge count from localStorage
    if (!localStorage.getItem('badgeCount')) {
      localStorage.setItem('badgeCount', '0');
    }

    // Fetch VAPID key (only once per session, cached in store)
    await this.$store.dispatch('push/fetchVapidKey');

    // Check subscription status (only once per session)
    if (this.isSupported && this.isSecure) {
      await this.$store.dispatch('push/checkSubscription');
    }
  }
};

Navigation.add(PushNotificationSettings);