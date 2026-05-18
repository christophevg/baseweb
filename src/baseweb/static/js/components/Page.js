/**
 * Page - Unified page component for baseweb
 *
 * This component consolidates functionality from PageWithBanner and PageWithStatus
 * into a single configurable component with props and slots.
 *
 * Supports:
 * - Basic content wrapper (backward compatible)
 * - Banner/alert integration via banner prop
 * - Status notification snackbar (via status prop)
 *
 * @example
 * // Basic usage (backward compatible)
 * <Page><v-container>...</v-container></Page>
 *
 * @example
 * // With banner support
 * <Page banner>
 *   <v-container>...</v-container>
 * </Page>
 *
 * @example
 * // With status notifications
 * // Use store.commit('page/success', 'message') or store.commit('page/error', 'message')
 * <Page status>
 *   <v-container>...</v-container>
 * </Page>
 */
app.component("Page", {
  name: "Page",
  props: {
    // Banner configuration
    banner: {
      type: Boolean,
      default: false
    },
    // Status configuration
    status: {
      type: Boolean,
      default: false
    },
    statusTimeout: {
      type: Number,
      default: 5000
    }
  },

  template: `
<div class="page-container">
  <slot name="header"></slot>

  <v-alert
    v-if="banner && bannerState.alert"
    v-model="bannerState.alert"
    :closable="bannerState.dismissible"
    :type="bannerState.type"
    class="mb-3"
  >
    {{ bannerState.message }}
  </v-alert>

  <div class="page-body">
    <slot></slot>
  </div>

  <slot name="footer"></slot>

  <v-snackbar
    v-if="status && statusShowing"
    v-model="statusShowing"
    :color="statusLevel"
    :timeout="statusTimeout"
    :key="statusKey"
    location="top"
  >
    {{ statusMessage }}
    <template v-slot:actions>
      <v-btn variant="plain" @click="statusShowing = false">
        <v-icon>mdi-close</v-icon>
      </v-btn>
    </template>
  </v-snackbar>
</div>
`,

  computed: {
    bannerState: function() {
      if (this.banner && store.state.page.banner) {
        return store.state.page.banner;
      }
      return {
        alert: false,
        dismissible: true,
        type: 'info',
        message: ''
      };
    },

    statusShowing: {
      set: function(value) {
        if (!value) {
          store.commit('page/clearStatus');
        }
      },
      get: function() {
        return store.state.page.status.msg !== '';
      }
    },

    statusMessage: function() {
      return store.state.page.status.msg;
    },

    statusLevel: function() {
      return store.state.page.status.level;
    },

    statusKey: function () {
      return store.state.page.status.key;
    }
  }
});

store.registerModule('page', {
  namespaced: true,
  state: {
    banner: {
      alert: false,
      dismissible: true,
      type: 'success',
      message: 'OK'
    },
    status: {
      msg: '',
      level: '',
      key: 0
    }
  },
  mutations: {
    banner: function (state, banner) {
      Object.keys(state.banner).forEach(function (prop) {
        if (prop in banner) {
          state.banner[prop] = banner[prop];
        }
      });
    },
    info: function (state, msg) {
      state.status.msg = msg;
      state.status.level = 'info';
      state.status.key += 1;
    },
    success: function(state, msg) {
      state.status.msg = msg;
      state.status.level = 'success';
      state.status.key += 1;
    },
    warning: function(state, msg) {
      state.status.msg = msg;
      state.status.level = 'warning';
      state.status.key += 1;
    },
    error: function (state, msg) {
      state.status.msg = msg;
      state.status.level = 'error';
      state.status.key += 1;
    },
    clearStatus: function(state) {
      state.status.msg = '';
      state.status.level = '';
      state.status.key += 1;
    }
  }
});