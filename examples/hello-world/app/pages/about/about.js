/**
 * About Component
 *
 * A second page to demonstrate routing in baseweb with Vue + Vuetify.
 */

var About = {
  name: 'About',
  navigation: {
    icon: "mdi-information",
    text: "About",
    path: "/about",
    index: 2
  },
  template: `
    <Page>
      <v-container fluid>
        <v-row justify="center">
          <v-col cols="12" sm="8" md="6">
            <v-card>
              <v-card-title class="text-h5">
                About
              </v-card-title>
              <v-card-text>
                <p>This is the About page.</p>
                <p>It demonstrates routing between pages in baseweb.</p>
                <v-btn color="primary" to="/">Go to Home</v-btn>
              </v-card-text>
            </v-card>
          </v-col>
        </v-row>
      </v-container>
    </Page>
  `
};

// Register component with app
app.component('About', About);

// Register with baseweb's Navigation system
Navigation.add(About);
