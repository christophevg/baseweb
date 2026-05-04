// Create a reactive ref for connection state (can be updated from outside)
var connectedRef = Vue.ref(false);

// Create Vue app early so components can register with app.component()
var app = Vue.createApp({
  delimiters: ['{{', '}}'],
  data() {
    return {
      initialized: false
    };
  },
  computed: {
    connected: function() {
      return connectedRef.value;
    }
  },
  methods: {
    toggle_drawer: function() {
      store.commit('toggle_drawer');
    }
  }
});

// Expose the ref globally for socketio.js to update
window._socketConnected = connectedRef;