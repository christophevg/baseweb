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
    "sortBy"
  ],
  template : `
<div>
  <v-card>
    <v-card-title>
      <h2>{{ topic }}
        <v-btn flat icon color="primary" @click="search">
          <v-icon>refresh</v-icon>
        </v-btn>
        <v-btn flat icon color="primary" @click="create" v-if="has_action('create')">
          <v-icon>add_circle</v-icon>
        </v-btn>
      </h2>
      <v-spacer></v-spacer>
      <v-text-field
        v-model="model.query"
        append-icon="search"
        single-line
        hide-details
      ></v-text-field>
    </v-card-title>

    <v-data-table
      :headers="all_headers"
      :items="rows"
      :expand="expand"
      item-key="requestId"
      :pagination.sync="options"
      :total-items="model.totalElements"
      :loading="loading"
      next-icon=""
      prev-icon=""
      class="elevation-1"
    >
      <template slot="items" slot-scope="row">
        <tr @click="select(row.item)" :class="row.item[id] === selected[id] ? 'selected-row' : ''">
          <td v-for="(header, i) in headers" v-if="header != ''" :align="header.align">{{ extract(header.value, row.item) }}</td>
          <td :width="actions_width" v-if="has_actions" align="center">
            <v-btn v-for="action in row_actions" :key="action.icon" flat icon :color="action.color" @click="action.func(row.item[id]);">
              <v-icon>{{ action.icon }}</v-icon>
            </v-btn>
          </td>
        </tr>
      </template>
    </v-data-table>

    <div class="text-xs-center pt-2">
      <v-pagination
        v-model="options.page"
        :length="pages"
        :total-visible="7"
        circle
        @input="search"
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
        <span class="headline">{{ label('title') }}</span>
      </v-card-title>
      <v-card-text>
        <vue-form-generator :schema="schema" :model="created" :options="formOptions"></vue-form-generator>
      </v-card-text>
      <v-card-actions>
        <v-spacer></v-spacer>
        <v-btn color="blue darken-1" flat @click="model.dialog = false">{{ label('cancel') }}</v-btn>
        <v-btn color="blue darken-1" flat @click="submit()">{{ label('create') }}</v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>

</div>
`,
  mounted: function() {
    this.options.sortBy = this.sortBy;
    var self = this;
    document.addEventListener("keypress", function (e) {
      var key = e.which || e.keyCode;
      if (key === 13) { // 13 is enter
        self.search();
      }
    });
  },
  created: function() {
    // adopt queries from URL
    if( window.location.search ) {
      // TODO: improve unmarshalling
      this.model.query = window.location.search.slice(1).replace("&", " ");
    }
    if(! this.sortBy ) {
      this.search();
    }
  },
  computed: {
    label: function() {
      var self = this;
      return function(name) {
        if( ! self.labels ) { return name; }
        return self.labels[name] || name;
      }
    },
    has_actions: function() {
      return this.row_actions.length > 0;
    },
    all_headers: function() {
      if(this.has_actions) {
        return this.headers.concat({ text: "Acties", align: "center",  sortable: false, value: "" })
      }
      return this.headers;
    },
    actions_width: function() {
      return (25 + (this.row_actions.length * 75)) + "px";
    },
    has_action: function() {
      var self = this;
      return function(action) {
        if(! self.has_actions ) { return false; }
        return self.actions.split(" ").includes(action);
      }
    },
    row_actions: function() {
      if( ! this.actions ) { return [] };
      var self = this;
      return this.actions.split(" ").map(function(action) {
        if( action == "create" ) {
          return null;
        }
        if( action == "delete") {
          return {
            "color" : "red",
            "icon"  : "delete",
            "func"  : self.delete
          }
        }
        var parts = action.split("|");
        return {
          "func"  : function(id) { self.$emit(parts[0], id) },
          "color" : parts[1],
          "icon"  : parts[2]
        }
      }).filter(function(item) { return item != null });
    },
    extract : function() {
      return function(path, obj) {
        var v = obj;
        path.split(".").forEach(function(step) { v = v[step]; });
        return v;
      }
    },
    rows: function() {
      return this.model.results.map(function(item) {
        return item;
      });
    },
    hasRows : function() {
      return this.model.results.length > 0;
    },
    pages : function() {
      if (this.options.rowsPerPage == null ||
        this.options.totalItems == null
      ) return 0
      return Math.ceil(this.options.totalItems / this.options.rowsPerPage)
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
      for( var p in parts ) {
        var kv = parts[p].split("=");
        if(kv[0] && kv[1]) {
          params[kv[0]] = kv[1].replace("%20", " ");
        } else {
          if(parts[p].length > 2) {
            params[this.id] = parts[p];
          }
        }
      }
      const { descending, page, rowsPerPage, sortBy } = this.options;
      if (sortBy) {
        params["sort"] = sortBy;
        if( descending ) { params["order"] = "desc"; }
      }
      if( rowsPerPage > 0 ) {
        params["limit"] = rowsPerPage;
        params["start"] = (page-1) * rowsPerPage;
      }
      return params;
    },
    submit: function() {
      this.$emit("create");
      this.model.dialog = false;
    },
    search: function() {
      this.loading = true
      var params = this.get_search_params();
      var self = this;
      $.ajax({
        url: self.resource,
        data: params,
        type: "get",
        success: function(response) {
          self.loading = false;
          self.select({});
          self.model.results       = response.content;
          self.model.totalElements = response.totalElements;
          self.initiated = true;
        },
        error: function(response) {
          self.loading = false;
          app.$notify({
            group: "notifications",
            title: "Could not load " + self.resource,
            text:  response.responseText,
            type:  "warn",
            duration: 10000
          });
        }
      });
    },
    delete: function(id) {
      this.loading = true
      var self = this;
      $.ajax({
        url: self.resource + "?" + self.id + "=" + id,
        type: "delete",
        success: function(response) {
          self.loading = false;
          app.$notify({
            group: "notifications",
            title: id + " has been deleted",
            text:  response,
            type:  "success",
            duration: 10000
          });
          self.search();
        },
        error: function(response) {
          self.loading = false;
          app.$notify({
            group: "notifications",
            title: "Could not delte " + id,
            text:  response.responseText,
            type:  "warn",
            duration: 10000
          });
        }
      });
    }
  },
  watch: {
    options: {
      handler(o, n) {
        if(   o.descending != n.descending   || o.page   != n.page
           || o.rowsPerPage != n.rowsPerPage || o.sortBy != n.sortBy )
        {
          this.search();
        }
      },
      deep: true,
    }
  },
  data: function() {
    return {
      initiated       : false,
      loading         : true,
      expand          : false,
      options: {
        descending    : true,
        page          : 1,
        rowsPerPage   : 5,
        sortBy        : null,
        totalItems    : 0
      },
      model: {
        dialog        : false,
        query         : "",
        results       : [],
        totalElements : 0
      }
    }
  }
});
