var store = new Vuex.Store({
  state: {
    config : {{ app.toDict() | tojson }}
  },
  mutations: {
  },
  actions: {
  },
  getters: {
  }
});
