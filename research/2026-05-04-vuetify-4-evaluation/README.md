# Vuetify 4 Evaluation for Baseweb Migration

**Research Date:** 2026-05-04
**Purpose:** Evaluate Vuetify 4 for baseweb migration from Vuetify 1.5/Vue 2
**Previous Research:** `2026-05-04-vuetify-build-requirements/`

---

## Executive Summary

Vuetify 4 was released February 23, 2026 and is fully compatible with Vue 3. For baseweb's migration from Vuetify 1.5/Vue 2, there is **no direct migration path** - the migration must follow the sequence: Vuetify 1.5 -> 2 -> 3 -> 4. Vuetify 4 CDN bundle is ~1,016 KB (JS: 556 KB, CSS: 460 KB), which is similar to baseweb's current 1.0 MB vuetify.js. The main new features in Vuetify 4 are CSS cascade layers, Material Design 3 support, and grid system overhaul - but these come with significant breaking changes from Vuetify 3.

---

## 1. Major Changes from Vuetify 3 to Vuetify 4

### Key Findings

- Released February 23, 2026 [1]
- Material Design 3 (MD3) integration with streamlined elevation (6 levels vs 25) [2]
- CSS cascade layers for better style specificity [2]
- Grid system overhaul using CSS gap instead of negative margins [1]
- System theme by default (respects OS dark/light preference) [1]

### Details

**CSS Cascade Layers:**
Vuetify 4 uses five top-level CSS layers:
- `vuetify-core`
- `vuetify-components`
- `vuetify-utilities`
- `vuetify-overrides`
- `vuetify-final`

This eliminates specificity wars - custom styles now take priority without `!important` hacks [2].

**Grid System Changes:**
- `VRow` now uses CSS `gap` instead of negative margins
- New `density` prop: `default`, `comfortable`, `compact`
- Deprecated props moved to utility classes:
  - `align`, `justify`, `alignContent` -> `align-*`, `justify-*` classes
  - `order` on `VCol` -> `order-*` classes
  - `dense` -> `density="comfortable"`
  - `noGutters` -> `density="compact"`
- Offset classes renamed: `.offset-*` -> `.v-col--offset-*`

**Breakpoint Changes:**
| Breakpoint | Vuetify 3 | Vuetify 4 |
|------------|-----------|-----------|
| md | 960px | 840px |
| xl | 1920px | 1545px |

**Sources:**
- [1] GitHub v4.0.0 Release Notes
- [2] Medium Article - Vuetify 4 is Live Now

---

## 2. Breaking Changes for Migration from Vuetify 1.5

### Key Findings

- **No direct migration path** from Vuetify 1.5 to Vuetify 3/4 [3]
- Must migrate: Vuetify 1.5 -> 2 -> 3 -> 4
- Each step has significant breaking changes
- Vuetify 1.5 and 2.x are NOT compatible with Vue 3

### Details

**Vuetify 1.5 to 2.x Breaking Changes:**
- Framework restructure (new plugin system)
- Component prop renames
- Slot naming changes

**Vuetify 2.x to 3.x Breaking Changes:**
- `Vuetify` class removed -> use `createVuetify()` function
- Import structure: `'vuetify/lib'` -> `'vuetify'` or `'vuetify/components'`
- `value` prop -> `model-value` (Vue 3 requirement)
- `@input` event -> `@update:model-value`
- `background-color` -> `bg-color`
- `filled`/`outlined`/`solo` props -> single `variant` prop

**Component Renames (Vuetify 2 -> 3):**
| Old (v2) | New (v3) |
|----------|----------|
| `v-simple-table` | `v-table` |
| `v-tab-item` | `v-window-item` |
| `v-expansion-panel-header` | `v-expansion-panel-title` |
| `v-expansion-panel-content` | `v-expansion-panel-text` |
| `v-subheader` | `v-list-subheader` |

**Vuetify 3 to 4 Breaking Changes:**
- `VSnackbar`: `multi-line` prop removed
- `VSelect/VAutocomplete/VCombobox`: `item` slot renamed to `internalItem`
- `VBtn`: grid display changed to flex
- Default theme changed from "light" to "system"

**Sources:**
- [3] Vuetify 3 Upgrade Guide

---

## 3. Vue 3 Compatibility

### Key Findings

- Vuetify 4 **requires Vue 3** (no Vue 2 support) [3]
- Vuetify 3 also requires Vue 3
- Vuetify 1.5 and 2.x are NOT compatible with Vue 3 [4]

### Details

For baseweb currently using Vuetify 1.5 with Vue 2:
- Cannot upgrade Vue without upgrading Vuetify
- Cannot use Vuetify 1.5 with Vue 3
- Must upgrade both together (Vue 2 -> 3 and Vuetify 1.5 -> 3 or 4)

**Sources:**
- [3] Vuetify 3 Upgrade Guide
- [4] Previous research - Vuetify Build Requirements

---

## 4. CDN/Bundle Availability

### Key Findings

- Vuetify 4 CDN available via jsDelivr and unpkg [5]
- CDN bundle includes ALL components (no tree shaking)
- Vue 3 global build required (separate CDN)

### Bundle Size Comparison

| Version | JS (min) | CSS (min) | Total |
|---------|----------|-----------|-------|
| Vuetify 1.5 | ~1,000 KB (baseweb's vuetify.js) | - | ~1.0 MB |
| Vuetify 3.7.6 | 410.68 KB | 433.7 KB | ~844 KB |
| Vuetify 4.0.6 | 556.39 KB | 459.86 KB | ~1,016 KB |

**Note:** Vuetify 4 CDN bundle is ~20% larger than Vuetify 3. This is because Vuetify 4 includes additional MD3 styles and CSS cascade layer infrastructure.

**CDN Usage:**
```html
<link href="https://cdn.jsdelivr.net/npm/vuetify@4.0.6/dist/vuetify.min.css" rel="stylesheet" />
<script src="https://cdn.jsdelivr.net/npm/vue@3/dist/vue.global.prod.js"></script>
<script src="https://cdn.jsdelivr.net/npm/vuetify@4.0.6/dist/vuetify.min.js"></script>
<script>
  const { createApp } = Vue
  const { createVuetify } = Vuetify
  const app = createApp()
  app.use(createVuetify()).mount('#app')
</script>
```

**Sources:**
- [5] jsDelivr CDN
- [6] Vuetify 4 Installation Docs

---

## 5. Migration Path Analysis

### Option A: Direct to Vuetify 4

**Pros:**
- Latest version with MD3 and CSS cascade layers
- Active support and updates
- Better long-term maintenance

**Cons:**
- Most breaking changes to handle
- Larger bundle size (~1 MB)
- Must handle 1.5 -> 2 -> 3 -> 4 migration

### Option B: Migrate to Vuetify 3 First

**Pros:**
- Smaller bundle size (~844 KB)
- More mature/stable
- More migration resources available
- Can upgrade to Vuetify 4 later

**Cons:**
- Still requires 1.5 -> 2 -> 3 migration
- Will need another migration to Vuetify 4
- Missing MD3 and CSS layers

### Migration Effort Estimate

| Step | Changes Required |
|------|------------------|
| Vuetify 1.5 -> 2 | Plugin system, component renames, slots |
| Vuetify 2 -> 3 | `createVuetify()`, `model-value`, `variant`, `v-table` |
| Vuetify 3 -> 4 | `internalItem` slot, `density` prop, theme default |

---

## Comparison: Vuetify 3 vs Vuetify 4 for Migration

| Aspect | Vuetify 3 | Vuetify 4 |
|--------|-----------|-----------|
| Vue Version | Vue 3 only | Vue 3 only |
| Bundle Size (CDN) | ~844 KB | ~1,016 KB |
| Material Design | MD2 | MD3 |
| CSS Layers | No | Yes (5 layers) |
| Grid System | Negative margins | CSS gap |
| Elevation Levels | 25 | 6 |
| Default Theme | Light | System |
| Stability | Mature | New (Feb 2026) |
| Support | Maintenance | Active development |

---

## Key Takeaways

1. **No direct migration path** exists from Vuetify 1.5 to Vuetify 3/4. Must migrate through Vuetify 2.

2. **Vuetify 4 CDN bundle (~1 MB)** is similar in size to baseweb's current Vuetify 1.5 bundle (~1 MB), so bundle size is not a deciding factor.

3. **Vuetify 3 is smaller** (~844 KB) than Vuetify 4, offering ~20% reduction in CDN bundle size.

4. **Both require Vue 3**, which means baseweb must migrate from Vue 2 to Vue 3 regardless of Vuetify version choice.

5. **CSS cascade layers in Vuetify 4** could simplify custom styling by eliminating specificity issues.

---

## Recommendation for Baseweb

**Recommended Path: Migrate to Vuetify 3 first, then plan Vuetify 4 upgrade**

**Rationale:**
1. Vuetify 3 is more mature with more migration resources
2. Smaller bundle size (~844 KB vs ~1,016 KB)
3. Easier testing ground for Vue 3 migration
4. Can upgrade to Vuetify 4 later (fewer changes between 3 -> 4 than 1.5 -> 3)

**Migration Steps:**
1. Stay on Vue 2, upgrade Vuetify 1.5 -> 2.x
2. Migrate Vue 2 -> Vue 3 + Vuetify 3
3. Optionally upgrade Vuetify 3 -> 4 later

**Alternative for immediate Vuetify 4:**
- Skip Vuetify 3 entirely and migrate directly to Vuetify 4
- Same migration path (1.5 -> 2 -> 3 -> 4), just skip installing Vuetify 3
- More breaking changes to handle at once, but only one migration effort

---

## Sources

[1] GitHub v4.0.0 Release Notes - https://github.com/vuetifyjs/vuetify/releases/tag/v4.0.0 - Accessed 2026-05-04

[2] Medium Article - Vuetify 4 is Live Now - https://medium.com/@nakranirakesh/vuetify-4-is-live-now-45dce07fb95a - Accessed 2026-05-04

[3] Vuetify 3 Upgrade Guide - https://v3.vuetifyjs.com/en/getting-started/upgrade-guide/ - Accessed 2026-05-04

[4] Previous Research - Vuetify Build Requirements - research/2026-05-04-vuetify-build-requirements/ - Accessed 2026-05-04

[5] jsDelivr CDN - https://cdn.jsdelivr.net/npm/vuetify@4.0.6/dist/ - Accessed 2026-05-04

[6] Vuetify 4 Installation Docs - https://v4.vuetifyjs.com/en/getting-started/installation/ - Accessed 2026-05-04