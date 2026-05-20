// Vuex store for baseweb
// This creates the central store that components can register modules with

var store = Vuex.createStore({
  modules: {},
  state: {
    online: navigator.onLine
  },
  mutations: {
    setOnline: function(state, status) {
      state.online = status;
    }
  },
  getters: {
    isOnline: function(state) {
      return state.online;
    }
  }
});

// Track online/offline status
window.addEventListener('online', function() {
  store.commit('setOnline', true);
});
window.addEventListener('offline', function() {
  store.commit('setOnline', false);
});