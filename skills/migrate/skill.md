---
name: baseweb-migrate
description: Migrate Flask/Vue 2 baseweb apps to async Quart and Vue 3
triggers:
  - when asked to migrate a Flask/baseweb app
  - when modernizing legacy baseweb code
  - when converting sync Flask patterns to async Quart
  - when migrating Vue 2 to Vue 3
---

# Baseweb Migrate Skill

Migrate existing baseweb applications from Flask/Vue 2 to Quart/Vue 3 with Vuetify 3.

## Overview

This skill guides the complete migration from legacy baseweb to modern baseweb:

| Component | From | To |
|-----------|------|-----|
| **Backend** | Flask (sync) | Quart (async) |
| **Resources** | flask_restful.Resource | baseweb.Resource |
| **WebSocket** | Flask-SocketIO | python-socketio (ASGI) |
| **Server** | eventlet | uvicorn |
| **Frontend** | Vue 2 | Vue 3 |
| **UI Framework** | Vuetify 2 | Vuetify 3 |
| **Icons** | Material Icons | Material Design Icons (MDI) |
| **State** | Vuex 3 | Vuex 4 |

## When to Use

- Migrating existing baseweb `< 0.4.0` apps to `>= 1.0.0`
- Converting sync Flask patterns to async Quart patterns
- Migrating Vue 2 frontend to Vue 3
- Modernizing legacy baseweb codebases

---

# Part 1: Backend Migration (Flask → Quart)

## Step 1: Analyze Current Project

```bash
# Find all Python files
find . -name "*.py" -type f

# Check for Flask imports
grep -r "from flask import" --include="*.py"
grep -r "import flask" --include="*.py"

# Check for Flask-RESTful usage
grep -r "from flask_restful import" --include="*.py"

# Check for Flask-SocketIO usage
grep -r "from flask_socketio import" --include="*.py"
```

## Step 2: Update Dependencies

Update `pyproject.toml`:

```diff
- Flask>=2.0.0
- Flask-RESTful>=0.3.0
- Flask-SocketIO>=5.0.0
- eventlet>=0.30.0

+ quart>=0.18.0
+ python-socketio>=5.0.0
+ gunicorn>=21.0.0
+ uvicorn[standard]>=0.24.0
```

## Step 3: Update Imports

| Before | After |
|--------|-------|
| `from flask import Flask` | `from quart import Quart` |
| `from flask import request, abort, Response` | `from quart import request, abort, Response` |
| `from flask_restful import Resource` | `from baseweb import Resource` |

## Step 4: Convert to Async

```python
# Before (sync)
class Hello(Resource):
    def get(self):
        return {"message": "Hello"}

    def post(self):
        data = request.get_json()
        return {"received": data}

# After (async)
class Hello(Resource):
    async def get(self):
        return {"message": "Hello"}

    async def post(self):
        data = await request.get_json()
        return {"received": data}
```

**Key changes:**
- Add `async` keyword to method definitions
- Add `await` to `request.get_json()` calls
- Add `await` to `render_template()` calls

## Step 5: Update Resource Registration

```python
# Before
from flask_restful import Api
api = Api(server)
api.add_resource(HelloResource, '/api/hello')

# After
server.add_resource(HelloResource, '/api/hello')
```

## Step 6: Migrate Socket.IO Handlers

```python
# Before (Flask-SocketIO)
@server.socketio.on("connect")
def handle_connect():
    emit("connected", {"status": "ok"})

@server.socketio.on("message")
def handle_message(data):
    return {"echo": data}

# After (python-socketio with ASGI)
@server.socketio.on("connect")
async def handle_connect(sid, environ):
    await server.socketio.emit("connected", {"status": "ok"})

@server.socketio.on("message")
async def handle_message(sid, data):
    return {"echo": data}
```

**Key changes:**
- Add `async` keyword to handler definitions
- Add `sid` as first parameter (session ID)
- Add `environ` as second parameter for connect handlers
- Add `await` to `emit()` calls

## Step 7: Create ASGI Entry Point

```python
# module/__init__.py
from baseweb import Baseweb

server = Baseweb("myapp")

# ... configuration ...

# ASGI entry point (for uvicorn/gunicorn)
asgi_app = server._asgi_app
```

## Step 8: Update Run Command

```bash
# Before (WSGI with eventlet)
gunicorn -k eventlet -w 1 module:server

# After (ASGI with uvicorn)
uvicorn app:asgi_app --host 0.0.0.0 --port 8000
# or with gunicorn
gunicorn -w 1 -k uvicorn.workers.UvicornWorker "module:asgi_app"
```

---

# Part 2: Frontend Migration (Vue 2 → Vue 3)

## Critical: App Loading Order

Vue 3 requires `app` to be available before components can register. The main.html template must load `app.js` **immediately after `vue.js`**:

```html
<!-- Vue 3 -->
<script src="/static/vendor/js/vue.js"></script>
<script src="/static/js/app.js"></script>  <!-- Load early! -->

<!-- Vuetify 3 -->
<script src="/static/vendor/js/vuetify.js"></script>
```

## Vue 2 → Vue 3 Patterns

### Component Registration

```javascript
// Before (Vue 2)
Vue.component("MyComponent", {
  template: `<div>Hello</div>`
});

// After (Vue 3)
app.component("MyComponent", {
  template: `<div>Hello</div>`
});
```

### Filters Removed

Vue 3 removed filters. Use global properties instead:

```javascript
// Before (Vue 2 template)
{{ message.when | formatDate }}

// After (Vue 3 template)
{{ $filters.formatDate(message.when) }}
```

Register filters in main.html:

```html
<script>
  app.config.globalProperties.$filters = {
    syntaxHighlight: syntaxHighlight,
    formatDate: formatDate,
    formatEpoch: formatEpoch
  };
</script>
```

Update common.js to export functions instead of registering filters:

```javascript
// Before (Vue 2)
Vue.filter('formatDate', function(value) {
  return moment(value).format('DD/MM/YYYY HH:mm:ss');
});

// After (Vue 3 - just export the function)
function formatDate(value) {
  if (value) {
    return moment(value).format('DD/MM/YYYY HH:mm:ss');
  }
  return '';
}
```

### v-if and v-for Priority

**Critical:** In Vue 3, `v-if` has **higher priority** than `v-for` when on the same element.

```html
<!-- Before (Vue 2 - v-for has priority) -->
<div v-for="item in items" v-if="item.active">
  {{ item.name }}
</div>

<!-- After (Vue 3 - use computed property) -->
<div v-for="item in activeItems" :key="item.id">
  {{ item.name }}
</div>

<script>
computed: {
  activeItems: function() {
    return this.items.filter(function(item) {
      return item.active;
    });
  }
}
</script>

<!-- Alternative: use template wrapper -->
<template v-for="item in items" :key="item.id">
  <div v-if="item.active">
    {{ item.name }}
  </div>
</template>
```

**For table headers:**
```html
<!-- Before (Vue 2) -->
<td v-for="header in headers" v-if="header.value">
  {{ header.text }}
</td>

<!-- After (Vue 3) -->
<td v-for="header in filteredHeaders" :key="header.value">
  {{ header.text }}
</td>

<script>
computed: {
  filteredHeaders: function() {
    return this.headers.filter(function(h) {
      return h.value !== '' && h.value !== undefined;
    });
  }
}
</script>
```

### Notification System

```javascript
// Before (Vue 2)
app.$notify({
  group: "notifications",
  title: "Success",
  text: "Saved!",
  type: "success"
});

// After (Vue 3)
notify({
  title: "Success",
  text: "Saved!",
  type: "success"
});

// Or via store
store.commit('notify', { title: "Success", text: "Saved!", type: "success" });
```

### Socket.io Connection State

Use a Vue ref for connection state that can be updated from outside:

```javascript
// app.js
var connectedRef = Vue.ref(false);

var app = Vue.createApp({
  computed: {
    connected: function() {
      return connectedRef.value;
    }
  }
});

window._socketConnected = connectedRef;
```

```javascript
// socketio.js
socket.on("connect", function() {
  window._socketConnected.value = true;
});
```

---

# Part 3: Vuetify 2 → Vuetify 3 Migration

## Icon Migration (Critical)

**This is the most common breaking change.**

### Install MDI Font

```bash
npm pack @mdi/font
tar -xzf mdi-font-*.tgz
cp package/css/materialdesignicons.min.css /path/to/static/vendor/css/mdi.min.css
cp package/fonts/materialdesignicons-webfont.* /path/to/static/vendor/fonts/
```

### Icon Name Mapping

| Material Icons | MDI Equivalent |
|---------------|---------------|
| `menu` | `mdi-menu` |
| `home` | `mdi-home` |
| `close` | `mdi-close` |
| `edit` | `mdi-pencil` |
| `delete` | `mdi-delete` |
| `search` | `mdi-magnify` |
| `add_circle` | `mdi-plus-circle` |
| `description` | `mdi-text-box` |
| `extension` | `mdi-puzzle` |
| `cloud_done` | `mdi-cloud-check` |
| `cloud_off` | `mdi-cloud-off` |
| `layers` | `mdi-layers` |
| `web` | `mdi-web` |

### Icon Usage in Components

```html
<!-- Before -->
<v-icon>menu</v-icon>

<!-- After -->
<v-icon>mdi-menu</v-icon>
```

For navigation items using slots:

```html
<!-- Before -->
<v-list-item :prepend-icon="page.icon">

<!-- After (use slot for Material Icons) -->
<v-list-item>
  <template v-slot:prepend>
    <v-icon>{{ page.icon }}</v-icon>
  </template>
</v-list-item>
```

## Grid System

```html
<!-- Before (Vuetify 2) -->
<v-layout>
  <v-flex xs12 sm6 offset-sm3>
    <v-card>...</v-card>
  </v-flex>
</v-layout>

<!-- After (Vuetify 3) -->
<v-container>
  <v-row justify="center">
    <v-col cols="12" sm="6">
      <v-card>...</v-card>
    </v-col>
  </v-row>
</v-container>
```

## App Bar

```html
<!-- Before -->
<v-toolbar color="primary" dark>
  <v-toolbar-title>Title</v-toolbar-title>
</v-toolbar>

<!-- After -->
<v-app-bar color="primary" theme="dark">
  <v-app-bar-title>Title</v-app-bar-title>
</v-app-bar>
```

## Main Content

```html
<!-- Before -->
<v-content>
  <router-view></router-view>
</v-content>

<!-- After -->
<v-main>
  <router-view></router-view>
</v-main>
```

## Tabs

**Critical:** In Vuetify 3, `v-tabs` and `v-tabs-window` must be **siblings**, not nested.

```html
<!-- Before (Vuetify 2 - nested structure) -->
<v-tabs v-model="tab">
  <v-tab>Tab 1</v-tab>
  <v-tab>Tab 2</v-tab>
  <v-tabs-window>
    <v-tab-item key="0">Content 1</v-tab-item>
    <v-tab-item key="1">Content 2</v-tab-item>
  </v-tabs-window>
</v-tabs>

<!-- After (Vuetify 3 - sibling structure) -->
<v-tabs v-model="tab">
  <v-tab value="tab1">Tab 1</v-tab>
  <v-tab value="tab2">Tab 2</v-tab>
</v-tabs>

<v-divider></v-divider>

<v-tabs-window v-model="tab">
  <v-window-item value="tab1">Content 1</v-window-item>
  <v-window-item value="tab2">Content 2</v-window-item>
</v-tabs-window>
```

**Key changes:**
- `v-tabs-window` must be outside `v-tabs` (sibling, not child)
- `v-tab-item` renamed to `v-window-item`
- Use `value` prop instead of `key` for tab items
- Use `value` prop instead of text content for tabs
- Add `v-model` to both `v-tabs` and `v-tabs-window`
- Add `v-divider` for visual separation

## Expansion Panels

```html
<!-- Before -->
<v-expansion-panel>
  <v-expansion-panel-content>
    <div slot="header">Header</div>
    <div>Content</div>
  </v-expansion-panel-content>
</v-expansion-panel>

<!-- After -->
<v-expansion-panels>
  <v-expansion-panel>
    <v-expansion-panel-title>Header</v-expansion-panel-title>
    <v-expansion-panel-text>Content</v-expansion-panel-text>
  </v-expansion-panel>
</v-expansion-panels>
```

## Cards

```html
<!-- Before -->
<v-card-title primary-title>
  <h3 class="headline mb-0">Title</h3>
</v-card-title>

<!-- After -->
<v-card-title>
  <h3 class="text-h5">Title</h3>
</v-card-title>
```

## Buttons

```html
<!-- Before -->
<v-btn flat color="secondary">Cancel</v-btn>

<!-- After -->
<v-btn variant="text" color="secondary">Cancel</v-btn>
```

## Data Tables

**Critical:** Vuetify 3 separates client-side and server-side tables.

```html
<!-- Before (Vuetify 2 - single component) -->
<v-data-table
  :headers="headers"
  :items="items"
  :pagination.sync="pagination"
  :total-items="totalItems"
></v-data-table>

<!-- After (Vuetify 3 - client-side data) -->
<v-data-table
  :headers="headers"
  :items="items"
></v-data-table>

<!-- After (Vuetify 3 - server-side data) -->
<v-data-table-server
  :headers="headers"
  :items="items"
  :items-length="totalItems"
  v-model:page="page"
  v-model:items-per-page="itemsPerPage"
  v-model:sort-by="sortBy"
  @update:options="loadFromServer"
></v-data-table-server>
```

**Key changes:**
- Use `v-data-table` for client-side data
- Use `v-data-table-server` for server-side pagination/sorting
- `items-length` instead of `total-items`
- Use `v-model:page`, `v-model:items-per-page`, `v-model:sort-by` instead of `options` object
- `@update:options` event for server-side data loading
- `item-value` must use literal string (not bound)

**Common migration issues:**

```html
<!-- WRONG: dynamic item-value -->
<v-data-table-server :item-value="id"></v-data-table-server>

<!-- CORRECT: literal item-value -->
<v-data-table-server item-value="id"></v-data-table-server>
```

**Custom row templates:**

```html
<!-- Vuetify 3 requires CSS classes on custom rows -->
<v-data-table-server :items="items" :headers="headers">
  <template v-slot:item="{ item }">
    <tr :key="item.id" :class="['v-data-table__tr']">
      <td v-for="header in filteredHeaders" :key="header.value" class="v-data-table__td">
        {{ item[header.value] }}
      </td>
    </tr>
  </template>
</v-data-table-server>
```

## Images

```html
<!-- Before (Vuetify 2 - cover by default) -->
<v-img src="/image.jpg" aspect-ratio="2.75"></v-img>

<!-- After (Vuetify 3 - must add cover) -->
<v-img src="/image.jpg" aspect-ratio="2.75" cover></v-img>
```

**Key change:** Images use `contain` behavior by default in Vuetify 3. Add `cover` prop for full-bleed display.

## Snackbars

```html
<!-- Before (Vuetify 2) -->
<v-snackbar v-model="showing">
  {{ message }}
  <v-btn flat @click="showing = false">Close</v-btn>
</v-snackbar>

<!-- After (Vuetify 3) -->
<v-snackbar v-model="showing">
  {{ message }}
  <template v-slot:actions>
    <v-btn variant="plain" @click="showing = false">
      <v-icon>mdi-close</v-icon>
    </v-btn>
  </template>
</v-snackbar>
```

**Key changes:**
- Action buttons must be in `v-slot:actions`
- `variant="flat"` replaced by `variant="plain"`

## Navigation Sections

```javascript
// Before (Vue 2 - all sections expanded by default)
Navigation.add_section({
  name: "admin",
  icon: "settings",
  text: "Administration"
});

// After (Vue 3 - control initial expansion)
Navigation.add_section({
  name: "admin",
  icon: "settings",
  text: "Administration",
  expanded: true  // Optional: defaults to false
});
```

**Implementation in NavigationDrawer:**
```html
<v-list v-model:opened="openGroups">
  <v-list-group v-if="section.group" :value="section.text">
    <!-- section content -->
  </v-list-group>
</v-list>

<script>
computed: {
  openGroups: {
    get: function() {
      // Return section names that should be expanded
      return this.sections
        .filter(function(section) { return section.group && section.expanded === true; })
        .map(function(section) { return section.text; });
    },
    set: function(value) {
      store.commit('set_open_sections', value);
    }
  }
}
</script>
```

## Calendar Component

**Note:** As of Vuetify 3.11+, Calendar is in core distribution (no Labs required).

```html
<v-calendar
  v-model="focus"
  :events="events"
></v-calendar>

<script>
data: function() {
  return {
    focus: '2019-01-08',  // Set to date range with events
    events: [
      {
        title: 'Event Name',
        start: '2019-01-08',  // Required: YYYY-MM-DD format
        end: '2019-01-10',     // Optional: for multi-day events
        color: 'blue'          // Optional: event color
      }
    ]
  };
}
</script>
```

**Event format:**
- `start` (required): Date string in `YYYY-MM-DD` format
- `end` (optional): End date for multi-day events
- `title` (required): Event title
- `color` (optional): Event color
- `timed` (optional): Boolean for timed events

**Custom event display:**
```html
<v-calendar
  v-model="focus"
  :events="events"
>
  <template v-slot:event="{ event }">
    <div class="pa-1" @click="showEvent(event)">
      <strong>{{ event.title }}</strong>
      <div v-if="event.details">{{ event.details }}</div>
    </div>
  </template>
</v-calendar>
```

## Chart.js Options

```javascript
// Before
options: {
  legend: { display: true }
}

// After
options: {
  plugins: {
    legend: { display: true }
  }
}
```

**Critical:** Baseweb uses Chart.js 2.x, not 3.x. Scale configuration differs:

```javascript
// ❌ WRONG - Chart.js 3.x format (doesn't work in baseweb)
scales: {
  x: { display: true },
  y: { beginAtZero: true }
}

// ✅ CORRECT - Chart.js 2.x format (required for baseweb)
scales: {
  xAxes: [{
    id: 'x-axis-0',
    display: true
  }],
  yAxes: [{
    id: 'y-axis-0',
    display: true,
    ticks: {
      beginAtZero: true
    }
  }]
}
```

**Chart.js 2.x limitations:**
- Cannot replace `chart.options` after creation
- Must destroy and recreate chart when options change
- Scales use `xAxes` and `yAxes` arrays (not `x` and `y` objects)

```javascript
// ✅ CORRECT - Chart.js 2.x update pattern
methods: {
  createChart: function() {
    this.chart = new Chart(ctx, {
      type: 'line',
      data: this.chartData,
      options: this.merged_options
    });
  },
  
  updateChartData: function() {
    // Only update data, not options
    if (this.chart) {
      this.chart.data = this.chartData;
      this.chart.update();
    }
  },
  
  recreateChart: function() {
    // Destroy and recreate for options changes
    if (this.chart) {
      this.chart.destroy();
      this.chart = null;
    }
    this.createChart();
  }
},

watch: {
  chartData: {
    handler: function() { this.updateChartData(); }
  },
  options: {
    handler: function() { this.recreateChart(); }
  }
}
```

### Vue 3 Proxy Reactivity with Third-Party Libraries

**Problem:** Vue 3's Proxy-based reactivity breaks Chart.js and similar libraries when they try to mutate data.

```javascript
// ❌ WRONG - Vue Proxy causes issues
this.chart.data = this.chartData;  // Proxy object!

// ✅ CORRECT - Clone to break reactivity
this.chart.data = JSON.parse(JSON.stringify(this.chartData));
this.chart.options = JSON.parse(JSON.stringify(this.merged_options));
```

**Complete pattern:**
```javascript
methods: {
  createChart: function() {
    var ctx = this.$refs.canvas.getContext('2d');
    // Clone to break Vue 3 Proxy chain
    this.chart = new Chart(ctx, {
      type: 'line',
      data: JSON.parse(JSON.stringify(this.chartData)),
      options: JSON.parse(JSON.stringify(this.merged_options))
    });
  },
  
  updateChartData: function() {
    if (this.chart) {
      // Clone to prevent infinite loops
      this.chart.data = JSON.parse(JSON.stringify(this.chartData));
      this.chart.update();
    }
  }
}
```

---

# Part 4: Common Issues and Solutions

## Issue: Components Not Registering

**Symptom:** "Component x is not found" or component doesn't render.

**Cause:** `app.js` loaded too late, `app` undefined when components register.

**Solution:** Load `app.js` immediately after `vue.js`:

```html
<script src="/static/vendor/js/vue.js"></script>
<script src="/static/js/app.js"></script>  <!-- Must be early! -->
```

## Issue: Icons Not Showing

**Symptom:** Icon buttons are blank or show as text.

**Cause:** Using Material Icons names without MDI prefix.

**Solution:** 
1. Ensure MDI font is loaded
2. Use `mdi-*` prefix on all icons

```html
<v-icon>mdi-menu</v-icon>  <!-- Correct -->
<v-icon>menu</v-icon>      <!-- Wrong -->
```

## Issue: Filters Not Working

**Symptom:** `{{ value | filter }}` shows as literal text.

**Cause:** Vue 3 removed filters.

**Solution:** Use `$filters` global property:

```html
<!-- Before -->
{{ value | filterName }}

<!-- After -->
{{ $filters.filterName(value) }}
```

## Issue: v-layout/v-flex Not Working

**Symptom:** Layout broken, items not positioned correctly.

**Cause:** Vuetify 3 removed `v-layout`/`v-flex`.

**Solution:** Use `v-container`/`v-row`/`v-col`:

```html
<v-container>
  <v-row>
    <v-col cols="12">...</v-col>
  </v-row>
</v-container>
```

## Issue: Socket.io Connected State Not Updating

**Symptom:** Connection indicator stays red even when connected.

**Cause:** Direct property assignment not reactive in Vue 3.

**Solution:** Use `Vue.ref()`:

```javascript
// app.js
var connectedRef = Vue.ref(false);
window._socketConnected = connectedRef;

// socketio.js
window._socketConnected.value = true;
```

## Issue: Vue Form Generator Validators

**Symptom:** `VueFormGenerator.validators is undefined`.

**Cause:** Vue 3 migration removed vue-form-generator.

**Solution:** Remove validator references or use VuetifyFormGenerator's built-in validation:

```javascript
// Before
validator: VueFormGenerator.validators.string

// After - use required and min attributes
required: true,
min: 3
```

## Issue: `this.$set is not a function`

**Symptom:** Form fields throw error when typing: `TypeError: this.$set is not a function`.

**Cause:** Vue 3 removed `this.$set` - Proxy-based reactivity doesn't need it.

**Solution:** Replace `$set` with direct assignment:

```javascript
// Before (Vue 2)
this.$set(obj, key, value);
this.$set(this.errors, field, error);

// After (Vue 3)
obj[key] = value;
this.errors[field] = error;
```

## Issue: `notify is not defined`

**Symptom:** `ReferenceError: Can't find variable: notify`.

**Cause:** `window.notify` was defined in static store.js which gets overridden by template store.js.

**Solution:** Move notification system to template store.js:

```javascript
// templates/store.js - must include notification system
var store = Vuex.createStore({
  state: {
    config: {{ app.toDict() | tojson }},
    notifications: []  // Queue of notifications
  },
  mutations: {
    notify: function(state, payload) {
      state.notifications.push({ id: ++notificationId, ...payload });
    },
    remove_notification: function(state, id) {
      // Remove by id
    }
  }
});

// Global helpers
window.notify = function(options) {
  store.commit('notify', options);
};
```

## Issue: Navigation Drawer Sections Collapsing Together

**Symptom:** Clicking one section collapses all sections.

**Cause:** All `v-list-group` components had the same `value`, causing shared state.

**Solution:** Use unique values per group and avoid `:to` on list items:

```javascript
// Use unique value per section
<v-list-group :value="section.text">

// Use click handler instead of :to for navigation
<v-list-item @click="navigate" :active="isActive">
```

## Issue: Logo/Icon Not Showing in App Bar

**Symptom:** Custom logo component doesn't appear in app bar, shows `<v-icon>Logo</v-icon>`.

**Cause:** Template not distinguishing between MDI icons and custom components.

**Solution:** Detect component vs MDI icon:

```html
<v-btn icon @click="toggle_drawer">
  {% if app.icon and not app.icon.startswith('mdi-') %}
    <!-- Custom component (e.g., "Logo") -->
    <component :is="'{{ app.icon }}'" style="width:40px;height:40px"></component>
  {% else %}
    <!-- MDI icon or default menu icon -->
    <v-icon>{{ app.icon or 'mdi-menu' }}</v-icon>
  {% endif %}
</v-btn>
```

## Issue: Vuetify Labs Components Not Working

**Symptom:** Calendar and other Labs components fail to render.

**Cause:** Vuetify Labs requires special bundling - the CDN files don't merge automatically.

**Solution:** Use a bundler (Vite/Webpack) that imports from `vuetify/labs/components`:

```javascript
// Requires build step
import { VCalendar } from 'vuetify/labs/components'

// CDN approach doesn't work - Labs overwrites Vuetify global
```

**Note:** As of Vuetify 3.11+, Calendar is in core distribution and doesn't require Labs:

```html
<!-- Calendar is now in core Vuetify 3 -->
<v-calendar
  v-model="focus"
  :events="events"
></v-calendar>

<script>
data: function() {
  return {
    focus: '2019-01-08',  // Set to event date range
    events: [
      { title: 'Event', start: '2019-01-08', color: 'blue' }
    ]
  };
}
</script>
```

## Issue: Chart.js TypeError "scales.xAxes.concat"

**Symptom:** `TypeError: undefined is not an object (evaluating 'e.scales.xAxes.concat')`

**Cause:** Using Chart.js 3.x scale format with Chart.js 2.x library.

**Solution:** Use Chart.js 2.x scale format:

```javascript
// Wrong - Chart.js 3.x format
scales: {
  x: { display: true },
  y: { beginAtZero: true }
}

// Correct - Chart.js 2.x format
scales: {
  xAxes: [{
    id: 'x-axis-0',
    display: true
  }],
  yAxes: [{
    id: 'y-axis-0',
    ticks: { beginAtZero: true }
  }]
}
```

## Issue: "undefined is not a object (evaluating 'header.value')"

**Symptom:** TypeError when component mounts with `v-for` and `v-if` on same element.

**Cause:** Vue 3 gives `v-if` higher priority than `v-for`.

**Solution:** Use computed property or template wrapper:

```javascript
// Wrong
<td v-for="header in headers" v-if="header.value">

// Correct - computed property
computed: {
  filteredHeaders: function() {
    return this.headers.filter(function(h) {
      return h.value !== '' && h.value !== undefined;
    });
  }
}
<td v-for="header in filteredHeaders" :key="header.value">
```

## Issue: Browser Freezes When Updating Chart Data

**Symptom:** Browser becomes unresponsive when chart data changes.

**Cause:** Vue 3 Proxy reactivity causes infinite loop with Chart.js internal mutations.

**Solution:** Clone data before passing to Chart.js:

```javascript
// Always clone
this.chart.data = JSON.parse(JSON.stringify(this.chartData));
this.chart.options = JSON.parse(JSON.stringify(this.mergedOptions));
```

## Issue: CollectionView Shows Duplicate Rows

**Symptom:** Data table shows duplicate or missing rows on pagination.

**Cause:** Multiple issues:
1. Using `v-data-table` instead of `v-data-table-server`
2. `item-value` bound as dynamic prop instead of literal
3. Multiple `@update:options` handlers causing race conditions
4. Array reference issues in computed properties

**Solution:**

```html
<!-- Use v-data-table-server for server-side data -->
<v-data-table-server
  :items="model.results"
  :items-length="model.totalElements"
  item-value="id"
  @update:options="onOptionsUpdate"
>
  <!-- ... -->
</v-data-table-server>

<script>
methods: {
  // Use event parameter, not stale v-model
  onOptionsUpdate: function(options) {
    if (options.page !== undefined) this.tableOptions.page = options.page;
    if (options.itemsPerPage !== undefined) this.tableOptions.itemsPerPage = options.itemsPerPage;
    this.search();
  },
  
  // Prevent race conditions
  search: async function() {
    if (this.searchInProgress) return;
    this.searchInProgress = true;
    // ... fetch data
    this.searchInProgress = false;
  }
},

computed: {
  // Return array directly, not mapped copy
  rows: function() {
    return this.model.results;  // Not .map(item => item)
  }
}
</script>
```

## Issue: Calendar Not Showing Events

**Symptom:** Calendar displays but events don't appear.

**Cause:** Events in wrong format or calendar showing wrong date range.

**Solution:**

```javascript
// Events need start/end timestamps
events: [
  { 
    title: 'Event', 
    start: '2019-01-08',  // Required
    end: '2019-01-10',     // Optional (for multi-day)
    color: 'blue' 
  }
]

// Set focus to event date range
data: function() {
  return {
    focus: '2019-01-08',  // Show Jan 2019, not today
    events: [...]
  };
}
```

---

# Part 5: Migration Checklist

## Backend (Flask → Quart)

- [ ] Update dependencies (Flask → Quart)
- [ ] Update imports (flask → quart, flask_restful → baseweb)
- [ ] Convert sync methods to async
- [ ] Add `await` to `request.get_json()` calls
- [ ] Replace `server.api.add_resource()` with `server.add_resource()`
- [ ] Migrate Socket.IO handlers (add `sid`, `async`, `await`)
- [ ] Create `asgi_app` entry point
- [ ] Update run command (gunicorn + uvicorn)

## Frontend (Vue 2 → Vue 3)

- [ ] Move `app.js` to load immediately after `vue.js`
- [ ] Replace `Vue.component()` with `app.component()`
- [ ] Convert filters to global properties
- [ ] Replace `app.$notify()` with `notify()`
- [ ] Update socketio.js to use `Vue.ref()` for connection state
- [ ] Replace `this.$set()` with direct assignment
- [ ] Move notification system to template store.js (not static)
- [ ] Update navigation drawer to use unique section values
- [ ] Detect logo component vs MDI icon in app bar

## UI (Vuetify 2 → Vuetify 3)

- [ ] Install and load MDI font
- [ ] Update all icon names to `mdi-*` prefix
- [ ] Replace `v-layout`/`v-flex` with `v-container`/`v-row`/`v-col`
- [ ] Replace `v-toolbar` with `v-app-bar`
- [ ] Replace `v-content` with `v-main`
- [ ] **Fix v-tabs structure** (siblings, not nested)
  - [ ] Move `v-tabs-window` outside `v-tabs`
  - [ ] Rename `v-tab-item` to `v-window-item`
  - [ ] Use `value` props instead of `key`
- [ ] **Fix v-if/v-for priority**
  - [ ] Use computed properties for filtered lists
  - [ ] Or use template wrapper pattern
- [ ] **Fix v-data-table for server-side data**
  - [ ] Use `v-data-table-server` instead of `v-data-table`
  - [ ] Convert `:pagination.sync` to `v-model:page`, `v-model:items-per-page`, `v-model:sort-by`
  - [ ] Use `item-value` as literal, not bound
- [ ] **Add `cover` prop to `v-img` components**
- [ ] **Fix v-snackbar actions**
  - [ ] Move buttons to `v-slot:actions`
  - [ ] Change `variant="flat"` to `variant="plain"`
- [ ] **Fix navigation sections**
  - [ ] Add `expanded` property to control initial state
  - [ ] Use `v-model:opened` on `v-list`
  - [ ] Set unique `value` on each `v-list-group`
- [ ] Update expansion panels (title/text structure)
- [ ] Update card titles (remove `primary-title`, use `text-h*` classes)
- [ ] Update button variants (`flat` → `variant="text"`)

## Chart.js (If Using Charts)

- [ ] **Use Chart.js 2.x format** (not 3.x)
  - [ ] Use `xAxes`/`yAxes` arrays instead of `x`/`y` objects
  - [ ] Add `id` property to each axis
- [ ] **Handle Vue 3 Proxy reactivity**
  - [ ] Clone data before passing to Chart.js: `JSON.parse(JSON.stringify(data))`
  - [ ] Clone options too
- [ ] **Use separate methods for data vs options updates**
  - [ ] `updateChartData()` - only updates data
  - [ ] `recreateChart()` - destroys and recreates for options changes

## Testing

- [ ] Run tests and verify all pass
- [ ] Manual testing of all pages
- [ ] Verify icons display correctly
- [ ] Verify socket.io connection indicator
- [ ] Verify forms work
- [ ] Verify routing works

---

# Part 6: Quick Reference Card

## Icon Quick Reference

```
menu        → mdi-menu
home        → mdi-home
close       → mdi-close
edit        → mdi-pencil
delete      → mdi-delete
search      → mdi-magnify
add_circle  → mdi-plus-circle
refresh     → mdi-refresh
layers      → mdi-layers
web         → mdi-web
extension   → mdi-puzzle
description → mdi-text-box
cloud_done  → mdi-cloud-check
cloud_off   → mdi-cloud-off
information → mdi-information
```

## Component Quick Reference

```
Vue.component()     → app.component()
{{ value | filter }} → {{ $filters.filter(value) }}
app.$notify()       → notify()
v-layout/v-flex     → v-container/v-row/v-col
v-toolbar           → v-app-bar
v-content           → v-main
v-tab-item          → v-tabs-window > v-tab-item
v-expansion-panel-content → v-expansion-panel-text
slot="header"       → #header or <template #header>
primary-title       → (removed)
headline            → text-h5
flat                → variant="flat"
dark                → theme="dark"
```

## See Also

- [Vuetify 3 Migration Guide](https://vuetifyjs.com/en/getting-started/upgrade-guide/)
- [Vue 3 Migration Guide](https://v3-migration.vuejs.org/)
- [baseweb-demo](https://github.com/christophevg/baseweb-demo) - Reference implementation