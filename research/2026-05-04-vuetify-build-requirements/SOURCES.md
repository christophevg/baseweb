# Sources: Vuetify Build Requirements

**Date**: 2026-05-04T00:00:00Z
**Previous Research**: none

---

## Searches

<!-- Record each WebSearch immediately after performing it -->

### search-1

- **Query**: Vuetify 3 without build system CDN standalone browser
- **Timestamp**: 2026-05-04T00:01:00Z
- **Results**:
  - [Get started with Vuetify 3](https://v3.vuetifyjs.com/en/getting-started/installation/) - Official Vuetify 3 installation docs
  - [Is there a way to use Vuetify directly without a CDN?](https://stackoverflow.com/questions/50633036/is-there-a-way-to-use-vuetify-directly-without-a-cdn) - Stack Overflow discussion
  - [How can I avoid bundling Vuetify and use from CDN?](https://stackoverflow.com/questions/67995021/how-can-i-avoid-bundling-vuetify-and-use-from-cdn) - SO on CDN usage
  - [Vuetify instance with cdn not work on vuejs3](https://stackoverflow.com/questions/74911322/vuetify-instance-with-cdn-not-work-on-vuejs3) - SO troubleshooting
  - [Using vuetify in single .html page](https://stackoverflow.com/questions/77567419/using-vuetify-in-single-html-page) - SO on single HTML page usage

**Key Finding**: Vuetify 3 CAN be used without a build system via CDN. Two methods: traditional script tags (UMD) and ES modules with import maps.

### search-2

- **Query**: Vuetify 3 CDN installation limitations tree shaking components available
- **Timestamp**: 2026-05-04T00:02:00Z
- **Results**:
  - [Get started with Vuetify 3](https://v3.vuetifyjs.com/en/getting-started/installation/) - Official docs
  - [Treeshaking](https://vuetifyjs.com/en/guides/a-la-carte/) - Vuetify tree shaking docs
  - [How to load vuetify/lib from CDN to achieve minimal sized app](https://stackoverflow.com/questions/79296239/how-to-load-vuetify-lib-from-cdn-to-achieve-minimal-sized-app) - SO on minimal bundle size
  - [Vuetify instance with cdn not work on vuejs3](https://stackoverflow.com/questions/74911322/vuetify-instance-with-cdn-not-work-on-vuejs3) - SO troubleshooting
  - [Get started with Vuetify 3](https://vuetifyjs.cn/en/getting-started/installation) - Mirror site

**Key Finding**: CDN loads ALL components (no tree shaking). Tree shaking requires Vite/Webpack plugin. CDN bundle is full library, larger than optimized builds.

### search-3

- **Query**: Vue 3 UI framework no build system CDN standalone without bundler
- **Timestamp**: 2026-05-04T00:03:00Z
- **Results**:
  - [Install PrimeVue with CDN](https://v3.primevue.org/cdn/) - PrimeVue CDN installation docs
  - [Installation | Vue.js](https://vueframework.com/guide/installation.html) - Vue installation guide
  - [I want to use Vue 3 without build and without CDN](https://stackoverflow.com/questions/67685823/i-want-to-use-vue-3-without-build-and-without-cdn) - SO on no-build setup
  - [Setup - PrimeVue](https://v3.primevue.org/setup) - PrimeVue setup docs
  - [Vue 3 Local Run: No Build Tools, No CDN](https://openillumi.com/en/en-vue3-no-build-no-cdn-local-setup/) - Guide for offline setup

**Key Finding**: PrimeVue is the most CDN-friendly Vue 3 UI framework with per-component script loading. Vue 3 global build can also be downloaded for offline/no-build use.

### search-4

- **Query**: Vuetify 1.5 Vue 3 compatibility incompatibility
- **Timestamp**: 2026-05-04T00:04:00Z
- **Results**:
  - [How to use vuetify with vue 3.x?](https://github.com/vuetifyjs/vuetify-loader/issues/127) - GitHub issue on compatibility
  - [Vuejs 3 support Feature Request](https://github.com/vuetifyjs/vuetify/issues/11162) - GitHub issue tracking Vue 3 support
  - [August 2025 Update](https://vuetifyjs.com/en/blog/august-2025-update/) - Vuetify blog update
  - [Vuetify 3 with Vue 3 not working well](https://stackoverflow.com/questions/78627461/im-trying-to-use-vuetify-3-with-vue-3-and-its-not-working-very-well) - SO troubleshooting
  - [how to install vuetify 2.5.6 with vue 3?](https://stackoverflow.com/questions/68224962/how-to-install-vuetify-2-5-6-with-vue-3) - SO on Vue 3 incompatibility

**Key Finding**: Vuetify 1.5 and 2.x are NOT compatible with Vue 3. Vuetify 3 is the only version that works with Vue 3, requiring a complete rewrite.

### search-5

- **Query**: Vite simple build process Vue components without SFC single file components
- **Timestamp**: 2026-05-04T00:05:00Z
- **Results**:
  - [Build Options | Vite](https://v4.vitejs.dev/config/build-options) - Vite build docs
  - [Tooling | Vue.js](https://vuejs.org/guide/scaling-up/tooling.html) - Vue tooling guide
  - [Making and publishing components with Vue 3 and Vite](https://www.matijanovosel.com/blog/making-and-publishing-components-with-vue-3-and-vite) - Blog on component publishing
  - [Build Vue 3 plugin usable without build process](https://stackoverflow.com/questions/75375213/how-can-i-use-vite-to-build-my-vue-3-plugin-so-that-its-usable-without-a-build) - SO on no-build output
  - [Vite config for individual Vue components](https://stackoverflow.com/questions/78313899/recommended-vite-config-js-for-compilation-of-individual-vue-components) - SO on component compilation

**Key Finding**: Vue components can be written without SFCs using render functions, JSX, or template strings. Vite can build these without special config. Template strings require runtime compiler (+14kb).

### search-6

- **Query**: "vite-plugin-vuetify" tree shaking how it works bundle size
- **Timestamp**: 2026-05-04T00:07:00Z
- **Results**:
  - [Treeshaking — Vuetify](https://vuetifyjs.com/en/guides/a-la-carte/) - Official tree shaking docs
  - [vite-plugin-vuetify](https://registry.npmjs.org/vite-plugin-vuetify) - NPM package
  - [Reduce bundle size](https://stackoverflow.com/questions/76138551/reduce-bundle-size-of-vue-and-vuetify-lib) - SO on bundle size
  - [Tree-shaking - Vuetify](https://vuetifyjs-vuetify.mintlify.app/advanced/treeshaking) - Alternative docs
  - [Vuetify with Laravel/Vite](https://stackoverflow.com/questions/76650137/vuetify-how-to-import-only-needed-components-in-vuetify-when-using-laravel-v) - SO on component imports

**Key Finding**: vite-plugin-vuetify auto-scans for component usage and only includes what's used. Uses package exports and sideEffects declaration in package.json for tree shaking.

## Fetches

<!-- Record each Web WebFetch immediately after performing it -->

### fetch-1

- **URL**: https://v3.primevue.org/cdn/
- **Timestamp**: 2026-05-04T00:06:00Z
- **Source**: search-3
- **Title**: Install PrimeVue with CDN
- **Content**: [fetched/fetch-1.md](fetched/fetch-1.md)
- **Summary**: PrimeVue supports CDN usage with per-component loading. No build step required. Manual component registration needed.
- **Key Excerpts**:
  - "does not involve any build step, and is suitable for enhancing static HTML"
  - Load individual component scripts: `unpkg.com/primevue/calendar/calendar.min.js`
  - Register components manually: `app.component('p-datepicker', primevue.calendar);`

## Citations

<!-- Track citations used in report -->

## Excluded Findings

<!-- Record information found but excluded as incorrect/irrelevant -->