# Fetch 2: Vuetify Icon Fonts Documentation (GitHub Raw Source)

**URL**: https://raw.githubusercontent.com/vuetifyjs/vuetify/master/packages/docs/src/pages/en/features/icon-fonts.md
**Timestamp**: 2026-05-04T00:00:03Z
**Source**: search-1
**Title**: Icon Fonts Documentation

## Content

Based on the documentation, Vuetify supports these icon libraries:
- **Material Design Icons (MDI)** - default icon set
- **Material Icons** - official Google icons
- **Font Awesome** (versions 4, 5, 6)
- **Phosphor**
- **Lucide**
- **Tabler**
- **Remix Icon**
- **BoxIcons**
- **Carbon**
- **Material Symbols**
- **UnoCSS icon sets** (via Iconify)

## Material Icons CSS Configuration (Non-CDN)

Install locally:
```bash
pnpm add material-design-icons-iconfont -D
```

Configure in Vuetify:
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

## Self-Hosted Material Design Icons (MDI)

For the extended Material Design Icons library (MDI), there are two approaches:

**MDI CSS (font-based):**
```bash
pnpm add @mdi/font -D
```
```js
import '@mdi/font/css/materialdesignicons.css'
import { createVuetify } from 'vuetify'

export default createVuetify({
  icons: {
    defaultSet: 'mdi',
  },
})
```

**MDI JS SVG (recommended for production):**
```bash
pnpm add @mdi/js -D
```
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

## Icon Rendering in Vuetify 3 Components

The documentation states: "we recommend using the `icon` prop instead" of the default slot.

**Basic usage:**
```html
<v-icon icon="mdi-home" />
```

**With alias references:**
```html
<v-icon icon="$account" />
```

**In component props:**
```html
<v-btn prepend-icon="$account">Custom Icon</v-btn>
<v-alert icon="i-solar:album-linear" title="Create new album" />
```

## Configuration Examples by Icon Set

**Font Awesome 5 CSS:**
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

**Font Awesome SVG:**
```js
import { aliases, fa } from 'vuetify/iconsets/fa-svg'
import { library } from '@fortawesome/fontawesome-svg-core'
import { FontAwesomeIcon } from '@fortawesome/vue-fontawesome'
import { fas } from '@fortawesome/free-solid-svg-icons'

app.component('font-awesome-icon', FontAwesomeIcon)
library.add(fas)
```

**Phosphor (via UnoCSS):**
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

**Multiple icon sets:**
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

## Custom Aliases

Custom aliases use `$` prefix and can reference icon names, Vue components, or SVG paths:

```js
export const customIcons = {
  mdiCustomAlias: 'mdi-tag',
  account: AccountIcon, // Vue component
  annotation: ['M14 9.45h-1...'], // SVG path
}
```