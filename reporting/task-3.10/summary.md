# Task 3.10: Vue 3 + Vuetify 3 Migration - CollectionView Component

**Completed:** 2026-05-04

## Summary

Successfully migrated CollectionView.js to Vuetify 3, the most complex component in baseweb. Removed jQuery dependency and vue-notification.

## Files Modified/Created

### New Files

- `src/baseweb/static/js/store.js` - Vuex store with notification module
- `src/baseweb/static/js/components/NotificationSnackbar.js` - Vuetify 3 notification

### Modified Files

- `src/baseweb/static/js/components/CollectionView.js` - Full Vuetify 3 migration
- `src/baseweb/templates/main.html` - Updated script loading order

## v-data-table API Changes

| Vuetify 1.5 | Vuetify 3 |
|-------------|-----------|
| `:pagination.sync="pagination"` | `v-model:options="options"` |
| `:total-items="total"` | `:items-length="total"` |
| `slot="items" slot-scope="row"` | `v-slot:item="{ item }"` |
| `pagination.rowsPerPage` | `options.itemsPerPage` |
| `pagination.sortBy` (string) | `options.sortBy` (array of `{key, order}`) |

## jQuery AJAX → Fetch API

```javascript
// Before (jQuery)
$.ajax({
  url: '/api/items',
  method: 'GET',
  success: (data) => { ... },
  error: (err) => { ... }
});

// After (fetch)
try {
  const response = await fetch('/api/items');
  const data = await response.json();
  // success handling
} catch (error) {
  // error handling
}
```

## vue-notification → Vuetify Snackbar

Created notification store module:

```javascript
// store.js
const notification = {
  namespaced: true,
  state: { message: '', color: 'info', showing: false },
  mutations: {
    notify(state, { message, color }) { ... },
    notify_success(state, message) { ... },
    notify_error(state, message) { ... },
    ...
  }
}
```

NotificationSnackbar component uses Vuetify's `v-snackbar`.

## Vuetify 3 Prop Updates

| Component | Old | New |
|-----------|-----|-----|
| v-btn | `flat` | `variant="text"` |
| v-pagination | `circle` | `rounded="circle"` |
| v-pagination | `@input` | `@update:modelValue` |
| v-text-field | `append-icon` | `append-inner-icon` |
| Typography | `class="headline"` | `class="text-h5"` |
| Utility | `text-xs-center` | `text-center` |

## Test Results

- **144 tests passed**
- Coverage: 78%

## What to Test

1. Data table rendering
2. Pagination controls (page numbers, items per page)
3. Sorting by column headers
4. CRUD operations (create, read, update, delete)
5. Search functionality
6. Notifications (success and error cases)

## Next Steps

Task 3.11 will update charts (vue-chartjs) and finalize notifications.