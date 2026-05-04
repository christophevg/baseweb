# Vuetify v4.0.0 Release Notes

**URL**: https://github.com/vuetifyjs/vuetify/releases/tag/v4.0.0
**Fetched**: 2026-05-04T12:02:00Z

---

## Vuetify v4.0.0 Release Summary

### Breaking Changes from Vuetify 3

- **VSnackbar**: "`multi-line` prop" removed - "closes #15996"
- **VSelect/Autocomplete/Combobox**: "rename item to internalItem" - "closes #18354"
- **Theme**: "remove unimportant option"
- **VBtn**: "remove default text transform" and "convert display from grid to flex"
- **Default theme**: "change default theme to 'system'"

### New Features

- **MD3 typography and elevation levels** added
- **VSnackbarQueue**: new component to "show multiple snackbars"
- **VAvatar**: "`badge` prop + `dot-size` for VBadge" added
- **VInput**: "`indent-details` prop" added
- **VSelect/VAutocomplete/VCombobox**: "`menu-elevation` prop" added
- **Theme**: "support transparent colors"
- **VImg**: "pass attributes to the underlying `<img>`"

### Grid System Changes

- **Complete overhaul**: "grid system overhaul (#21500)" - "closes #8611"
- **VRow**: "smaller density steps"
- **VCol**: "syntax for overriding row size"
- **Breakpoints**: "reduce default breakpoint sizes (#19759)"

### CSS Changes

- **Layers**: "always use css layers" - "closes #3400, #20232"
- **!important**: "replace !important with layers"
- **Layer names**: "flatten layer names"
- **Entry points**: "add separate entry points"
- **Reset**: "cut down CSS reset" and "remove overflow-y from reset"

### Migration Resources

- **Documentation**: https://vuetifyjs.com/
- **Upgrade Guide**: https://vuetifyjs.com/en/getting-started/upgrade-guide