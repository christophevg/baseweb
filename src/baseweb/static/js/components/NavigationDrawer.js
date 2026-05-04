// NavigationDrawer.js - Navigation components for baseweb

// Individual navigation item component
app.component("navigation-drawer-page", {
  props: ["page"],
  template: `
<v-list-item :to="page.path">
  <template v-slot:prepend>
    <v-icon>{{ page.icon }}</v-icon>
  </template>
  <v-list-item-title>{{ page.text }}</v-list-item-title>
  <template v-if="page.badge" v-slot:append>
    <v-badge :color="page.badge.color" :model-value="page.badge.visible" inline>
      <template v-slot:badge>
        <v-icon v-if="page.badge.icon" size="small">{{ page.badge.icon }}</v-icon>
        <span v-if="page.badge.text">{{ page.badge.text }}</span>
      </template>
    </v-badge>
  </template>
</v-list-item>
`
});

// Navigation drawer component
app.component("navigation-drawer", {
  template: `
<v-navigation-drawer v-model="drawerShowing" location="start">
  <v-list density="compact" nav>
    <template v-for="section in sections" :key="section.path || section.name">
      <v-list-subheader v-if="section.group">{{ section.text }}</v-list-subheader>

      <v-list-group v-if="section.group && section.pages && section.pages.length > 0" value="true">
        <template v-slot:activator="{ props }">
          <v-list-item v-bind="props">
            <template v-slot:prepend>
              <v-icon>{{ section.icon }}</v-icon>
            </template>
            <v-list-item-title>{{ section.text }}</v-list-item-title>
          </v-list-item>
        </template>
        <navigation-drawer-page v-for="subsection in section.pages" :key="subsection.path" :page="subsection"/>
      </v-list-group>

      <navigation-drawer-page v-if="!section.group" :key="section.path" :page="section"/>
    </template>
  </v-list>
</v-navigation-drawer>
`,
  computed: {
    drawerShowing: {
      get: function() {
        return store.state.drawer.showing;
      },
      set: function(value) {
        store.commit('set_drawer', value);
      }
    },
    sections: function() {
      return store.state.drawer.sections;
    }
  }
});

// Register drawer module with Vuex
store.registerModule("drawer", {
  state: {
    showing: true,
    sections: []
  },
  mutations: {
    toggle_drawer: function(state) {
      state.showing = !state.showing;
    },
    set_drawer: function(state, value) {
      state.showing = value;
    },
    navigation: function(state, navigation) {
      state.sections.push(navigation);
      state.sections.sort(function(a, b) {
        if (!a.index || !b.index) return 0;
        if (a.index < b.index) return -1;
        if (a.index > b.index) return 1;
        return 0;
      });
    },
    section: function(state, section) {
      if (!section.pages) section.pages = [];
      section.group = true;
      state.sections.push(section);
      state.sections.sort(function(a, b) {
        if (!a.index || !b.index) return 0;
        if (a.index < b.index) return -1;
        if (a.index > b.index) return 1;
        return 0;
      });
    }
  }
});

// Global Navigation helper
window.Navigation = {
  add: function(component) {
    store.commit("navigation", component.navigation);
    router.addRoute({ path: component.navigation.path, component: component });
  },
  add_section: function(section) {
    store.commit("section", section);
  }
};