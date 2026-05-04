/**
 * NotificationSnackbar - Vuetify 3 notification component
 *
 * Replaces vue-notification with a Vuetify snackbar-based system.
 * Listens to the store notification state and displays snackbar accordingly.
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
<v-snackbar
  v-model="showing"
  :color="color"
  :timeout="timeout"
  :location="location"
  multi-line
>
  <div v-if="title" class="font-weight-bold mb-1">${'{{'} title ${'}}'}</div>
  <div>${'{{'} text ${'}}'}</div>

  <template v-slot:actions>
    <v-btn
      variant="text"
      @click="hide"
    >
      Close
    </v-btn>
  </template>
</v-snackbar>
`,
  data: function() {
    return {
      internalShowing: false
    };
  },
  computed: {
    notification: function() {
      return store.state.notification || {
        showing: false,
        text: '',
        title: '',
        color: 'info',
        timeout: 4000,
        location: 'bottom right'
      };
    },
    showing: {
      get: function() {
        return this.notification.showing;
      },
      set: function(value) {
        if (!value) {
          store.commit('hide_notification');
        }
      }
    },
    text: function() {
      return this.notification.text;
    },
    title: function() {
      return this.notification.title;
    },
    color: function() {
      return this.notification.color;
    },
    timeout: function() {
      return this.notification.timeout;
    },
    location: function() {
      return this.notification.location;
    }
  },
  methods: {
    hide: function() {
      store.commit('hide_notification');
    }
  }
});

// Also register as "notifications" for backward compatibility with templates
app.component("notifications", {
  template: `<notification-snackbar></notification-snackbar>`
});