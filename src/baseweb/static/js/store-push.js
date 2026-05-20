/**
 * Push Notifications Vuex Store Module
 *
 * Manages VAPID key and subscription state centrally to avoid
 * redundant API calls when navigating between pages.
 */

var pushModule = {
  namespaced: true,
  state: {
    // VAPID public key (fetched once per session)
    vapidKey: null,
    vapidKeyLoading: false,
    vapidKeyError: null,

    // Subscription state
    subscription: null,        // PushSubscription object from browser
    subscriptionStatus: null,  // 'checking', 'unsubscribed', 'subscribed', 'error'
    serverSubscription: null, // Subscription synced with server
    subscriptionError: null,

    // Badge count (for demo purposes)
    badgeCount: 0
  },
  mutations: {
    SET_VAPID_KEY: function(state, key) {
      state.vapidKey = key;
      state.vapidKeyLoading = false;
      state.vapidKeyError = null;
    },
    SET_VAPID_KEY_LOADING: function(state, loading) {
      state.vapidKeyLoading = loading;
    },
    SET_VAPID_KEY_ERROR: function(state, error) {
      state.vapidKeyError = error;
      state.vapidKeyLoading = false;
    },
    SET_SUBSCRIPTION: function(state, subscription) {
      state.subscription = subscription;
    },
    SET_SUBSCRIPTION_STATUS: function(state, status) {
      state.subscriptionStatus = status;
    },
    SET_SERVER_SUBSCRIPTION: function(state, serverSub) {
      state.serverSubscription = serverSub;
    },
    SET_SUBSCRIPTION_ERROR: function(state, error) {
      state.subscriptionError = error;
    },
    SET_BADGE_COUNT: function(state, count) {
      state.badgeCount = count;
      localStorage.setItem('badgeCount', String(count));
    },
    CLEAR_PUSH_STATE: function(state) {
      state.vapidKey = null;
      state.subscription = null;
      state.subscriptionStatus = null;
      state.serverSubscription = null;
      state.subscriptionError = null;
      localStorage.removeItem('vapidKey');
      localStorage.setItem('badgeCount', '0');
    }
  },
  actions: {
    // Fetch VAPID key from server (only once per session)
    fetchVapidKey: async function(context) {
      // Return cached key if available
      if (context.state.vapidKey) {
        return context.state.vapidKey;
      }

      // Avoid duplicate requests
      if (context.state.vapidKeyLoading) {
        return null;
      }

      context.commit('SET_VAPID_KEY_LOADING', true);

      try {
        const response = await fetch('/api/vapid-public-key', { credentials: 'include' });
        if (!response.ok) {
          throw new Error('Failed to fetch VAPID key');
        }
        const data = await response.json();
        context.commit('SET_VAPID_KEY', data.public_key);
        return data.public_key;
      } catch (error) {
        context.commit('SET_VAPID_KEY_ERROR', error.message);
        return null;
      }
    },

    // Check existing subscription in browser and sync with server
    checkSubscription: async function(context) {
      context.commit('SET_SUBSCRIPTION_STATUS', 'checking');

      try {
        const registration = await navigator.serviceWorker.ready;
        const subscription = await registration.pushManager.getSubscription();

        if (subscription) {
          context.commit('SET_SUBSCRIPTION', subscription);

          // Check if VAPID key changed
          const storedVapidKey = localStorage.getItem('vapidKey');
          const currentVapidKey = context.state.vapidKey;

          if (storedVapidKey && currentVapidKey && storedVapidKey !== currentVapidKey) {
            // VAPID key changed - need to re-subscribe
            await subscription.unsubscribe();
            context.commit('SET_SUBSCRIPTION', null);
            context.commit('SET_SUBSCRIPTION_STATUS', 'unsubscribed');
            return 'unsubscribed';
          }

          // Sync with server (server may have restarted)
          const syncResult = await context.dispatch('syncSubscriptionWithServer', subscription);

          if (syncResult === 'valid') {
            context.commit('SET_SUBSCRIPTION_STATUS', 'subscribed');
            return 'subscribed';
          } else if (syncResult === 'vapid_mismatch') {
            // VAPID mismatch - need to re-subscribe
            await subscription.unsubscribe();
            context.commit('SET_SUBSCRIPTION', null);
            context.commit('SET_SUBSCRIPTION_STATUS', 'unsubscribed');
            return 'unsubscribed';
          } else {
            context.commit('SET_SUBSCRIPTION_STATUS', 'unsubscribed');
            return 'unsubscribed';
          }
        } else {
          context.commit('SET_SUBSCRIPTION_STATUS', 'unsubscribed');
          return 'unsubscribed';
        }
      } catch (error) {
        console.error('Error checking subscription:', error);
        context.commit('SET_SUBSCRIPTION_STATUS', 'error');
        context.commit('SET_SUBSCRIPTION_ERROR', error.message);
        return 'error';
      }
    },

    // Sync subscription with server
    syncSubscriptionWithServer: async function(context, subscription) {
      try {
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
          // Store VAPID key for comparison
          if (context.state.vapidKey) {
            localStorage.setItem('vapidKey', context.state.vapidKey);
          }
          return 'valid';
        } else if (response.status === 400) {
          const error = await response.json();
          if (error.detail && error.detail.includes('VAPID')) {
            return 'vapid_mismatch';
          }
        }
        return 'unknown';
      } catch (error) {
        console.error('Error syncing subscription with server:', error);
        return 'error';
      }
    },

    // Subscribe to push notifications
    subscribe: async function(context) {
      const vapidKey = context.state.vapidKey;
      if (!vapidKey) {
        context.commit('SET_SUBSCRIPTION_ERROR', 'VAPID key not loaded');
        return 'error';
      }

      context.commit('SET_SUBSCRIPTION_STATUS', 'subscribing');

      try {
        // Request permission
        const permission = await Notification.requestPermission();
        if (permission !== 'granted') {
          context.commit('SET_SUBSCRIPTION_STATUS', 'error');
          context.commit('SET_SUBSCRIPTION_ERROR', 'Notification permission denied');
          return 'error';
        }

        // Subscribe
        const registration = await navigator.serviceWorker.ready;
        const subscription = await registration.pushManager.subscribe({
          userVisibleOnly: true,
          applicationServerKey: urlBase64ToUint8Array(vapidKey)
        });

        if (!subscription || !subscription.endpoint) {
          throw new Error('Browser returned empty subscription endpoint');
        }

        // Sync with server
        const syncResult = await context.dispatch('syncSubscriptionWithServer', subscription);

        if (syncResult === 'valid') {
          context.commit('SET_SUBSCRIPTION', subscription);
          context.commit('SET_SUBSCRIPTION_STATUS', 'subscribed');
          return 'subscribed';
        } else {
          throw new Error('Failed to register subscription with server');
        }
      } catch (error) {
        console.error('Subscription error:', error);
        context.commit('SET_SUBSCRIPTION_STATUS', 'error');
        context.commit('SET_SUBSCRIPTION_ERROR', error.message);
        return 'error';
      }
    },

    // Unsubscribe from push notifications
    unsubscribe: async function(context) {
      try {
        const subscription = context.state.subscription;
        if (subscription) {
          await fetch('/api/push-subscriptions', {
            method: 'DELETE',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ endpoint: subscription.endpoint }),
            credentials: 'include'
          });
          await subscription.unsubscribe();
        }

        // Clear stored VAPID key and badge
        localStorage.removeItem('vapidKey');
        localStorage.setItem('badgeCount', '0');
        if ('clearAppBadge' in navigator) {
          await navigator.clearAppBadge().catch(function() {});
        }

        context.commit('CLEAR_PUSH_STATE');
        return 'unsubscribed';
      } catch (error) {
        console.error('Unsubscribe error:', error);
        return 'error';
      }
    }
  },
  getters: {
    vapidKey: function(state) { return state.vapidKey; },
    isSubscribed: function(state) { return state.subscriptionStatus === 'subscribed'; },
    subscriptionStatus: function(state) { return state.subscriptionStatus; },
    badgeCount: function(state) { return state.badgeCount; }
  }
};

// Helper functions (duplicated from component for store use)
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
  for (const byte of bytes) {
    binary += String.fromCharCode(byte);
  }
  return window.btoa(binary)
    .replace(/\+/g, '-')
    .replace(/\//g, '_')
    .replace(/=+$/, '');
}

// Register module with store if store exists
if (typeof store !== 'undefined') {
  store.registerModule('push', pushModule);
}