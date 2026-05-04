/**
 * CollectionView Component - Vue 3 + Vuetify 3 Compatible
 *
 * A data table component with CRUD operations.
 *
 * Props:
 * - topic: Title for the collection
 * - headers: Array of header objects { text, value, align?, sortable? }
 * - resource: API endpoint URL
 * - id: Primary key field name
 * - selected: Currently selected item
 * - actions: Space-separated action string (create, delete, custom|color|icon)
 * - schema: Form schema for create dialog
 * - created: Model object for create form
 * - formOptions: Options for form generator
 * - labels: Label overrides object
 * - sortBy: Default sort field
 * - enrich: Function to transform API response
 *
 * Events:
 * - select: Emitted when a row is selected
 * - create: Emitted when create form is submitted
 * - Custom events from actions string
 */
Vue.component("CollectionView", {
  props: [
    "topic",
    "headers",
    "resource",
    "id",
    "selected",
    "actions",
    "schema",
    "created",
    "formOptions",
    "labels",
    "sortBy",
    "enrich"
  ],
  template: `
<div>
  <v-card>
    <v-card-title>
      <h2>${'{{'} topic ${'}}'}
        <v-btn variant="text" icon color="primary" @click="search">
          <v-icon>refresh</v-icon>
        </v-btn>
        <v-btn variant="text" icon color="primary" @click="create" v-if="has_action('create')">
          <v-icon>add_circle</v-icon>
        </v-btn>
      </h2>
      <v-spacer></v-spacer>
      <v-text-field
        v-model="model.query"
        append-inner-icon="search"
        single-line
        hide-details
        @click:append-inner="search"
        @keyup.enter="search"
      ></v-text-field>
    </v-card-title>

    <v-data-table
      :headers="all_headers"
      :items="rows"
      v-model:options="tableOptions"
      :items-length="model.totalElements"
      :loading="loading"
      item-value="requestId"
      class="elevation-1"
    >
      <template v-slot:item="{ item }">
        <tr @click="select(item)" :class="item[id] === selected[id] ? 'selected-row' : ''">
          <td v-for="(header, i) in headers" v-if="header.value != '' && header.value != undefined" :align="header.align">${'{{'} extract(header.value || header.key, item) ${'}}'}</td>
          <td :style="{ width: actions_width }" v-if="has_actions" class="text-center">
            <v-btn v-for="action in row_actions" :key="action.icon" variant="text" icon :color="action.color" @click.stop="action.func(item[id]);">
              <v-icon>${'{{'} action.icon ${'}}'}</v-icon>
            </v-btn>
          </td>
        </tr>
      </template>
    </v-data-table>

    <div class="text-center pt-2">
      <v-pagination
        v-model="tableOptions.page"
        :length="pages"
        :total-visible="7"
        rounded="circle"
        @update:modelValue="search"
      ></v-pagination>
    </div>

    <v-card v-if="selected[id]">
      <v-card-text>
        <slot></slot>
      </v-card-text>
    </v-card>

  </v-card>

  <v-dialog v-model="model.dialog" persistent max-width="600px">
    <v-card>
      <v-card-title>
        <span class="text-h5">${'{{'} label('title') ${'}}'}</span>
      </v-card-title>
      <v-card-text>
        <vue-form-generator :schema="schema" :model="created" :options="formOptions"></vue-form-generator>
      </v-card-text>
      <v-card-actions>
        <v-spacer></v-spacer>
        <v-btn color="blue-darken-1" variant="text" @click="model.dialog = false">${'{{'} label('cancel') ${'}}'}</v-btn>
        <v-btn color="blue-darken-1" variant="text" @click="submit()">${'{{'} label('create') ${'}}'}</v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>

  <v-dialog v-model="model.confirm_delete_dialog" persistent max-width="600px">
    <v-card>
      <v-card-title class="text-h5">${'{{'} label('delete it') ${'}}'}?</v-card-title>

      <v-card-text>
        ${'{{'} label('delete item') ${'}}'} ${'{{'} model.confirm_delete ${'}}'}?
      </v-card-text>

      <v-card-actions>
        <v-spacer></v-spacer>

        <v-btn color="secondary" variant="text" @click="model.confirm_delete_dialog = false">
          ${'{{'} label('cancel delete') ${'}}'}
        </v-btn>

        <v-btn color="error" variant="flat" @click="do_delete">
          ${'{{'} label('confirm delete') ${'}}'}
        </v-btn>

      </v-card-actions>

    </v-card>
  </v-dialog>

</div>
`,
  mounted: function() {
    // Set initial sort if provided
    if (this.sortBy) {
      this.tableOptions.sortBy = [{ key: this.sortBy, order: 'desc' }];
    }
  },
  created: function() {
    // adopt queries from URL
    if (window.location.search) {
      // TODO: improve unmarshalling
      this.model.query = window.location.search.slice(1).replace("&", " ");
    }
    if (!this.sortBy) {
      this.search();
    }
  },
  computed: {
    label: function() {
      var self = this;
      return function(name) {
        if (!self.labels) { return name; }
        return self.labels[name] || name;
      };
    },
    has_actions: function() {
      return this.row_actions.length > 0;
    },
    all_headers: function() {
      var self = this;
      // Convert Vuetify 1.5/2.x headers to Vuetify 3 format
      var convertedHeaders = self.headers.map(function(header) {
        return {
          title: header.text || header.title,
          key: header.value || header.key,
          align: header.align,
          sortable: header.sortable !== undefined ? header.sortable : true
        };
      });

      if (self.has_actions) {
        return convertedHeaders.concat({ title: "Actions", align: "center", sortable: false, key: "__actions" });
      }
      return convertedHeaders;
    },
    actions_width: function() {
      return (25 + (this.row_actions.length * 75)) + "px";
    },
    has_action: function() {
      var self = this;
      return function(action) {
        if (!self.has_actions) { return false; }
        return self.actions.split(" ").includes(action);
      };
    },
    row_actions: function() {
      if (!this.actions) { return []; }
      var self = this;
      return this.actions.split(" ").map(function(action) {
        if (action == "create") {
          return null;
        }
        if (action == "delete") {
          return {
            "color": "red",
            "icon": "delete",
            "func": self.confirm_delete
          };
        }
        var parts = action.split("|");
        return {
          "func": function(id) { self.$emit(parts[0], id); },
          "color": parts[1],
          "icon": parts[2]
        };
      }).filter(function(item) { return item != null; });
    },
    extract: function() {
      return function(path, obj) {
        if (!path || !obj) return '';
        var v = obj;
        path.split(".").forEach(function(step) {
          if (v === null || v === undefined) return '';
          v = v[step];
        });
        return v !== undefined && v !== null ? v : '';
      };
    },
    rows: function() {
      return this.model.results.map(function(item) {
        return item;
      });
    },
    hasRows: function() {
      return this.model.results.length > 0;
    },
    pages: function() {
      if (this.tableOptions.itemsPerPage == null ||
        this.model.totalElements == null
      ) return 0;
      return Math.ceil(this.model.totalElements / this.tableOptions.itemsPerPage);
    }
  },
  methods: {
    select: function(selection) {
      this.$emit("select", selection);
    },
    create: function() {
      this.model.dialog = true;
    },
    get_search_params: function() {
      // TODO: improve marshalling ;-)
      var parts = this.model.query.split(" ");
      var params = {};
      for (var p in parts) {
        var kv = parts[p].split("=");
        if (kv[0] && kv[1]) {
          params[kv[0]] = kv[1].replace("%20", " ");
        } else {
          if (parts[p].length > 2) {
            params[this.id] = parts[p];
          }
        }
      }

      // Handle sorting from Vuetify 3 options
      var sortBy = this.tableOptions.sortBy;
      if (sortBy && sortBy.length > 0) {
        params["sort"] = sortBy[0].key;
        if (sortBy[0].order === 'desc') {
          params["order"] = "desc";
        }
      }

      var itemsPerPage = this.tableOptions.itemsPerPage;
      var page = this.tableOptions.page;
      if (itemsPerPage > 0) {
        params["limit"] = itemsPerPage;
        params["start"] = (page - 1) * itemsPerPage;
      }
      return params;
    },
    submit: function() {
      this.$emit("create");
      this.model.dialog = false;
    },
    search: async function() {
      var self = this;
      self.loading = true;

      var params = self.get_search_params();
      var queryString = Object.keys(params).map(function(key) {
        return encodeURIComponent(key) + '=' + encodeURIComponent(params[key]);
      }).join('&');

      try {
        var response = await fetch(self.resource + (queryString ? '?' + queryString : ''), {
          method: 'GET',
          headers: {
            'Accept': 'application/json'
          }
        });

        if (!response.ok) {
          throw new Error('HTTP error! status: ' + response.status);
        }

        var data = await response.json();
        self.loading = false;
        self.select({});
        var content = self.enrich ? self.enrich(data.content) : data.content;
        self.model.results = content;
        self.model.totalElements = data.totalElements;
        self.initiated = true;
      } catch (error) {
        self.loading = false;
        store.commit('notify_error', {
          title: 'Could not load ' + self.resource,
          text: error.message,
          timeout: 10000
        });
        console.error('Search error:', error);
      }
    },
    confirm_delete: function(id) {
      this.model.confirm_delete = id;
      this.model.confirm_delete_dialog = true;
    },
    do_delete: async function() {
      var self = this;
      var id = self.model.confirm_delete;

      if (id < 0) {
        console.warn("invalid id");
        self.model.confirm_delete_dialog = false;
        return;
      }

      self.loading = true;

      try {
        var response = await fetch(self.resource + '?' + self.id + '=' + id, {
          method: 'DELETE',
          headers: {
            'Accept': 'application/json'
          }
        });

        if (!response.ok) {
          throw new Error('HTTP error! status: ' + response.status);
        }

        var text = await response.text();
        self.loading = false;
        store.commit('notify_success', {
          title: id + ' has been deleted',
          text: text,
          timeout: 10000
        });
        self.search();
      } catch (error) {
        self.loading = false;
        store.commit('notify_error', {
          title: 'Could not delete ' + id,
          text: error.message,
          timeout: 10000
        });
        console.error('Delete error:', error);
      }

      self.model.confirm_delete = -1;
      self.model.confirm_delete_dialog = false;
    }
  },
  watch: {
    tableOptions: {
      handler: function(newVal, oldVal) {
        // Check if relevant options changed
        var newSort = newVal.sortBy && newVal.sortBy[0];
        var oldSort = oldVal && oldVal.sortBy && oldVal.sortBy[0];

        var sortChanged = !oldVal ||
          (newSort && oldSort && (newSort.key !== oldSort.key || newSort.order !== oldSort.order)) ||
          (newSort && !oldSort) || (!newSort && oldSort);

        var pageChanged = !oldVal || newVal.page !== oldVal.page;
        var itemsPerPageChanged = !oldVal || newVal.itemsPerPage !== oldVal.itemsPerPage;

        if (sortChanged || pageChanged || itemsPerPageChanged) {
          this.search();
        }
      },
      deep: true
    }
  },
  data: function() {
    return {
      initiated: false,
      loading: true,
      // Vuetify 3 table options structure
      tableOptions: {
        page: 1,
        itemsPerPage: 5,
        sortBy: [],
        groupBy: [],
        search: ''
      },
      model: {
        dialog: false,
        confirm_delete: -1,
        confirm_delete_dialog: false,
        query: "",
        results: [],
        totalElements: 0
      }
    };
  }
});