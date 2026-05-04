var store = Vuex.createStore({
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