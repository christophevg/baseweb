var Page2 = {
  template : `
<div>
  <h1>Page 2</h1>
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
  { path: '/page2', component: Page2 },
])

app.sections.push({
  icon  : "home",
  text  : "Page2",
  path  : "/page2",
  index : 3
});
