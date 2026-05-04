# Task 3.7: Vue 3 + Vuetify 3 Migration - Simple Components

**Completed:** 2026-05-04

## Summary

Successfully updated simple components for Vuetify 3 compatibility. Changes were minimal - only 2 files required modifications.

## Files Modified

### 1. PageWithBanner.js

Changed v-alert prop for Vuetify 3:

```javascript
// Before (Vuetify 1.5/2)
:dismissible="banner.dismissible"

// After (Vuetify 3)
:closable="banner.dismissible"
```

Vuetify 3 renamed `dismissible` to `closable` for consistency with other components.

### 2. PageWithStatus.js

Changed v-snackbar and v-btn props:

```javascript
// Before (Vuetify 1.5/2)
<v-snackbar top ...>
  <v-btn dark flat ...>

// After (Vuetify 3)
<v-snackbar location="top" ...>
  <v-btn variant="flat" ...>
```

Changes:
- `top` → `location="top"` (Vuetify 3 uses `location` prop for positioning)
- `dark` removed (Vuetify 3 uses theme system)
- `flat` → `variant="flat"` (Vuetify 3 uses `variant` for button styles)

## Files Not Modified

| File | Reason |
|------|--------|
| Page.js | No Vuetify dependencies, simple wrapper |
| ProcessDiagram.js | v-card components compatible with Vuetify 3 |
| common.js | Filter registration works via compatibility shim |

## Filter Migration

No filter syntax migration was needed - none of the simple components used the Vue 2 filter pipe syntax (`${ value | filter }`).

## Vuetify 3 Prop Changes Reference

| Component | Vue 2 Prop | Vue 3 Prop |
|-----------|------------|------------|
| v-alert | `dismissible` | `closable` |
| v-snackbar | `top`, `bottom`, `left`, `right` | `location="top"` etc. |
| v-btn | `flat`, `outline`, `depressed` | `variant="flat"`, `variant="outlined"`, `variant="tonal"` |
| v-btn | `dark` | (removed - use theme) |

## Test Results

- **144 tests passed**
- Coverage: 78%

## Next Steps

Task 3.8 will update NavigationDrawer.js with Vuetify 3 component names:
- `v-list-tile` → `v-list-item`
- `v-list-tile-content` → `v-list-item-content`
- `v-list-tile-title` → `v-list-item-title`
- `v-list-tile-action` → `v-list-item-action`