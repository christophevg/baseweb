var app = new Vue({
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
