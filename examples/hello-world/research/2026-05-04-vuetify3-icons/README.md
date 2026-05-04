# Vuetify 3 Material Icons Configuration

**Research Date:** 2026-05-04
**Purpose:** Research Vuetify 3 icon fonts configuration options, focusing on Material Icons self-hosting and icon rendering
**Previous Research:** none

---

## Executive Summary

Vuetify 3 supports multiple icon font libraries with Material Design Icons (MDI) as the default. For self-hosted Material Icons (Google's official icons), use the `material-design-icons-iconfont` package with the `md` iconset. For production applications, consider using SVG-based icons (`mdi-svg` or `@mdi/js`) for tree-shaking benefits. Icons are rendered using the `icon` prop on `v-icon` components or component props like `prepend-icon`.

---

## 1. Valid Icon Font Options

Vuetify 3 supports these icon libraries:

### Official Documentation List
- **Material Design Icons (MDI)** - Default icon set, third-party extended library
- **Material Icons** - Official Google icons
- **Font Awesome** (versions 4, 5, 6)
- **Phosphor**
- **Lucide**
- **Tabler**
- **Remix Icon**
- **BoxIcons**
- **Carbon**
- **Material Symbols**
- **UnoCSS icon sets** (via Iconify)

### Key Differences: Material Icons vs Material Design Icons

| Feature | Material Icons (`md`) | Material Design Icons (`mdi`) |
|---------|----------------------|------------------------------|
| **Source** | Google official | Community extended |
| **Icon count** | ~1,000 | ~7,000+ |
| **Bundle size** | ~80KB | ~330KB (CSS) / tree-shakable (SVG) |
| **Usage prefix** | None | `mdi-` |
| **Vuetify default** | No | Yes |

**Sources:**
- [Icon Fonts Documentation](https://raw.githubusercontent.com/vuetifyjs/vuetify/master/packages/docs/src/pages/en/features/icon-fonts.md) [1]

---

## 2. Self-Hosted Material Icons Configuration

### Material Icons (Google Official Icons)

**Installation:**
```bash
pnpm add material-design-icons-iconfont -D
```

**Configuration:**
```js
import 'material-design-icons-iconfont/dist/material-design-icons.css'
import { createVuetify } from 'vuetify'
import { aliases, md } from 'vuetify/iconsets/md'

export default createVuetify({
  icons: {
    defaultSet: 'md',
    aliases,
    sets: {
      md,
    },
  },
})
```

**Usage:**
```html
<v-icon icon="home" />
```

**Sources:**
- [Icon Fonts Documentation](https://raw.githubusercontent.com/vuetifyjs/vuetify/master/packages/docs/src/pages/en/features/icon-fonts.md) [1]

---

## 3. Self-Hosted Material Design Icons (MDI)

### Option A: CSS Font (Full Bundle)

**Installation:**
```bash
pnpm add @mdi/font -D
```

**Configuration:**
```js
import '@mdi/font/css/materialdesignicons.css'
import { createVuetify } from 'vuetify'
import { aliases, mdi } from 'vuetify/iconsets/mdi'

export default createVuetify({
  icons: {
    defaultSet: 'mdi',
    aliases,
    sets: { mdi },
  },
})
```

**Usage:**
```html
<v-icon icon="mdi-home" />
```

### Option B: SVG (Tree-Shakable - Recommended for Production)

**Installation:**
```bash
pnpm add @mdi/js -D
```

**Configuration:**
```js
import { createVuetify } from 'vuetify'
import { aliases, mdi } from 'vuetify/iconsets/mdi-svg'

export default createVuetify({
  icons: {
    defaultSet: 'mdi',
    aliases,
    sets: { mdi },
  },
})
```

**Benefits:**
- Only bundles icons you actually use
- No font loading delay
- Better performance
- Smaller bundle size

**Usage with specific icons:**
```html
<template>
  <v-icon :icon="mdiAccount" />
</template>

<script setup>
  import { mdiAccount } from '@mdi/js'
</script>
```

**Sources:**
- [Icon Fonts Documentation](https://raw.githubusercontent.com/vuetifyjs/vuetify/master/packages/docs/src/pages/en/features/icon-fonts.md) [1]

---

## 4. How Icons Are Rendered in Vuetify 3 Components

### Basic v-icon Usage

Vuetify 3 recommends using the `icon` prop instead of the default slot:

```html
<!-- Basic usage -->
<v-icon icon="mdi-home" />

<!-- With alias references -->
<v-icon icon="$account" />
```

### Component Props

Icons can be used in component props:

```html
<v-btn prepend-icon="$account">Custom Icon</v-btn>
<v-alert icon="i-solar:album-linear" title="Create new album" />
```

### Multiple Icon Sets

When using multiple icon sets, specify the set with a prefix:

```js
import { aliases, fa } from 'vuetify/iconsets/fa'
import { mdi } from 'vuetify/iconsets/mdi'

export default createVuetify({
  icons: {
    defaultSet: 'fa',
    aliases,
    sets: { fa, mdi },
  },
})
```

```html
<v-icon icon="fas fa-plus" />     <!-- FontAwesome -->
<v-icon icon="mdi:mdi-minus" />   <!-- MDI with prefix -->
```

### Custom Aliases

Custom aliases use `$` prefix and can reference icon names, Vue components, or SVG paths:

```js
export const customIcons = {
  mdiCustomAlias: 'mdi-tag',
  account: AccountIcon, // Vue component
  annotation: ['M14 9.45h-1...'], // SVG path
}
```

**Sources:**
- [Icon Fonts Documentation](https://raw.githubusercontent.com/vuetifyjs/vuetify/master/packages/docs/src/pages/en/features/icon-fonts.md) [1]

---

## 5. Other Icon Set Examples

### Font Awesome 5 CSS

```js
import '@fortawesome/fontawesome-free/css/all.css'
import { createVuetify } from 'vuetify'
import { aliases, fa } from 'vuetify/iconsets/fa'

export default createVuetify({
  icons: {
    defaultSet: 'fa',
    aliases,
    sets: { fa },
  },
})
```

### Font Awesome SVG

```js
import { aliases, fa } from 'vuetify/iconsets/fa-svg'
import { library } from '@fortawesome/fontawesome-svg-core'
import { FontAwesomeIcon } from '@fortawesome/vue-fontawesome'
import { fas } from '@fortawesome/free-solid-svg-icons'

app.component('font-awesome-icon', FontAwesomeIcon)
library.add(fas)
```

### Phosphor (via UnoCSS)

```js
import { aliases, ph } from 'vuetify/iconsets/ph'

export default createVuetify({
  icons: {
    defaultSet: 'ph',
    aliases,
    sets: { ph },
  },
})
```

**Sources:**
- [Icon Fonts Documentation](https://raw.githubusercontent.com/vuetifyjs/vuetify/master/packages/docs/src/pages/en/features/icon-fonts.md) [1]

---

## Key Takeaways

1. **Material Design Icons (MDI) is the default** in Vuetify 3, not Google's Material Icons
2. **For self-hosted Google Material Icons**, use `material-design-icons-iconfont` package with `vuetify/iconsets/md`
3. **For production apps**, consider SVG-based icons (`mdi-svg` or `@mdi/js`) for tree-shaking
4. **Use the `icon` prop** instead of default slots in Vuetify 3 components
5. **Multiple icon sets can coexist** using prefixes like `mdi:` or `fa:` to specify the icon set
6. **Custom aliases** use `$` prefix and can reference icon names, Vue components, or SVG paths

---

## Sources

[1] Icon Fonts Documentation - https://raw.githubusercontent.com/vuetifyjs/vuetify/master/packages/docs/src/pages/en/features/icon-fonts.md - Accessed 2026-05-04

---

## Files

- [SOURCES.md](SOURCES.md) - Complete source provenance
- [fetched/fetch-2.md](fetched/fetch-2.md) - Raw documentation content