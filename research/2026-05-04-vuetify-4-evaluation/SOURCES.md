# Sources: Vuetify 4 Evaluation

**Date**: 2026-05-04T12:00:00Z
**Previous Research**: `2026-05-04-vuetify-build-requirements/`

---

## Searches

<!-- Record each WebSearch immediately after performing it -->

### search-1

- **Query**: Vuetify 4 released February 2026 major changes new features
- **Timestamp**: 2026-05-04T12:00:00Z
- **Results**:
  - [Vuetify 4 is Live Now | Medium](https://medium.com/@nakranirakesh/vuetify-4-is-live-now-45dce07fb95a) - Medium article on Vuetify 4 release
  - [v4.0.0 Release](https://github.com/vuetifyjs/vuetify/releases/tag/v4.0.0) - GitHub release notes
  - [Grid system overhaul commit](https://github.com/vuetifyjs/vuetify/commit/f6d24a923479300f55607b33f18114a5e9f724e1) - Grid changes details
  - [Bug Report](https://github.com/vuetifyjs/vuetify/issues/22656) - Bug report on Nuxt 4 compatibility
  - [v4.0.1 Release](https://github.com/vuetifyjs/vuetify/releases/tag/v4.0.1) - Patch release notes

**Key Finding**: Vuetify 4 released February 23, 2026. Major changes include Material Design 3, CSS cascade layers, grid system overhaul with CSS gap instead of negative margins, and system theme by default.

### search-2

- **Query**: Vuetify 4 CDN installation jsdelivr unpkg bundle size 2026
- **Timestamp**: 2026-05-04T12:03:00Z
- **Results**:
  - [Get started with Vuetify 4](https://v4.vuetifyjs.com/en/getting-started/installation/) - Official Vuetify 4 installation docs
  - [jsDelivr README](https://cdn.jsdelivr.net/npm/vuetify@4.0.3/README.md) - jsDelivr package info
  - [How to load vuetify/lib from CDN](https://stackoverflow.com/questions/79296239/how-to-load-vuetify-lib-from-cdn-to-achieve-minimal-sized-app) - SO on bundle size
  - [vuetify CDN by jsDelivr](https://cdn.jsdelivr.net/npm/vuetify@4.0.5/) - jsDelivr CDN listing
  - [UNPKG](https://app.unpkg.com/vuetify@4.0.3) - unpkg CDN listing

**Key Finding**: Vuetify 4 CDN available via jsDelivr and unpkg. CDN bundle includes all components (no tree shaking). Vue 3 required.

### search-3

- **Query**: Vuetify 1.5 to Vuetify 3 migration guide breaking changes component API differences
- **Timestamp**: 2026-05-04T12:04:00Z
- **Results**:
  - [August 2025 Update](https://vuetifyjs.com/en/blog/august-2025-update/) - Vuetify blog update
  - [Upgrade guide](https://vuetifyjs.com/getting-started/upgrade-guide/) - Official upgrade guide
  - [Exploring Vuetify 3](https://vuemastery.com/blog/exploring-vuetify-3) - Vue Mastery article
  - [Vuetify 3 Upgrade guide](https://v3.vuetifyjs.com/en/getting-started/upgrade-guide/) - Vuetify 3 upgrade docs
  - [Breaking changes PR](https://github.com/vuetifyjs/vuetify/pull/15485) - GitHub PR with breaking changes

**Key Finding**: No direct migration path from Vuetify 1.5 to Vuetify 3/4. Must migrate Vuetify 1.5 -> 2 -> 3 -> 4. Major API changes include `value` -> `model-value`, `background-color` -> `bg-color`, component renames, and slot changes.

### search-4

- **Query**: Vuetify 3 vs Vuetify 4 bundle size comparison minified gzipped 2026
- **Timestamp**: 2026-05-04T12:06:00Z
- **Results**:
  - [Vuetify 3 lib bundle size discussion](https://github.com/vuetifyjs/vuetify/discussions/17843) - GitHub discussion on bundle size
  - [Reduce bundle size](https://stackoverflow.com/questions/76138551/reduce-bundle-size-of-vue-and-vuetify-lib) - SO on reducing bundle size
  - [VTimePickerControls.css bug](https://github.com/vuetifyjs/vuetify/issues/22733) - Bundle size regression bug in Vuetify 4
  - [How to reduce vue js build size](https://stackoverflow.com/questions/61434797/how-to-reduce-vue-js-build-size-with-vuetify) - SO on build size
  - [npm trends comparison](https://npmtrends.com/@ionic/vue-vs-@vuetify/nightly-vs-bootstrap-vue-3-vs-naive-ui-vs-primevue-vs-quasar-framework) - Package comparison

**Key Finding**: Vuetify 3 ~300KB minified, ~245KB gzipped. Vuetify 4 had a CSS bundle size regression bug (246KB utilities in VTimePickerControls.css) that was fixed. CDN bundle includes all components (no tree shaking).

## Fetches

<!-- Record each WebFetch immediately after performing it -->

### fetch-1

- **URL**: https://github.com/vuetifyjs/vuetify/releases/tag/v4.0.0
- **Timestamp**: 2026-05-04T12:02:00Z
- **Source**: search-1
- **Title**: Vuetify v4.0.0 Release Notes
- **Content**: [fetched/fetch-1.md](fetched/fetch-1.md)
- **Summary**: GitHub release notes for Vuetify 4.0.0. Breaking changes include VSnackbar multi-line removal, VSelect/Autocomplete/Combobox slot rename (item -> internalItem), VBtn grid to flex change. Grid system overhaul with smaller density steps and new VCol syntax. CSS cascade layers replace !important.
- **Key Excerpts**:
  - "grid system overhaul (#21500)"
  - "always use css layers"
  - "rename item to internalItem"
  - "change default theme to 'system'"

### fetch-2

- **URL**: https://medium.com/@nakranirakesh/vuetify-4-is-live-now-45dce07fb95a
- **Timestamp**: 2026-05-04T12:05:00Z
- **Source**: search-1
- **Title**: Vuetify 4 is Live Now
- **Content**: [fetched/fetch-2.md](fetched/fetch-2.md)
- **Summary**: Medium article covering Vuetify 4 release. Key changes: Material Design 3 integration, CSS cascade layers (5 layers), elevation reduced to 6 levels, breakpoints adjusted (md 840px, xl 1545px), VBtn/VField reverted to Flexbox, system theme by default, dynamic color support.
- **Key Excerpts**:
  - "Elevation system reduced from 25 levels to 6 distinct levels (0–5)"
  - "five top-level layers (vuetify-core, vuetify-components, vuetify-utilities, etc.)"
  - "Core components like VBtn and VField have reverted from CSS Grid back to Flexbox"

### fetch-3

- **URL**: https://cdn.jsdelivr.net/npm/vuetify@4.0.6/dist/
- **Timestamp**: 2026-05-04T12:07:00Z
- **Source**: search-2
- **Title**: Vuetify 4.0.6 CDN Bundle Sizes
- **Content**: [fetched/fetch-3.md](fetched/fetch-3.md)
- **Summary**: Vuetify 4 CDN bundle sizes: vuetify.min.js 556.39 KB, vuetify.min.css 459.86 KB. Total ~1,016 KB minified.
- **Key Excerpts**:
  - "vuetify.min.js: 556.39 KB"
  - "vuetify.min.css: 459.86 KB"

### fetch-4

- **URL**: https://cdn.jsdelivr.net/npm/vuetify@3.7.6/dist/
- **Timestamp**: 2026-05-04T12:07:00Z
- **Source**: search-2
- **Title**: Vuetify 3.7.6 CDN Bundle Sizes
- **Content**: [fetched/fetch-4.md](fetched/fetch-4.md)
- **Summary**: Vuetify 3 CDN bundle sizes: vuetify.min.js 410.68 KB, vuetify.min.css 433.7 KB. Total ~844 KB minified.
- **Key Excerpts**:
  - "vuetify.min.js: 410.68 KB"
  - "vuetify.min.css: 433.7 KB"

## Citations

<!-- Track citations used in report -->

## Excluded Findings

<!-- Record information found but excluded as incorrect/irrelevant -->