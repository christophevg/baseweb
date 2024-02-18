// basic page, with status-reporting snackbar support

Vue.component("PageWithStatus", {
  template : `
<Page>
  <slot/>
  <v-snackbar v-model="showing" :color="level" :timeout="timeout" top>
    {{ msg }}
    <v-btn dark flat @click="showing=false"><v-icon>close</v-icon></v-btn>
  </v-snackbar>
</Page>
`,
  computed: {
    showing: {
      set: function(value) {
        store.commit("clear");
      },
      get: function() {
        return store.state.status.msg !== "";
      }
    },
    msg: function() {
      return store.state.status.msg;
    },
    level: function() {
      return store.state.status.level;
    }
  },
  data: function() {
    return {
      timeout: 5000 // ms
    }
  }
});

store.registerModule("status", {
  state: {
    msg : "",
    level: ""
  },
  mutations: {
    info: function(state, msg) {
      state.msg = msg;
      state.level = "info";
    },
    success: function(state, msg) {
      state.msg = msg;
      state.level = "success";
    },
    warning: function(state, msg) {
      state.msg = msg;
      state.level = "warning";
    },
    error: function(state, msg) {
      state.msg = msg;
      state.level = "error";
    },
    clear: function(state) {
      state.msg = "";
      state.level = "";
    }
  }
});
