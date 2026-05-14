/**
 * HelloWorld Component
 *
 * A minimal Vuetify component demonstrating baseweb integration.
 * Uses the Page component wrapper and basic Vuetify components.
 */

var HelloWorld = {
  name: 'HelloWorld',
  navigation: {
    icon: "mdi-home",
    text: "Home",
    path: "/",
    index: 1
  },
  template: `
    <Page>
      <v-container fluid>
        <v-row justify="center">
          <v-col cols="12" sm="8" md="6">
            <v-card>
              <v-card-title class="text-h5">
                Hello World
              </v-card-title>
              <v-card-text>
                <p>Welcome to baseweb with Vue 3 + Vuetify 3!</p>
                <p>This is a minimal example application.</p>
                <v-btn color="primary" to="/about">About...</v-btn>
              </v-card-text>
            </v-card>
          </v-col>
        </v-row>
      </v-container>
    </Page>
  `
};

// Register component with app
app.component('HelloWorld', HelloWorld);

// Register with baseweb's Navigation system
// This adds it to both the navigation drawer and the router
Navigation.add(HelloWorld);
