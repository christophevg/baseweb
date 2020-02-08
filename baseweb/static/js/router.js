var routes = [];
var router = new VueRouter({
  routes: routes,
  mode  : 'history'
});

function order(a, b) {
  if( !a.index || !b.index ) { return 0;  }
  if(  a.index  <  b.index ) { return -1; }
  if(  a.index  >  b.index ) { return 1;  }
  return 0;
}

var app = new Vue({
  el: "#app",
  delimiters: ['${', '}'],
  router: router,
  components: {
    multiselect: VueMultiselect.Multiselect
  },
  data: {
    connected:   false,
    initialized: false,
    drawer: null,
    sections: []
  },
  computed: {
    orderedSections : function() {
      this.sections.sort(order);
      $.each(this.sections, function(idx, section) {
        if( "subsections" in section ) {
          section.subsections.sort(order);
        }
      });
      return this.sections;
    }
  },
  methods: {
    fixVuetifyCSS : function() {
      this.$vuetify.theme.info  = '#ffffff';
      this.$vuetify.theme.error = '#ffffff';
    },
    registerClientComponent: function(component) {
      store.commit("clientComponent", component);
    },
    registerGroupComponent: function(component) {
      store.commit("groupComponent", component);
    }
  }
}).$mount('#app');

app.fixVuetifyCSS();
