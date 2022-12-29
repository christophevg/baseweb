var app = new Vue({
  el:         "#app",
  delimiters: ['${', '}'],
  router:     router,
  components: {
    multiselect:      VueMultiselect.Multiselect,
    navigationdrawer: NavigationDrawer
  },
  data: {
    connected:   false,
    initialized: false,
    socketio:    false
  },
  methods: {
    // deprecated ?
    // registerClientComponent: function(component) {
    //   store.commit("clientComponent", component);
    // },
    // registerGroupComponent: function(component) {
    //   store.commit("groupComponent", component);
    // },

    // used from main to access drawer store in NavigationDrawer
    toggle_drawer: function() {
      store.commit('toggle_drawer');
    }
  }
});

function before_app_mount(f) {
  if( app.$options.beforeMount ) {
    app.$options.beforeMount.push(f);
  } else {
    app.$options.beforeMount = [ f ];
  }
}
