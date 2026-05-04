# Sources: Vuetify 3 Material Icons Configuration

**Date**: 2026-05-04T00:00:00Z
**Previous Research**: none

---

## Searches

<!-- Record each WebSearch immediately after performing it -->

### search-1

- **Query**: Vuetify 3 icon fonts configuration Material Icons 2026
- **Timestamp**: 2026-05-04T00:00:01Z
- **Results**:
  - [Icon Fonts — Vuetify](https://vuetifyjs.com/en/features/icon-fonts/?one=settings) - Main Vuetify icon fonts documentation
  - [Installing Icons — Vuetify.js](https://v15.vuetifyjs.com/en/framework/icons/) - Vuetify v15 icons (outdated)
  - [Font Icons | Vuetify Nuxt Module](https://nuxt.vuetifyjs.com/guide/features/icons/font-icons.html) - Nuxt-specific configuration
  - [GitHub Vuetify icon-fonts.md](https://github.com/vuetifyjs/vuetify/blob/36d3d3c9/packages/docs/src/pages/en/features/icon-fonts.md) - Source documentation
  - [Stack Overflow: How to import custom iconfont in Vuetify 3?](https://stackoverflow.com/questions/75544155/how-to-import-custom-iconfont-in-vuetify-3) - Community Q&A

### search-2

- **Query**: Vuetify 3 Material Icons vs Material Design Icons MDI difference self-hosted
- **Timestamp**: 2026-05-04T00:00:04Z
- **Results**:
  - [Icon System - Vuetify](https://www.mintlify.com/vuetifyjs/vuetify/concepts/icons) - Icon system concepts
  - [Installing Icons — Vuetify.js](https://v15.vuetifyjs.com/en/framework/icons/) - Vuetify v15 icons (outdated)
  - [Vuetify + Nuxt + locally add md icons](https://stackoverflow.com/questions/67808532/vuetify-nuxt-locally-add-md-icons) - Stack Overflow Q&A
  - [VIcon - Vuetify](https://vuetifyjs-vuetify.mintlify.app/components/icon) - VIcon component docs

## Fetches

<!-- Record each WebFetch immediately after performing it -->

### fetch-1

- **URL**: https://vuetifyjs.com/en/features/icon-fonts/
- **Timestamp**: 2026-05-04T00:00:02Z
- **Source**: search-1
- **Status**: Failed - JavaScript rendering required

### fetch-2

- **URL**: https://raw.githubusercontent.com/vuetifyjs/vuetify/master/packages/docs/src/pages/en/features/icon-fonts.md
- **Timestamp**: 2026-05-04T00:00:03Z
- **Source**: search-1
- **Title**: Icon Fonts Documentation (GitHub Raw)
- **Content**: [fetched/fetch-2.md](fetched/fetch-2.md)
- **Summary**: Complete documentation on all icon font options, configuration, and usage in Vuetify 3
- **Key Excerpts**:
  - "Material Design Icons (MDI) - default icon set"
  - "Material Icons - official Google icons"
  - Install command: `pnpm add material-design-icons-iconfont -D`
  - Configuration: `import { aliases, md } from 'vuetify/iconsets/md'`
  - "we recommend using the `icon` prop instead" of default slot

## Citations

<!-- Track citations used in report -->

## Excluded Findings

<!-- Record information found but excluded as incorrect/irrelevant -->

### Excluded: Vuetify v15 Icons Page

- **URL**: https://v15.vuetifyjs.com/en/framework/icons/
- **Found**: 2026-05-04T00:00:01Z
- **Reason**: Outdated documentation for older Vuetify version, not relevant to Vuetify 3