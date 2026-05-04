# Vuetify Build Requirements

**Research Date:** 2026-05-04
**Purpose:** Determine if Vuetify 3 can work with baseweb's no-build architecture, or explore alternatives
**Previous Research:** none

---

## Executive Summary

Vuetify 3 CAN be used without a build system via CDN, but this approach has significant trade-offs. CDN usage loads the entire Vuetify library (~500KB+ minified) with no tree shaking. For baseweb's "drop-in" architecture, three viable paths exist: (1) Use Vuetify 3 via CDN accepting larger bundle size, (2) Switch to PrimeVue which offers better CDN support with per-component loading, or (3) Adopt a minimal Vite build process that preserves drop-in simplicity while enabling tree shaking. Vuetify 1.5 cannot be used with Vue 3.

---

## 1. Can Vuetify 3 Work Without a Build System?

### Key Findings

- Vuetify 3 fully supports CDN-based installation without any build tools [1]
- Two methods available: UMD (script tags) and ES Modules (import maps) [1]
- All 80+ components are loaded regardless of usage [2]
- No tree shaking possible without Vite/Webpack plugin [2]

### Details

**UMD Method (Script Tags):**
```html
<link href="https://cdn.jsdelivr.net/npm/vuetify@3/dist/vuetify.min.css" rel="stylesheet" />
<script src="https://cdn.jsdelivr.net/npm/vue@3/dist/vue.global.prod.js"></script>
<script src="https://cdn.jsdelivr.net/npm/vuetify@3/dist/vuetify.min.js"></script>
<script>
  const { createApp } = Vue
  const { createVuetify } = Vuetify
  const app = createApp()
  app.use(createVuetify()).mount('#app')
</script>
```

**ES Module Method (Import Maps):**
```html
<script type="importmap">
{
  "imports": {
    "vue": "https://cdn.jsdelivr.net/npm/vue@3/dist/vue.esm-browser.js",
    "vuetify": "https://cdn.jsdelivr.net/npm/vuetify@3/dist/vuetify.esm.js"
  }
}
</script>
<script type="module">
  import { createApp } from 'vue'
  import { createVuetify } from 'vuetify'
  // ...
</script>
```

**Important Caveat:** In-DOM templates may have parsing issues with certain HTML elements (tables, forms). Use `is="vue:v-table"` attribute syntax for affected elements [1].

**Sources:**
- [Get started with Vuetify 3](https://v3.vuetifyjs.com/en/getting-started/installation/)
- [Using vuetify in single .html page](https://stackoverflow.com/questions/77567419/using-vuetify-in-single-html-page)

---

## 2. Vuetify 1.5 + Vue 3 Compatibility

### Key Findings

- Vuetify 1.5 is NOT compatible with Vue 3 [3]
- Vuetify 2.x is also NOT compatible with Vue 3 [3]
- Vuetify 3 is the only version that works with Vue 3 [3]

### Details

Vuetify 1.5 and 2.x were built for Vue 2 and rely on Vue 2's template compiler and internal APIs that were completely changed in Vue 3. The GitHub issues show developers spending significant effort trying to make older Vuetify work with Vue 3, only to be told it's fundamentally incompatible.

**Migration Path (if needed):**
1. Upgrade to Vuetify 2.x first (while still on Vue 2)
2. Then migrate to Vue 3 + Vuetify 3

Both steps require significant code changes.

**Sources:**
- [How to use vuetify with vue 3.x?](https://github.com/vuetifyjs/vuetify-loader/issues/127)
- [Vuejs 3 support Feature Request](https://github.com/vuetifyjs/vuetify/issues/11162)

---

## 3. Alternative: PrimeVue for No-Build

### Key Findings

- PrimeVue supports per-component CDN loading [4]
- Only load components you actually use [4]
- Manual component registration required [4]
- Designed for "enhancing static HTML" [4]

### Details

PrimeVue offers more granular CDN loading than Vuetify:

```html
<script src="https://unpkg.com/vue@3/dist/vue.global.js"></script>
<script src="unpkg.com/primevue/core/core.min.js"></script>
<script src="unpkg.com/primevue/button/button.min.js"></script>
<script src="unpkg.com/primevue/datatable/datatable.min.js"></script>
```

Each component is a separate script, so you only load what you need. This is a significant advantage over Vuetify's all-or-nothing CDN approach.

**Configuration:**
```javascript
app.use(primevue.config.default);
app.component('p-button', primevue.button);
app.component('p-datatable', primevue.datatable);
```

**Sources:**
- [Install PrimeVue with CDN](https://v3.primevue.org/cdn/)

---

## 4. Minimal Build Process Option

### Key Findings

- Vue components can be written without SFCs (using render functions, JSX, or template strings) [5]
- Vite can build plain JS files without SFC transformation [5]
- vite-plugin-vuetify enables automatic tree shaking [6]
- Template strings require runtime compiler (+14kb) [5]

### Details

**Approach:** Keep baseweb's plain JS component files but add a minimal Vite build step:

```javascript
// vite.config.js
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import vuetify from 'vite-plugin-vuetify'

export default defineConfig({
  plugins: [
    vue(),
    vuetify(), // Auto tree-shaking
  ],
  build: {
    lib: {
      entry: 'src/components/index.js',
      formats: ['es', 'umd']
    }
  }
})
```

**Component Style (Render Functions - smallest bundle):**
```javascript
// MyComponent.js - no SFC needed
import { h, ref } from 'vue'
export default {
  setup() {
    const count = ref(0)
    return () => h('div', [/* ... */])
  }
}
```

**How vite-plugin-vuetify Works:**
- Automatically scans files for Vuetify component usage
- Only imports components actually used
- Uses package exports and sideEffects declaration for tree shaking [6]

**Sources:**
- [Tooling | Vue.js](https://vuejs.org/guide/scaling-up/tooling.html)
- [Treeshaking — Vuetify](https://vuetifyjs.com/en/guides/a-la-carte/)

---

## Comparison Table

| Approach | Build Required | Tree Shaking | Bundle Size | Drop-in Simplicity |
|----------|---------------|--------------|-------------|-------------------|
| Vuetify 3 CDN | No | No | Large (~500KB+) | Preserved |
| PrimeVue CDN | No | Per-component | Small (load only what you need) | Preserved (with manual registration) |
| Vite + Vuetify 3 | Yes | Yes | Optimized | Requires build step |
| Vuetify 1.5 + Vue 3 | N/A | N/A | Incompatible | N/A |

---

## Key Takeaways

1. **Vuetify 3 CAN work without a build system** via CDN, but loads entire library (~500KB+)
2. **Vuetify 1.5 CANNOT work with Vue 3** - fundamental incompatibility
3. **PrimeVue is better suited for no-build scenarios** with per-component CDN loading
4. **A minimal Vite build** could preserve drop-in simplicity while enabling tree shaking
5. **Tree shaking requires vite-plugin-vuetify** - not possible with CDN alone

---

## Recommendations for Baseweb

### Option A: Accept CDN Trade-offs (Simplest)
- Use Vuetify 3 via CDN
- Accept ~500KB+ library size
- Preserve current drop-in architecture
- No code changes needed beyond Vuetify 1.5 → 3 migration

### Option B: Switch to PrimeVue (Better Bundle)
- Migrate to PrimeVue
- Load only components used per-page
- Manual component registration required
- Better suited for no-build architecture

### Option C: Add Minimal Build (Best Bundle, Most Work)
- Add Vite build with vite-plugin-vuetify
- Keep plain JS components (no SFCs required)
- Use render functions or JSX (not template strings)
- Enables tree shaking while keeping component style

---

## Sources

[1] Get started with Vuetify 3 - https://v3.vuetifyjs.com/en/getting-started/installation/ - Accessed 2026-05-04

[2] Treeshaking — Vuetify - https://vuetifyjs.com/en/guides/a-la-carte/ - Accessed 2026-05-04

[3] How to use vuetify with vue 3.x? - https://github.com/vuetifyjs/vuetify-loader/issues/127 - Accessed 2026-05-04

[4] Install PrimeVue with CDN - https://v3.primevue.org/cdn/ - Accessed 2026-05-04

[5] Tooling | Vue.js - https://vuejs.org/guide/scaling-up/tooling.html - Accessed 2026-05-04

[6] vite-plugin-vuetify - https://registry.npmjs.org/vite-plugin-vuetify - Accessed 2026-05-04