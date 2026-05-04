/**
 * Vuex Store for Baseweb
 *
 * This store provides centralized state management including:
 * - Notification system for Vuetify snackbar integration
 * - Placeholder for other modules (drawer module added by NavigationDrawer.js)
 */

var store = Vuex.createStore({
  modules: {},

  state: {
    notification: {
      showing: false,
      text: '',
      title: '',
      color: 'info',
      timeout: 4000,
      location: 'bottom right'
    }
  },

  mutations: {
    // Show a notification
    notify: function(state, payload) {
      // Support both simple string and object payload
      if (typeof payload === 'string') {
        state.notification.text = payload;
        state.notification.title = '';
      } else {
        state.notification.text = payload.text || payload.message || '';
        state.notification.title = payload.title || '';
        state.notification.color = payload.type || payload.color || 'info';
        state.notification.timeout = payload.timeout || 4000;
        state.notification.location = payload.location || 'bottom right';
      }
      state.notification.showing = true;
    },

    // Hide the notification
    hide_notification: function(state) {
      state.notification.showing = false;
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

    hideNotification: function(context) {
      context.commit('hide_notification');
    }
  },

  getters: {
    notification: function(state) {
      return state.notification;
    }
  }
});

// Global convenience function for notifications (replaces app.$notify)
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