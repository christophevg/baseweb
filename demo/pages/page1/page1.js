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

var groupSection = app.sections.find(function(item) {
  return "group" in item && item.group && item.text == "Index";
});
if(! groupSection ) {
  groupSection = {
    index      : 1,
    group      : true,
    icon       : "home",
    text       : "Index",
    subsections: []
  }
  app.sections.push(groupSection);
}

groupSection.subsections.push({
  icon  : "description",
  text  : "Page1",
  path  : "/page1",
  index : 2
});
