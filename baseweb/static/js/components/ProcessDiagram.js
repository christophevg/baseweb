Vue.component("ProcessStep", {
  template: `
    <li v-if="'title' in step">
      <div class="step">
        <div class="header">
          <h4>{{ step.title }}</h4>
        </div>
        <div v-if="step.html" class="body" v-html="step.html"></div>
        <div v-if="step.body" class="body">
          <component :is="step.body.component" v-bind="step.body.data"/>
        </div>
      </div>
    </li>
    <li v-else-if="'sequence' in step && child">
      <ol>
        <ProcessStep v-for="(childstep, i) in step.sequence" :step="childstep" :key="i" child="true"/>
      </ol>
    </li>
    <ol v-else-if="'sequence' in step && ! child" class="process_diagram">
      <ProcessStep v-for="(childstep, i) in step.sequence" :step="childstep" :key="i" child="true"/>
    </ol>
    <li v-else-if="'fanout' in step">
      <ul>
        <ProcessStep v-for="(childstep, i) in step.fanout" :step="childstep" :key="i" child="true"/>
      </ul>
    </li>
`,
  props: [ "step", "child" ]
});

Vue.component("ProcessDiagram", {
  template: `
  <v-card>
    <v-card-actions v-if="title">
      <h2>{{ title }}</h2>
    </v-card-actions>
    <v-card-text>
      <ProcessStep :step="diagram"/>
    </v-card-text>
  </v-card>
`,
  props: [ "title", "diagram" ]
});
