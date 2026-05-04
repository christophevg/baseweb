/**
 * Vuex Store for Baseweb
 *
 * Provides centralized state management including:
 * - App configuration from backend
 * - Notification system for Vuetify snackbar integration (queue-based)
 */

var notificationId = 0;

var store = Vuex.createStore({
  state: {
    config : {{ app.toDict() | tojson }},
    notifications: []  // Queue of notifications
  },

  mutations: {
    // Add a notification to the queue
    notify: function(state, payload) {
      // Support both simple string and object payload
      var notification;
      if (typeof payload === 'string') {
        notification = {
          id: ++notificationId,
          text: payload,
          title: '',
          color: 'info',
          timeout: 4000
        };
      } else {
        notification = {
          id: ++notificationId,
          text: payload.text || payload.message || '',
          title: payload.title || '',
          color: payload.type || payload.color || 'info',
          timeout: payload.timeout || 4000
        };
      }
      state.notifications.push(notification);
    },

    // Remove a notification from the queue
    remove_notification: function(state, id) {
      var index = state.notifications.findIndex(function(n) {
        return n.id === id;
      });
      if (index !== -1) {
        state.notifications.splice(index, 1);
      }
    },

    // Clear all notifications
    clear_notifications: function(state) {
      state.notifications = [];
    },

    // Convenience mutations for different notification types
    notify_success: function(state, payload) {
      var options = typeof payload === 'string' ? { text: payload } : payload;
      options.color = 'success';
      store.commit('notify', options);
    },

    notify_error: function(state, payload) {
      var options = typeof payload === 'string' ? { text: payload } : payload;
      options.color = 'error';
      store.commit('notify', options);
    },

    notify_warning: function(state, payload) {
      var options = typeof payload === 'string' ? { text: payload } : payload;
      options.color = 'warning';
      store.commit('notify', options);
    },

    notify_info: function(state, payload) {
      var options = typeof payload === 'string' ? { text: payload } : payload;
      options.color = 'info';
      store.commit('notify', options);
    }
  },

  actions: {
    // Async notification action
    showNotification: function(context, payload) {
      context.commit('notify', payload);
    },

    removeNotification: function(context, id) {
      context.commit('remove_notification', id);
    },

    clearNotifications: function(context) {
      context.commit('clear_notifications');
    }
  },

  getters: {
    notifications: function(state) {
      return state.notifications;
    }
  }
});

// Global convenience functions for notifications (replaces app.$notify)
window.notify = function(options) {
  store.commit('notify', options);
};

window.notifySuccess = function(text, title) {
  store.commit('notify_success', { text: text, title: title });
};

window.notifyError = function(text, title) {
  store.commit('notify_error', { text: text, title: title });
};

window.notifyWarning = function(text, title) {
  store.commit('notify_warning', { text: text, title: title });
};

window.notifyInfo = function(text, title) {
  store.commit('notify_info', { text: text, title: title });
};