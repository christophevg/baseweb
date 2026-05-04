# Vuetify 4 Evaluation for Baseweb Migration

**Analysis Date:** 2026-05-04
**Purpose:** Compare Vuetify 3 vs Vuetify 4 as migration targets for baseweb's Vuetify 1.5/Vue 2 stack

---

## Executive Summary

For baseweb's migration from Vuetify 1.5/Vue 2 to Vue 3, **Vuetify 3 is the recommended intermediate target** due to smaller bundle size and more mature migration resources. Vuetify 4 offers Material Design 3 and CSS cascade layers but comes with a larger bundle and additional breaking changes. The migration path requires going through Vuetify 2 regardless of final target version.

---

## Version Comparison

| Aspect | Vuetify 3 | Vuetify 4 | Notes |
|--------|-----------|-----------|-------|
| **Release Date** | 2022 | Feb 2026 | Vuetify 4 is brand new |
| **Vue Version** | Vue 3 only | Vue 3 only | Both require Vue 3 |
| **Bundle Size (CDN)** | ~844 KB | ~1,016 KB | 20% larger for Vuetify 4 |
| **Material Design** | MD2 | MD3 | Vuetify 4 has latest MD |
| **CSS Layers** | No | Yes (5 layers) | Eliminates `!important` hacks |
| **Grid System** | Negative margins | CSS gap | Vuetify 4 is cleaner |
| **Elevation Levels** | 25 | 6 | Simplified in Vuetify 4 |
| **Default Theme** | Light | System | Vuetify 4 respects OS preference |
| **Stability** | Mature | New | Vuetify 3 is battle-tested |

---

## Bundle Size Analysis

### Current State (Vuetify 1.5)

- baseweb's `vuetify.js`: **~1.0 MB** (from vendor folder)

### Migration Targets

| Version | JS (min) | CSS (min) | Total | Gzipped (est) |
|---------|----------|-----------|-------|---------------|
| Vuetify 3.7.6 | 410.68 KB | 433.7 KB | **~844 KB** | ~245 KB |
| Vuetify 4.0.6 | 556.39 KB | 459.86 KB | **~1,016 KB** | ~290 KB |

**Key Insight:** Vuetify 4 CDN bundle is similar to baseweb's current Vuetify 1.5 bundle (~1 MB). Vuetify 3 offers a ~15% size reduction.

**Note:** All CDN bundles include ALL components. Tree shaking with Vite/Webpack can significantly reduce these sizes.

---

## Migration Path

### No Direct Path from Vuetify 1.5

```
Vuetify 1.5 -> Vuetify 2 -> Vuetify 3 -> Vuetify 4
              (Vue 2)      (Vue 3)       (Vue 3)
```

Both Vuetify 3 and 4 require going through this migration sequence. The main question is whether to stop at Vuetify 3 or continue to Vuetify 4.

### Breaking Changes Summary

**Vuetify 1.5 -> 2:**
- New plugin system
- Component renames
- Slot naming changes

**Vuetify 2 -> 3:**
- `Vuetify` class removed -> `createVuetify()`
- `value` -> `model-value` (Vue 3 requirement)
- `background-color` -> `bg-color`
- `v-simple-table` -> `v-table`
- `filled`/`outlined`/`solo` -> single `variant` prop

**Vuetify 3 -> 4:**
- `VSnackbar`: `multi-line` prop removed
- `item` slot -> `internalItem` slot
- Grid props moved to utility classes (`align`, `justify`, `order`)
- `dense` -> `density="comfortable"`
- `noGutters` -> `density="compact"`
- Theme default: `light` -> `system`

---

## Component API Changes Affecting Baseweb

Based on common baseweb component patterns, these changes will require updates:

### Grid System (Vuetify 4)

```html
<!-- Before (Vuetify 3) -->
<v-row dense align="center">
  <v-col order="last">
    <!-- content -->
  </v-col>
</v-row>

<!-- After (Vuetify 4) -->
<v-row density="comfortable" class="align-center">
  <v-col class="order-last">
    <!-- content -->
  </v-col>
</v-row>
```

### Form Components (Vuetify 3)

```html
<!-- Before (Vuetify 1.5) -->
<v-text-field
  v-model="value"
  background-color="grey"
  filled
/>

<!-- After (Vuetify 3/4) -->
<v-text-field
  v-model="value"
  bg-color="grey"
  variant="filled"
/>
```

### Tables

```html
<!-- Before (Vuetify 1.5) -->
<v-simple-table>
  <!-- content -->
</v-simple-table>

<!-- After (Vuetify 3/4) -->
<v-table>
  <!-- content -->
</v-table>
```

---

## CDN/Bundle Availability

Both Vuetify 3 and 4 are available via CDN:

**Vuetify 3:**
```html
<link href="https://cdn.jsdelivr.net/npm/vuetify@3.7.6/dist/vuetify.min.css" rel="stylesheet" />
<script src="https://cdn.jsdelivr.net/npm/vue@3/dist/vue.global.prod.js"></script>
<script src="https://cdn.jsdelivr.net/npm/vuetify@3.7.6/dist/vuetify.min.js"></script>
```

**Vuetify 4:**
```html
<link href="https://cdn.jsdelivr.net/npm/vuetify@4.0.6/dist/vuetify.min.css" rel="stylesheet" />
<script src="https://cdn.jsdelivr.net/npm/vue@3/dist/vue.global.prod.js"></script>
<script src="https://cdn.jsdelivr.net/npm/vuetify@4.0.6/dist/vuetify.min.js"></script>
```

**Important:** CDN bundles include all components - no tree shaking. For production optimization, use Vite with `vite-plugin-vuetify`.

---

## Recommendation

### Recommended: Vuetify 3 First

**Rationale:**

1. **Smaller Bundle:** ~844 KB vs ~1,016 KB (20% reduction)
2. **Mature Ecosystem:** More migration guides, Stack Overflow answers, examples
3. **Stability:** Battle-tested over 3+ years
4. **Incremental Path:** Can upgrade to Vuetify 4 later with fewer changes

### Migration Steps

1. **Phase 1:** Upgrade Vuetify 1.5 -> 2.x (staying on Vue 2)
2. **Phase 2:** Migrate Vue 2 -> Vue 3 + Vuetify 3
3. **Phase 3 (Optional):** Upgrade Vuetify 3 -> 4

### Alternative: Direct to Vuetify 4

If baseweb wants the latest features immediately:

- Same migration path required (no shortcut)
- More breaking changes to handle at once
- Bundle size similar to current Vuetify 1.5 (~1 MB)
- Benefits: MD3, CSS cascade layers, modern grid system

---

## Near-Miss Tier

The following alternatives were considered but not recommended:

### PrimeVue

- **Why it nearly made the cut:** Per-component CDN loading (smaller initial load), good Vue 3 support
- **Why it ranked below:** Complete component library change required, not just version upgrade
- **Best for:** Projects starting fresh or willing to rewrite all UI components

### Minimal Vite Build

- **Why it nearly made the cut:** Enables tree shaking, can reduce bundle size significantly
- **Why it ranked below:** Introduces build step, breaks baseweb's "drop-in" architecture
- **Best for:** Production deployments where bundle size is critical

---

## Conclusion

For baseweb's migration from Vuetify 1.5/Vue 2:

1. **Migrate to Vuetify 3 first** - smaller bundle, more resources, stable
2. **Use CDN approach** - maintains current architecture, bundle size comparable to current
3. **Consider Vuetify 4 later** - fewer changes (3 -> 4) than a complete migration

The CDN bundle sizes are similar to baseweb's current vuetify.js (~1 MB), so bundle size should not be the deciding factor. Focus on migration effort and stability instead.