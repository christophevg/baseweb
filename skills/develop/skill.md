---
name: baseweb-develop
description: Create and maintain baseweb applications (backend + frontend)
triggers:
  - when creating code in baseweb applications
  - when adding pages or components
  - when creating API endpoints
  - when adding Socket.IO handlers
  - when debugging baseweb apps
---

# Baseweb Develop Skill

Comprehensive skill for developing baseweb applications with async Quart backend and Vue/Vuetify frontend.

## Overview

This skill supports:

| Task | Description |
|------|-------------|
| Page Development | Create pages with Vue components and backend handlers |
| API Development | Create RESTful endpoints with Resource classes |
| WebSocket Development | Add Socket.IO event handlers |
| Component Development | Create reusable Vue components |
| Debugging | Diagnose and fix issues |

## When to Use

- Creating new pages in a baseweb app
- Adding API endpoints
- Adding Socket.IO handlers
- Creating Vue components
- Debugging baseweb applications

## Project Structure

Standard baseweb application structure:

```
myapp/
├── app/
│   ├── __init__.py          # Main entry point, server config
│   ├── pages/               # Page modules
│   │   └── mypage/
│   │       ├── __init__.py  # Backend handlers
│   │       └── mypage.js    # Vue component
│   ├── components/          # Shared Vue components
│   └── static/              # Static assets
├── tests/
├── pyproject.toml
└── Makefile
```

## Backend Development

### Creating a Page

**Backend (`app/pages/mypage/__init__.py`):**

```python
import logging
import os

from baseweb import Resource, server
from quart import request

logger = logging.getLogger(__name__)

# Register Vue component with route
HERE = os.path.dirname(__file__)
server.register_component("mypage.js", HERE, route="/mypage")

# REST API endpoint
class MyResource(Resource):
    @server.authenticated("app.mypage.get")
    async def get(self):
        return {"data": "value"}

    @server.authenticated("app.mypage.post")
    async def post(self):
        data = await request.get_json()
        return {"received": data}, 201

server.add_resource(MyResource, "/api/mypage")

# Socket.IO handler
@server.socketio.on("my_event")
@server.authenticated("app.mypage.my_event")
async def on_my_event(sid, data):
    logger.info(f"Received: {data} from {sid}")
    await server.socketio.emit("response", {"echo": data})
    return {"status": "ok"}
```

### Creating an API Endpoint

**Simple Resource:**

```python
from baseweb import Resource, server
from quart import request

class Users(Resource):
    async def get(self):
        # Return list of users
        return {"users": []}

    async def post(self):
        # Create new user
        data = await request.get_json()
        return {"id": 1, **data}, 201

class User(Resource):
    async def get(self, user_id):
        # Get single user
        return {"id": user_id, "name": "User"}

    async def put(self, user_id):
        # Update user
        data = await request.get_json()
        return {"id": user_id, **data}

    async def delete(self, user_id):
        # Delete user
        return "", 204

server.add_resource(Users, "/api/users")
server.add_resource(User, "/api/users/<int:user_id>")
```

**Stateful Resource (with dependencies):**

```python
class DatabaseResource(Resource):
    async def get(self):
        # Access injected dependency
        return {"data": self.db.query()}

# Create instance with dependencies
resource = DatabaseResource()
resource.db = my_database
server.add_resource(resource, "/api/data")
```

### Adding Socket.IO Handlers

```python
@server.socketio.on("connect")
async def on_connect(sid, environ):
    logger.info(f"Client connected: {sid}")
    await server.socketio.emit("welcome", {"message": "Hello"})

@server.socketio.on("disconnect")
async def on_disconnect(sid):
    logger.info(f"Client disconnected: {sid}")

@server.socketio.on("message")
async def on_message(sid, data):
    # Echo back to sender
    return {"echo": data}

@server.socketio.on("broadcast")
async def on_broadcast(sid, data):
    # Broadcast to all clients
    await server.socketio.emit("broadcast", data)

@server.socketio.on("room_message")
async def on_room_message(sid, data):
    # Send to specific room
    await server.socketio.emit("room_message", data, to=data["room"])
```

### Authentication

```python
# HTTP handlers
@server.authenticated("app.resource.get")
async def get(self):
    return {"protected": "data"}

# Socket.IO handlers
@server.socketio.on("private_event")
@server.authenticated("app.events.private")
async def handle_private(sid, data):
    return {"protected": True}
```

## Frontend Development

### Creating a Vue Component

**Basic Page Component:**

```javascript
// mypage.js
var MyPage = {
  template: `
<div>
  <h1>My Page</h1>
  <p>{{ message }}</p>
  <v-btn @click="doSomething" color="primary">Click Me</v-btn>
</div>
  `,
  navigation: {
    section: "main",
    icon: "star",
    text: "My Page",
    path: "/mypage",
    index: 10
  },
  data: function() {
    return {
      message: "Hello from MyPage"
    };
  },
  methods: {
    doSomething: function() {
      this.message = "Button clicked!";
    }
  }
};

Navigation.add(MyPage);
```

**Page with API Integration:**

```javascript
var UsersPage = {
  template: `
<div>
  <h1>Users</h1>
  <v-data-table :headers="headers" :items="users" :loading="loading">
    <template v-slot:item.actions="{ item }">
      <v-btn icon @click="editUser(item)"><v-icon>edit</v-icon></v-btn>
      <v-btn icon @click="deleteUser(item)"><v-icon>delete</v-icon></v-btn>
    </template>
  </v-data-table>
</div>
  `,
  navigation: {
    section: "admin",
    icon: "people",
    text: "Users",
    path: "/admin/users",
    index: 20
  },
  data: function() {
    return {
      headers: [
        { text: "ID", value: "id" },
        { text: "Name", value: "name" },
        { text: "Actions", value: "actions", sortable: false }
      ],
      users: [],
      loading: false
    };
  },
  mounted: function() {
    this.loadUsers();
  },
  methods: {
    loadUsers: function() {
      this.loading = true;
      $.ajax({
        url: "/api/users",
        success: (response) => {
          this.users = response.users;
          this.loading = false;
        },
        error: () => {
          this.loading = false;
        }
      });
    },
    editUser: function(user) {
      // Edit logic
    },
    deleteUser: function(user) {
      $.ajax({
        url: `/api/users/${user.id}`,
        type: "DELETE",
        success: () => {
          this.loadUsers();
        }
      });
    }
  }
};

Navigation.add(UsersPage);
```

**Page with Socket.IO:**

```javascript
var LivePage = {
  template: `
<div>
  <h1>Live Data</h1>
  <v-list>
    <v-list-item v-for="(msg, i) in messages" :key="i">
      <v-list-item-content>{{ msg }}</v-list-item-content>
    </v-list-item>
  </v-list>
  <v-text-field v-model="input" @keyup.enter="sendMessage" />
</div>
  `,
  navigation: {
    section: "main",
    icon: "chat",
    text: "Live Chat",
    path: "/chat",
    index: 30
  },
  data: function() {
    return {
      messages: [],
      input: ""
    };
  },
  mounted: function() {
    socket.on("message", (data) => {
      this.messages.push(data);
    });
  },
  methods: {
    sendMessage: function() {
      socket.emit("message", this.input);
      this.input = "";
    }
  }
};

Navigation.add(LivePage);
```

### Vuex Store Module

```javascript
// Add page-specific store module
store.registerModule("MyPage", {
  state: {
    items: []
  },
  mutations: {
    setItems: function(state, items) {
      state.items = items;
    },
    addItem: function(state, item) {
      state.items.push(item);
    }
  },
  getters: {
    items: function(state) {
      return state.items;
    }
  }
});

// Use in component
computed: {
  items: function() {
    return store.getters.items;
  }
}
```

## Common Patterns

### Form with Validation

```javascript
// Using vue-form-generator
var FormPage = {
  template: `
<div>
  <h1>Create Item</h1>
  <vue-form-generator
    ref="vfg"
    :schema="schema"
    :model="model"
    :options="formOptions"
    @validated="onValidated"
  />
  <v-btn
    @click="submit"
    :disabled="!isValid"
    color="primary"
  >
    Submit
  </v-btn>
</div>
  `,
  data: function() {
    return {
      isValid: false,
      model: { name: "", email: "" },
      schema: {
        fields: [
          {
            type: "input",
            inputType: "text",
            label: "Name",
            model: "name",
            required: true,
            validator: VueFormGenerator.validators.string
          },
          {
            type: "input",
            inputType: "email",
            label: "Email",
            model: "email",
            required: true,
            validator: VueFormGenerator.validators.email
          }
        ]
      },
      formOptions: {
        validateAfterChanged: true
      }
    };
  },
  methods: {
    onValidated: function(isValid, errors) {
      this.isValid = isValid;
    },
    submit: function() {
      $.ajax({
        url: "/api/items",
        type: "POST",
        data: JSON.stringify(this.model),
        contentType: "application/json",
        success: (response) => {
          app.$notify({
            group: "notifications",
            title: "Success",
            text: "Item created",
            type: "success"
          });
        }
      });
    }
  }
};
```

### Collection View Pattern

```javascript
// Reusable collection view
var MyCollection = {
  template: `
<CollectionView
  :headers="headers"
  :items="items"
  :loading="loading"
  @edit="onEdit"
  @delete="onDelete"
/>
  `,
  data: function() {
    return {
      headers: [
        { text: "Name", value: "name" }
      ],
      items: [],
      loading: false
    };
  },
  mounted: function() {
    this.load();
  },
  methods: {
    load: function() {
      this.loading = true;
      $.ajax({
        url: "/api/items",
        success: (response) => {
          this.items = response.items;
          this.loading = false;
        }
      });
    },
    onEdit: function(item) {
      // Handle edit
    },
    onDelete: function(item) {
      $.ajax({
        url: `/api/items/${item.id}`,
        type: "DELETE",
        success: () => this.load()
      });
    }
  }
};
```

## Debugging

### Common Issues

| Issue | Cause | Solution |
|-------|-------|----------|
| Page not loading | Missing route | Add `route="/page"` to `register_component()` |
| API 404 | Resource not registered | Add `server.add_resource()` call |
| 405 Method Not Allowed | Missing async method | Add `async def get(self):` to Resource |
| Socket.IO not connecting | Not using ASGI entry point | Use `app:asgi_app` with uvicorn |
| `RuntimeError: Not within a request context` | Using `request` in Socket.IO | Use `sid` parameter for Socket.IO handlers |
| Tests fail with async | Missing pytest-asyncio | Add `pytest-asyncio` to dev dependencies |

### Debug Commands

```bash
# Run development server with auto-reload
make run-dev

# Run tests
make test

# Check specific endpoint
curl http://localhost:8000/api/hello

# Check Socket.IO connection
# Open browser console, check for "socketio: connected"
```

## Testing

### Backend Tests

```python
import pytest
from app import server

@pytest.fixture
def app():
    server.config["TESTING"] = True
    return server

@pytest.mark.asyncio
async def test_api_endpoint(app):
    async with app.test_app() as test_app:
        client = test_app.test_client()
        response = await client.get("/api/hello")
        assert response.status_code == 200
        data = await response.get_json()
        assert "message" in data
```

## See Also

- `/baseweb-migrate` - Migrate Flask apps to Quart
- `/baseweb-create` - Create new baseweb projects
- `docs/migration-guide.md` - Migration documentation