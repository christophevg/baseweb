var app = new Vue({
  el: "#app",
  delimiters: ['${', '}'],
  router: router,
  components: {
    multiselect: VueMultiselect.Multiselect,
    navigationdrawer: NavigationDrawer
  },
  data: {
    connected:   false,
    initialized: false,
    socketio: false
  },
  methods: {
    // fixVuetifyCSS : function() {
    //   this.$vuetify.theme.info  = '#ffffff';
    //   this.$vuetify.theme.error = '#ffffff';
    // },
    registerClientComponent: function(component) {
      store.commit("clientComponent", component);
    },
    registerGroupComponent: function(component) {
      store.commit("groupComponent", component);
    },
    toggle_drawer: function() {
      store.commit('toggle_drawer');
    }
  }
});

// :-( can't remember why I did this ;-)
// app.fixVuetifyCSS();
