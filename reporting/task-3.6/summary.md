# Task 3.6: Vue 3 + Vuetify 3 Migration - App Initialization

**Completed:** 2026-05-04

## Summary

Successfully migrated the app initialization from Vue 2 to Vue 3, including Vue Router 4 and Vuex 4. Added compatibility shims to preserve Vue 2-style global registration patterns.

## Files Modified

### 1. `src/baseweb/templates/main.html`

Added Vue 3 compatibility shims and Vuetify 3 initialization:

```javascript
// Vue 3 compatibility shims
window._queuedComponents = [];
window._queuedFilters = [];
window._queuedMixins = [];
window._queuedPlugins = [];

Vue.component = function(name, definition) {
  window._queuedComponents.push({name, definition});
};
Vue.filter = function(name, fn) {
  window._queuedFilters.push({name, fn});
};
Vue.mixin = function(mixin) {
  window._queuedMixins.push(mixin);
};
Vue.use = function(plugin, options) {
  window._queuedPlugins.push({plugin, options});
};
```

Final initialization:
- Creates Vuetify instance with `Vuetify.createVuetify()`
- Installs store and router on app
- Applies queued plugins, components, mixins
- Stores filters in `app.config.globalProperties.$filters`

### 2. `src/baseweb/static/js/app.js`

```javascript
// Before (Vue 2)
var app = new Vue({...});

// After (Vue 3)
var app = Vue.createApp({...});
```

### 3. `src/baseweb/static/js/router.js`

```javascript
// Before (Vue Router 3)
var router = new VueRouter({
  mode: 'history',
  routes: [...]
});

// After (Vue Router 4)
var router = VueRouter.createRouter({
  history: VueRouter.createWebHistory(),
  routes: [...]
});
```

### 4. `src/baseweb/templates/store.js`

```javascript
// Before (Vuex 3)
var store = new Vuex.Store({...});

// After (Vuex 4)
var store = Vuex.createStore({...});
```

### 5. `src/baseweb/static/js/components/NavigationDrawer.js`

```javascript
// Before (Vue Router 3)
router.addRoutes([...]);

// After (Vue Router 4)
router.addRoute({...});  // One route at a time
```

### 6. `tests/test_baseweb_async.py`

Updated test assertion for Vuex 4:
```python
# Before
assert b"Vuex.Store" in content

# After
assert b"Vuex.createStore" in content
```

## Vue 2 → Vue 3 API Changes

| Feature | Vue 2 | Vue 3 |
|---------|-------|-------|
| App creation | `new Vue({...})` | `Vue.createApp({...})` |
| Router creation | `new VueRouter({...})` | `VueRouter.createRouter({...})` |
| History mode | `mode: 'history'` | `history: VueRouter.createWebHistory()` |
| Store creation | `new Vuex.Store({...})` | `Vuex.createStore({...})` |
| Global component | `Vue.component()` | `app.component()` (via shim) |
| Global filter | `Vue.filter()` | Removed (via shim → `$filters`) |
| Global mixin | `Vue.mixin()` | `app.mixin()` (via shim) |
| Plugin install | `Vue.use()` | `app.use()` (via shim) |
| Add routes | `router.addRoutes([...])` | `router.addRoute({...})` |

## Known Issues (Deferred to Later Tasks)

### Filters (Task 3.7+)
Vue 3 removed filters. Templates using `${ value | filterName }` need to be updated to `${ $filters.filterName(value) }`.

### Vuetify 2 Component Names (Task 3.8)
Templates still use Vuetify 2 component names:
- `v-list-tile` → `v-list-item`
- `v-list-tile-content` → `v-list-item-content`
- etc.

### vue-notification (Task 3.11)
This library is Vue 2 only. Replace with Vuetify snackbar.

### vue-form-generator (Task 3.9)
This library is Vue 2 only. Create Vuetify 3 replacement.

## Test Results

- **144 tests passed**
- 1 test updated for Vuex 4 syntax
- Coverage: 78%

## Next Steps

Task 3.7 will update simple components (Page, PageWithBanner, PageWithStatus, ProcessDiagram) to work with Vue 3, including filter syntax updates.