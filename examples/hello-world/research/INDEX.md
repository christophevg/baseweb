# Research Index

### Vuetify 3 Material Icons Configuration

**Folder**: `2026-05-04-vuetify3-icons/`
**Date**: 2026-05-04
**Status**: Complete

**Summary**: Research on Vuetify 3 icon fonts configuration, including all valid icon font options, self-hosted Material Icons configuration, and icon rendering in components.

**Key Findings**:
- Material Design Icons (MDI) is the default icon set, not Google's Material Icons
- Self-hosted Google Material Icons use `material-design-icons-iconfont` package with `md` iconset
- SVG-based icons (`mdi-svg` + `@mdi/js`) are recommended for production for tree-shaking benefits
- Use `icon` prop instead of default slots in Vuetify 3 components
- Multiple icon sets can coexist using prefixes like `mdi:` or `fa:`

**Sources**: 2 sources (1 successful fetch)

**Keywords**: vuetify, icons, material-icons, mdi, configuration, self-hosted