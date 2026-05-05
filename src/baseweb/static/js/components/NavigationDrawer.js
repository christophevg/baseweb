// NavigationDrawer.js - Navigation components for baseweb

// Individual navigation item component
// nested: if true, icon appears on the right (for pages within sections)
app.component("navigation-drawer-page", {
  props: ["page", "nested"],
  template: `
<v-list-item @click="navigate" :active="isActive">
  <template v-if="!nested" v-slot:prepend>
    <v-icon>{{ page.icon }}</v-icon>
  </template>
  <v-list-item-title>{{ page.text }}</v-list-item-title>
  <template v-slot:append>
    <v-icon v-if="nested && !page.badge">{{ page.icon }}</v-icon>
    <v-badge v-if="page.badge" :color="page.badge.color" :model-value="page.badge.visible" inline>
      <template v-slot:badge>
        <v-icon v-if="page.badge.icon" size="small">{{ page.badge.icon }}</v-icon>
        <span v-if="page.badge.text">{{ page.badge.text }}</span>
      </template>
    </v-badge>
  </template>
</v-list-item>
`,
  computed: {
    isActive: function() {
      return this.$route && this.$route.path === this.page.path;
    }
  },
  methods: {
    navigate: function() {
      if (this.$route && this.$route.path !== this.page.path) {
        this.$router.push(this.page.path);
      }
    }
  }
});

// Navigation drawer component
app.component("navigation-drawer", {
  template: `
<v-navigation-drawer v-model="drawerShowing" location="start">
  <v-list density="compact" nav v-model:opened="openGroups">
    <template v-for="(section, index) in sections" :key="index">
      <v-list-group v-if="section.group && section.pages && section.pages.length > 0" :value="section.text">
        <template v-slot:activator="{ props }">
          <v-list-item v-bind="props">
            <template v-slot:prepend>
              <v-icon>{{ section.icon }}</v-icon>
            </template>
            <v-list-item-title>{{ section.text }}</v-list-item-title>
          </v-list-item>
        </template>
        <navigation-drawer-page v-for="page in section.pages" :key="page.path" :page="page" :nested="true"/>
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
    },
    openGroups: {
      get: function() {
        // Return section names that should be expanded
        // Sections default to collapsed (expanded=false) unless explicitly set to true
        return this.sections
          .filter(function(section) {
            return section.group && section.expanded === true;
          })
          .map(function(section) { return section.text; });
      },
      set: function(value) {
        // User toggled groups - update state
        store.commit('set_open_sections', value);
      }
    }
  }
});

// Register drawer module with Vuex
store.registerModule("drawer", {
  state: {
    showing: true,
    sections: [],
    openSections: []  // Track which sections are open
  },
  mutations: {
    toggle_drawer: function(state) {
      state.showing = !state.showing;
    },
    set_drawer: function(state, value) {
      state.showing = value;
    },
    set_open_sections: function(state, value) {
      state.openSections = value;
    },
    navigation: function(state, navigation) {
      // If navigation has a section, find or create the section group
      if (navigation.section) {
        var sectionName = navigation.section;
        var existingSection = state.sections.find(function(s) {
          return s.group && s.text === sectionName;
        });

        if (existingSection) {
          // Add to existing section
          if (!existingSection.pages) existingSection.pages = [];
          existingSection.pages.push(navigation);
          existingSection.pages.sort(function(a, b) {
            if (!a.index || !b.index) return 0;
            if (a.index < b.index) return -1;
            if (a.index > b.index) return 1;
            return 0;
          });
        } else {
          // Create new section with this page
          // Use a high index to push sections to the end
          state.sections.push({
            text: sectionName,
            icon: navigation.icon,
            group: true,
            index: 1000,  // Default high index for sections
            pages: [navigation]
          });
        }
      } else {
        // No section - add as top-level navigation
        state.sections.push(navigation);
      }

      // Sort sections: top-level pages first (by index), then grouped sections
      state.sections.sort(function(a, b) {
        var aIndex = a.index || (a.group ? 1000 : 999);
        var bIndex = b.index || (b.group ? 1000 : 999);
        if (aIndex < bIndex) return -1;
        if (aIndex > bIndex) return 1;
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