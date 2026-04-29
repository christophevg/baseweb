Vue.component("NavigationDrawerPage", {
  props: [
    "page"
  ],
  template: `
<v-list-tile :to="page.path">
  <v-list-tile-content>

    <v-badge v-if="page.badge" :color="page.badge.color" :value="page.badge.visible">
      <template v-slot:badge>
        <v-icon :v-if="page.badge.icon" dark small>{{ page.badge.icon }}</v-icon>
        <span   :v-if="page.badge.text">{{ page.badge.text }}</span>
      </template>
      <v-list-tile-title>{{ page.text }}</v-list-tile-title>
    </v-badge>

    <v-list-tile-title v-else>{{ page.text }}</v-list-tile-title>

  </v-list-tile-content>
  <v-list-tile-action>
    <v-icon>{{ page.icon }}</v-icon>
  </v-list-tile-action>
</v-list-tile>
`
})

var NavigationDrawer = {
  template : `
<v-navigation-drawer fixed clipped app :value="showing">
  <v-list>
    <template v-for="section in sections">

      <v-list-group v-if="section.group" :prepend-icon="section.icon" no-action value="true">
        <v-list-tile slot="activator">
          <v-list-tile-content>
            <v-list-tile-title>{{ section.text }}</v-list-tile-title>
          </v-list-tile-content>
        </v-list-tile>

        <NavigationDrawerPage v-for="(subsection, i) in section.pages" :key="subsection.path"
                              :page="subsection"/>
      </v-list-group>

      <NavigationDrawerPage v-if="! section.group" :key="section.path"
                            :page="section"/>
    </template>
  </v-list>
</v-navigation-drawer>
`,
  computed: {
    showing: function() {
      return store.state.drawer.showing;
    },
    sections: function() {
      return store.state.drawer.sections;
    }
  }
};

Vue.component("NavigationDrawer", NavigationDrawer);

store.registerModule("drawer", {
  state: {
    showing  : true,
    sections : []
  },
  mutations: {
    toggle_drawer: function(state) {
      state.showing = ! state.showing;
    },
    navigation: function(state, navigation) {
      if(! navigation.section ) {
        // top level navigation: section or page
        state.sections.push(navigation);
        state.sections.sort(order);        
      } else {
        // page in an existing section
        var section = state.sections.find(function(section){
          return section.name == navigation.section;
        });
        section.pages.push(navigation);
        section.pages.sort(order);
      }
    },
    section: function(state, section) {
      if(!("pages" in section)) {
        section["pages"] = [];
      }
      section["group"] = true;
      state.sections.push(section);
      state.sections.sort(order);      
    },

    // deprecated...

    navigation_group : function(state, group) {
      state.sections.push(group);
      state.sections.sort(order);
    },
    navigation_page : function(state, page) {
      if(page.section) {
        // section page
        state.sections[page.section].push(page);
        state.sections[page.section].sort(order);        
      } else {
        // top-level page
        state.sections.push(page);
        state.sections.sort(order);
      }
    }
  }
});

function order(a, b) {
  if( !a.index || !b.index ) { return 0;  }
  if(  a.index  <  b.index ) { return -1; }
  if(  a.index  >  b.index ) { return 1;  }
  return 0;
}

// global functions, wrapping state mutations

(function (globals) {
  var sections = {};
  
  function add_group(section, icon, text, index, group, path) {
    console.warn("Navigation.add_group(...) is deprecated, use Navigation.add_section({})");
    sections[section] = {
      name  : section,
      index : index || Object.keys(sections).length+1,
      group : group !== false,
      icon  : icon,
      text  : text,
      pages :     [],
      path  : path
    }
    store.commit("navigation_group", sections[section]);
  }
  
  function add_page(section, icon, text, path, component, index) {
    console.warn("Navigation.add_page(...) is deprecated, use Navigation.add({}) in stead");
    if(! section) {
      // top-level page
      add_group(text, icon, text, index, false, path)
    } else {
      // page in section
      sections[section].pages.push({
        icon  : icon,
        text  : text,
        path  : path,
        index : index
      });
    }
    router.addRoutes([ { path: path, component: component } ]);
  }
  
  // new interface
  
  function add_section(section) {
    store.commit("section", section);
  }
  
  function add_component(component) {
    store.commit("navigation", component.navigation);
    router.addRoutes([
      { path: component.navigation.path, component: component }
    ]);
  }

  globals.Navigation = {
    // deprecated ... to be removed in due time ;-)
    "add_group"   : add_group,
    "add_page"    : add_page,

    "add_section" : add_section,
    "add"         : add_component
  };

})(window);
