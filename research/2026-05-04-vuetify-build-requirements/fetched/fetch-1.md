# PrimeVue CDN Usage Summary

**URL**: https://v3.primevue.org/cdn/
**Fetched**: 2026-05-04T00:06:00Z

---

## (1) Loading Individual Components

Load Vue, PrimeVue core, and individual component scripts via CDN:

```html
<script src="https://unpkg.com/vue@3/dist/vue.global.js"></script>
<script src="unpkg.com/primevue/core/core.min.js"></script>
<script src="unpkg.com/primevue/calendar/calendar.min.js"></script>
```

Include theme CSS separately:
```html
<link rel="stylesheet" href="unpkg.com/primevue/resources/themes/lara-light-green/theme.css" />
```

## (2) Bundle Size Implications

Not explicitly addressed in the documentation. The approach uses unpkg or similar providers (jsdelivr, cdnjs) to load resources on-demand.

## (3) Configuration and Usage

- Create app container and initialize with `createApp()`
- Install PrimeVue plugin: `app.use(primevue.config.default);`
- Register components manually: `app.component('p-datepicker', primevue.calendar);`
- Use components with `p-` prefix in templates: `<p-datepicker v-model="date"></p-datepicker>`

## (4) Limitations

The documentation states this approach "does not involve any build step, and is suitable for enhancing static HTML." No other limitations are specified compared to build-based installation.