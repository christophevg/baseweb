# Functional Analysis: Hello World Example Application

**Created:** 2026-05-04
**Status:** Draft
**Task:** task-5.1

---

## Overview

This document defines the functional requirements for a minimal "Hello World" example application to be created in `examples/hello-world/` within the baseweb repository. The goal is to validate the core baseweb setup after the Vue 3 + Vuetify 3 migration was marked complete (task-3.12).

## Background

The Vue 3 + Vuetify 3 migration in baseweb is marked complete, but migration attempts for baseweb-demo encountered fundamental problems. Before investing more effort in migrating complex applications, we need a minimal working example to validate that:

1. The baseweb library can be imported and instantiated correctly
2. A minimal Quart app with baseweb starts without errors
3. The Vue 3 + Vuetify 3 frontend renders a simple page

This minimal example serves as a "canary" to detect configuration or compatibility issues early.

## Scope

### In Scope

- Minimal Quart application using baseweb
- Single page application with Vue 3 + Vuetify 3
- Basic routing (/ route only)
- Validation of core functionality

### Out of Scope

- Authentication/authorization
- REST API endpoints
- WebSocket/Socket.IO functionality
- Database integration
- Multiple pages or navigation
- PWA features
- Complex Vue components

## Architecture

### Directory Structure

```
examples/
  hello-world/
    app.py              # Main application entry point
    requirements.txt    # Dependencies (for pip install)
    README.md           # Run instructions
    static/
      js/
        HelloWorld.js   # Simple Vue component
```

### Components

#### Backend (app.py)

The backend is a minimal Quart application that:
- Imports and instantiates the Baseweb class
- Registers a single Vue component (HelloWorld.js)
- Runs with an ASGI server (uvicorn/hypercorn)

```python
from baseweb import Baseweb

app = Baseweb(__name__)

# ASGI entry point for running with uvicorn/gunicorn
asgi_app = app._asgi_app
```

#### Frontend (HelloWorld.js)

A minimal Vue 3 component that displays a greeting:

```javascript
Vue.component('HelloWorld', {
  template: `
    <Page>
      <v-container>
        <v-card>
          <v-card-title>Hello World</v-card-title>
          <v-card-text>
            Welcome to baseweb with Vue 3 + Vuetify 3!
          </v-card-text>
        </v-card>
      </v-container>
    </Page>
  `
});
```

## Functional Requirements

### FR-1: Application Startup

**Requirement:** The application must start without errors when invoked with an ASGI server.

**Acceptance Criteria:**
- [ ] `gunicorn -w 1 -k uvicorn.workers.UvicornWorker "app:asgi_app"` starts successfully
- [ ] Or `uvicorn app:asgi_app` starts successfully
- [ ] No Python exceptions in startup logs
- [ ] baseweb banner appears in console output

### FR-2: Route Handling

**Requirement:** The root route (/) must return a valid HTML response.

**Acceptance Criteria:**
- [ ] HTTP GET to `/` returns status 200
- [ ] Response contains valid HTML with Vue 3 initialization
- [ ] Response includes Vuetify 3 CSS and JS references

### FR-3: Static File Serving

**Requirement:** baseweb static files must be served correctly.

**Acceptance Criteria:**
- [ ] `/static/vendor/js/vue.js` returns Vue 3 JavaScript
- [ ] `/static/vendor/js/vuetify.js` returns Vuetify 3 JavaScript
- [ ] `/static/vendor/css/vuetify.min.css` returns Vuetify 3 CSS
- [ ] `/static/js/app.js` returns app initialization script
- [ ] `/app/HelloWorld.js` returns the registered component

### FR-4: Vue 3 Application Initialization

**Requirement:** The Vue 3 application must initialize and mount without errors.

**Acceptance Criteria:**
- [ ] Browser console shows "Vue 3 app mounted successfully"
- [ ] No JavaScript errors in browser console
- [ ] Vue DevTools shows the Vue 3 application structure

### FR-5: Vuetify 3 Rendering

**Requirement:** Vuetify 3 components must render correctly.

**Acceptance Criteria:**
- [ ] The HelloWorld component renders inside a v-card
- [ ] v-container, v-card, v-card-title, v-card-text render properly
- [ ] Vuetify styling is applied (material design appearance)
- [ ] No Vuetify-related console warnings

### FR-6: Page Component Integration

**Requirement:** The baseweb Page component must render as the outer container.

**Acceptance Criteria:**
- [ ] Page component wraps the content
- [ ] v-toolbar appears at top with app title
- [ ] NavigationDrawer component exists (even if not used)

### FR-7: Component Registration

**Requirement:** Custom Vue components registered with baseweb must be available.

**Acceptance Criteria:**
- [ ] HelloWorld.js is registered via `app.register_component()`
- [ ] Component appears in Vue DevTools component tree
- [ ] Component template renders correctly

## Non-Functional Requirements

### NFR-1: Minimal Dependencies

**Requirement:** The example should have minimal external dependencies.

**Acceptance Criteria:**
- [ ] requirements.txt contains only: baseweb, gunicorn, uvicorn
- [ ] No database, cache, or other service dependencies

### NFR-2: Clear Documentation

**Requirement:** Running the example must be documented clearly.

**Acceptance Criteria:**
- [ ] README.md contains setup instructions
- [ ] README.md contains run commands
- [ ] README.md contains expected output
- [ ] README.md contains validation steps

### NFR-3: Fast Startup

**Requirement:** The application should start quickly (< 5 seconds).

**Acceptance Criteria:**
- [ ] Server starts within 5 seconds on modern hardware
- [ ] Page loads within 2 seconds after server start

## Test Scenarios

### TS-1: Cold Start

1. Install dependencies: `pip install -e . && pip install gunicorn uvicorn`
2. Start server: `gunicorn -w 1 -k uvicorn.workers.UvicornWorker "app:asgi_app"`
3. Open browser: `http://localhost:8000`
4. Verify: Page renders with "Hello World" title

### TS-2: Component Registration

1. Start server
2. Open browser with DevTools
3. Verify: Console shows "Registering components: ['HelloWorld']"
4. Verify: Console shows "Registered: HelloWorld"

### TS-3: Vue 3 Compatibility

1. Start server
2. Open browser
3. Open Vue DevTools
4. Verify: App structure shows Vue 3 composition
5. Verify: Vuetify plugin is installed

## Files to Create

| File | Purpose |
|------|---------|
| `examples/hello-world/app.py` | Main application entry point |
| `examples/hello-world/requirements.txt` | Python dependencies |
| `examples/hello-world/README.md` | Documentation and run instructions |
| `examples/hello-world/static/js/HelloWorld.js` | Vue 3 component |

## Implementation Notes

### Backend Implementation

```python
# examples/hello-world/app.py
from pathlib import Path
from baseweb import Baseweb

# Create baseweb app
app = Baseweb(__name__)

# Configure paths
app.app_static_folder = Path(__file__).parent / "static"

# Register the HelloWorld component
app.register_component(
  filename="HelloWorld.js",
  path=Path(__file__).parent / "static" / "js"
)

# Register the root route to show HelloWorld
app.register_app_route("/", endpoint="home")

# ASGI entry point
asgi_app = app._asgi_app
```

### Frontend Implementation

```javascript
// examples/hello-world/static/js/HelloWorld.js
Vue.component('HelloWorld', {
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
              </v-card-text>
            </v-card>
          </v-col>
        </v-row>
      </v-container>
    </Page>
  `
});
```

### Router Configuration

The router must include a route for the HelloWorld component:

```javascript
// The default route configuration in baseweb already handles '/'
// We just need to ensure the HelloWorld component is registered
const routes = [
  { path: '/', component: { template: '<HelloWorld></HelloWorld>' } }
];
```

Note: The actual router configuration is handled by baseweb's core. The example only needs to register the component and route.

## Dependencies

### Python Dependencies

```
baseweb>=0.4.3
gunicorn>=21.0.0
uvicorn>=0.24.0
```

### Frontend Dependencies (via baseweb)

- Vue 3.x (provided by baseweb)
- Vuetify 3.x (provided by baseweb)
- Vuex 4.x (provided by baseweb)
- Vue Router 4.x (provided by baseweb)

## Success Criteria

The task is complete when:

1. **Server starts successfully**: `gunicorn -k uvicorn.workers.UvicornWorker "app:asgi_app"` runs without errors
2. **Page renders**: Opening `http://localhost:8000` shows a styled page with "Hello World"
3. **No console errors**: Browser console shows no JavaScript errors
4. **Vue 3 confirmed**: Console shows "Vue 3 app mounted successfully"
5. **Components registered**: Console shows component registration messages
6. **Documentation complete**: README.md explains how to run the example

## Risk Assessment

| Risk | Impact | Likelihood | Mitigation |
|------|--------|------------|------------|
| Vue 3 compatibility issues | High | Medium | Minimal component scope, use baseweb's Page |
| Import path issues | Medium | Low | Use relative imports from example directory |
| ASGI server configuration | Medium | Low | Document both gunicorn and uvicorn options |
| Static file path resolution | Medium | Medium | Use explicit Path() configuration |

## Related Tasks

- **task-3.12**: Vue 3 + Vuetify 3 Migration - Complete (prerequisite)
- **task-5.2**: Unify special page components - Future

## Validation Checklist

After implementation, validate:

- [ ] `pip install -e .` from baseweb root succeeds
- [ ] `cd examples/hello-world && pip install -r requirements.txt` succeeds
- [ ] Server starts with gunicorn
- [ ] Server starts with uvicorn
- [ ] Browser shows Hello World page
- [ ] Browser console shows "Vue 3 app mounted successfully"
- [ ] Browser console shows component registration
- [ ] No JavaScript errors in browser console
- [ ] Page styling uses Vuetify (material design)
- [ ] v-toolbar shows app name
- [ ] NavigationDrawer exists (may be hidden)

---

## Appendix: Expected Console Output

### Server Startup

```
 _                   _
| |__   __ _ _ __ __| |
| '_ \ / _` | '__/ _` |
| |_) | (_| | |  | (_| |
|_.__/ \__,_|_|   \__,_|
baseweb 0.4.3
[INFO] Starting gunicorn 21.2.0
[INFO] Listening at: http://127.0.0.1:8000
[INFO] Using worker: uvicorn.workers.UvicornWorker
```

### Browser Console

```
Queueing component: HelloWorld
Registering components: ['HelloWorld']
Registered: HelloWorld
Vue 3 app mounted successfully
```