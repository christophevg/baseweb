/**
 * NotificationSnackbar - Vuetify 3 notification component
 *
 * Replaces vue-notification with a Vuetify snackbar-based system.
 * Displays multiple notifications that stack vertically.
 *
 * Usage:
 * <notification-snackbar></notification-snackbar>
 *
 * API:
 * store.commit('notify', { text: 'Message', title: 'Title', type: 'success' })
 * store.commit('notify_success', { text: 'Saved!' })
 * store.commit('notify_error', { text: 'Failed to save' })
 * store.commit('notify_warning', { text: 'Warning' })
 * store.commit('notify_info', { text: 'Info' })
 *
 * Global helpers:
 * window.notify({ text: 'Message', type: 'success' })
 * window.notifySuccess('Saved!')
 * window.notifyError('Failed')
 * window.notifyWarning('Warning')
 * window.notifyInfo('Info')
 */

app.component("NotificationSnackbar", {
  template: `
<div class="notification-container">
  <v-snackbar
    v-for="(notification, index) in notifications"
    :key="notification.id"
    :model-value="isShowing(notification.id)"
    :color="notification.color"
    :timeout="notification.timeout"
    location="bottom right"
    multi-line
    :style="'bottom:' + (index * 80) + 'px !important'"
    @update:modelValue="onSnackbarChange(notification.id, $event)"
  >
    <div v-if="notification.title" class="font-weight-bold mb-1">${'{{'} notification.title ${'}}'}</div>
    <div>${'{{'} notification.text ${'}}'}</div>

    <template v-slot:actions>
      <v-btn
        variant="text"
        @click.stop="hide(notification.id)"
      >
        Close
      </v-btn>
    </template>
  </v-snackbar>
</div>
`,
  data: function() {
    return {
      showingStates: {}
    };
  },
  computed: {
    notifications: function() {
      return store.getters.notifications;
    }
  },
  watch: {
    notifications: {
      handler: function(newNotifications) {
        var self = this;
        // Initialize showing state for new notifications
        newNotifications.forEach(function(n) {
          if (self.showingStates[n.id] === undefined) {
            self.showingStates[n.id] = true;
          }
        });
      },
      immediate: true,
      deep: true
    }
  },
  methods: {
    isShowing: function(id) {
      return this.showingStates[id] !== false;
    },
    hide: function(id) {
      this.showingStates[id] = false;
      store.commit('remove_notification', id);
    },
    onSnackbarChange: function(id, value) {
      if (!value) {
        // Snackbar closed (timeout or swipe)
        store.commit('remove_notification', id);
      }
    }
  }
});

// Also register as "notifications" for backward compatibility with templates
app.component("notifications", {
  template: `<notification-snackbar></notification-snackbar>`
});