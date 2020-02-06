var Page1 = {
  template : `
<div>
  <h1>Page 1</h1>
</div>
`,
  computed: {},
  methods: {},
  data: function() {
    return {}
  }
};

// add route and navigation entry

router.addRoutes([
  { path: '/page1', component: Page1 },
])

app.sections.push({
  icon  : "home",
  text  : "Page1",
  path  : "/page1",
  index : 2
});
