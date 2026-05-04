# Vuetify Build Requirements Analysis

**Date:** 2026-05-04
**Context:** Evaluating Vuetify 3 compatibility with baseweb's no-build architecture

---

## Core Question

Can Vuetify 3 work with baseweb's current "drop-in" architecture (plain JS components, script tag loading, no build step)?

## Answer: Yes, With Trade-offs

Vuetify 3 **CAN** be used without a build system via CDN, but this approach has significant implications.

---

## Key Findings

### 1. CDN Installation Works
Vuetify 3 supports two CDN methods:
- **UMD (script tags)**: Load `vuetify.min.js` globally
- **ES Modules**: Use import maps with `vuetify.esm.js`

```html
<script src="https://cdn.jsdelivr.net/npm/vue@3/dist/vue.global.prod.js"></script>
<script src="https://cdn.jsdelivr.net/npm/vuetify@3/dist/vuetify.min.js"></script>
```

### 2. No Tree Shaking With CDN
- CDN loads **all 80+ components** regardless of usage
- Bundle size: **~500KB+** (full library)
- Tree shaking requires `vite-plugin-vuetify` or `webpack-plugin-vuetify`

### 3. Vuetify 1.5 + Vue 3 = Incompatible
- Vuetify 1.5 and 2.x are **not compatible** with Vue 3
- Vuetify 3 is the **only** version that works with Vue 3
- Complete rewrite required for migration

---

## Alternatives Evaluated

### PrimeVue (Better for No-Build)
- Per-component CDN loading
- Load only what you need
- Designed for "enhancing static HTML"
- Requires manual component registration

```html
<script src="unpkg.com/primevue/button/button.min.js"></script>
<script src="unpkg.com/primevue/datatable/datatable.min.js"></script>
```

### Minimal Vite Build
- Keep plain JS components (no SFCs needed)
- Use render functions or JSX
- Add `vite-plugin-vuetify` for tree shaking
- Preserves drop-in feel with build optimization

---

## Decision Matrix

| Option | Build Step | Bundle Size | Migration Effort | Preserves Architecture |
|--------|-----------|-------------|------------------|----------------------|
| Vuetify 3 CDN | No | Large (~500KB) | Medium | Yes |
| PrimeVue CDN | No | Small (per-component) | High | Mostly |
| Vite + Vuetify 3 | Yes | Optimized | High | Modified |

---

## Recommendation

For baseweb, the **Vuetify 3 CDN approach** is the path of least resistance if bundle size is acceptable. It preserves the drop-in architecture with minimal changes.

If bundle size is a concern, **PrimeVue** offers better no-build characteristics with per-component loading.

A **minimal Vite build** is worth considering for long-term maintainability, as it enables tree shaking while keeping the plain JS component style.

---

## Further Research

- [ ] Benchmark actual bundle sizes for typical baseweb pages
- [ ] Evaluate PrimeVue component coverage vs Vuetify
- [ ] Prototype minimal Vite config with baseweb structure

---

## Sources

Full research details: `/Users/xtof/Workspace/agentic/baseweb/research/2026-05-04-vuetify-build-requirements/`

Key sources:
- [Vuetify 3 Installation](https://v3.vuetifyjs.com/en/getting-started/installation/)
- [Vuetify Tree Shaking](https://vuetifyjs.com/en/guides/a-la-carte/)
- [PrimeVue CDN](https://v3.primevue.org/cdn/)
- [Vue 3 Tooling](https://vuejs.org/guide/scaling-up/tooling.html)