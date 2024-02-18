// basic page with a persistent banner

Vue.component("PageWithBanner", {
  template : `
<Page>
  <v-alert v-model="banner.alert" :dismissible="banner.dismissible" :type="banner.type">{{ banner.message }}</v-alert>
  <div style="padding-top:15px" v-if="banner.alert">&nbsp;</div>
  <slot></slot>
</Page>
`,
  computed: {
    banner: function() {
      return store.state.banner;
    }
  }
});

store.registerModule("banner", {
  state: {
    alert:       false,
    dismissible: true,
    type:        "success",
    message:     "OK"
  },
  mutations: {
    banner: function(state, banner) {
      Object.keys(state).forEach(function(prop){
        if( prop in banner ) { state[prop] = banner[prop] }
      })
    }
  }
});
