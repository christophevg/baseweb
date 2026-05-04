# Task 3.11: Vue 3 + Vuetify 3 Migration - Charts and Notifications

**Completed:** 2026-05-04

## Summary

Migrated LineChart.js to use Chart.js directly (vue-chartjs v4 has no UMD build). Notifications already migrated in task-3.10 via NotificationSnackbar.

## Approach: Chart.js Direct

Since vue-chartjs v4 has no UMD build available, we use Chart.js directly as a framework-agnostic solution that works with the no-build setup.

## Files Modified

### LineChart.js

**Before (vue-chartjs v3):**
```javascript
extends: VueChartJs.Line,
mounted: function() {
  this.renderChart(this.chartData, this.options);
}
```

**After (Chart.js direct):**
```javascript
template: '<canvas ref="canvas"></canvas>',
mounted: function() {
  var ctx = this.$refs.canvas.getContext('2d');
  this.chart = new Chart(ctx, {
    type: 'line',
    data: this.chartData,
    options: this.normalizedOptions
  });
}
```

### main.html

- Removed `<script src="/static/vendor/js/vue-chartjs.min.js"></script>`
- Replaced `<notifications group="notifications" .../>` with `<notification-snackbar>`

## Chart.js v4 API Changes

| Chart.js v2/v3 | Chart.js v4 |
|----------------|-------------|
| `legend: { display: true }` | `plugins: { legend: { display: true } }` |
| `scales: { yAxes: [{ ticks: { beginAtZero } }] }` | `scales: { y: { beginAtZero: true } }` |

## Key Features

- **Reactive updates**: Watch on `chartData` and `options` props
- **Deep merge**: Custom `deepMerge()` utility replaces jQuery's `$.extend(true, ...)`
- **Cleanup**: `beforeUnmount` hook destroys chart to prevent memory leaks
- **Prop validation**: Proper type checking for chartData and options

## Notifications

Already replaced in task-3.10:
- Created `store.js` with notification module
- Created `NotificationSnackbar.js` using Vuetify's `v-snackbar`
- Usage: `store.commit('notify_success', { text: 'Saved!' })`

## Test Results

- **144 tests passed**
- Coverage: 78%

## Testing Recommendations

1. Chart rendering with existing data format
2. Reactive updates when data changes
3. Memory cleanup on component unmount
4. All notification types via NotificationSnackbar

## Next Steps

Task 3.12 will perform full integration testing and validate against baseweb-demo.