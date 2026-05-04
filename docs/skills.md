# Baseweb Skills Documentation

Baseweb provides a comprehensive set of skills to help you create, develop, migrate, and review baseweb applications.

## Available Skills

| Skill | Purpose | Trigger |
|-------|---------|---------|
| **baseweb:create** | Create new projects | `/baseweb-create` |
| **baseweb:develop** | Develop features | `/baseweb-develop` |
| **baseweb:migrate** | Migrate Flask apps | `/baseweb-migrate` |
| **baseweb:review** | Review and improve | `/baseweb-review` |

---

## baseweb:create

Set up new baseweb applications with guided setup.

### When to Use
- Creating a new baseweb project
- Starting a new web application
- Setting up a project template

### Project Flavors

| Flavor | Description | Use Case |
|--------|-------------|----------|
| **minimal** | Basic setup, one page | Simple apps, learning |
| **standard** | REST API + pages | Typical web apps |
| **full** | REST API + WebSocket + Auth | Complex interactive apps |
| **pwa** | Progressive Web App | Installable web apps |
| **api-only** | REST API without UI | Backend services |

### Setup Questions
1. Project basics (name, description)
2. Project type (flavor)
3. Features (auth, WebSocket, database)
4. Frontend preferences

### Generated Files
- `pyproject.toml` - Project configuration
- `app/__init__.py` - Server setup
- `Makefile` - Run/test commands
- `.env` - Environment variables
- `.python-version` - Python version
- `tests/` - Test directory
- `pages/index/` - Initial page

---

## baseweb:develop

Create and maintain baseweb applications.

### When to Use
- Adding new pages
- Creating API endpoints
- Adding Socket.IO handlers
- Building Vue components
- Debugging issues

### Backend Development

**Pages:**
```python
# Register page with route
server.register_component("mypage.js", HERE, route="/mypage")

# Add REST endpoint
class MyResource(Resource):
    async def get(self):
        return {"data": "value"}

server.add_resource(MyResource, "/api/mypage")
```

**Socket.IO:**
```python
@server.socketio.on("message")
async def on_message(sid, data):
    return {"echo": data}
```

**Authentication:**
```python
@server.authenticated("app.resource.get")
async def get(self):
    return {"protected": "data"}
```

### Frontend Development

**Vue Component:**
```javascript
var MyPage = {
  template: `<div>...</div>`,
  navigation: {
    section: "main",
    icon: "star",
    text: "My Page",
    path: "/mypage",
    index: 10
  },
  data: function() { return {...}; },
  methods: {...}
};
Navigation.add(MyPage);
```

### Patterns Covered
- Forms with validation
- Collection views
- API integration
- Socket.IO client
- Vuex store modules

---

## baseweb:migrate

Migrate Flask-based baseweb apps to async Quart.

### When to Use
- Migrating baseweb `< 0.4.0` apps to `>= 1.0.0`
- Converting sync Flask to async Quart
- Modernizing legacy codebases

### Migration Overview

| From | To |
|------|-----|
| Flask | Quart |
| flask_restful.Resource | baseweb.Resource |
| Sync handlers | Async handlers |
| Flask-SocketIO | python-socketio (ASGI) |
| eventlet | uvicorn |

### Key Changes

**Imports:**
```python
# Before
from flask import request
from flask_restful import Resource

# After
from quart import request
from baseweb import Resource
```

**Async:**
```python
# Before
def get(self):
    data = request.get_json()
    return {"data": data}

# After
async def get(self):
    data = await request.get_json()
    return {"data": data}
```

**Socket.IO:**
```python
# Before
@server.socketio.on("message")
def handle(data):
    return {"echo": data}

# After
@server.socketio.on("message")
async def handle(sid, data):
    return {"echo": data}
```

### Migration Checklist
- [ ] Update dependencies
- [ ] Update imports
- [ ] Convert to async
- [ ] Migrate Socket.IO
- [ ] Create asgi_app entry point
- [ ] Update tests

---

## baseweb:review

Review baseweb applications for best practices.

### When to Use
- Auditing existing applications
- Before production deployment
- Code review preparation
- Refactoring planning

### Review Areas

| Area | Focus |
|------|-------|
| Architecture | Structure, patterns, organization |
| Security | Auth, validation, secrets |
| Performance | Async, queries, caching |
| Code Quality | Style, maintainability |
| Frontend | Components, state, UX |

### Common Issues

**Security:**
- Hardcoded secrets
- Missing input validation
- SQL/NoSQL injection risk

**Performance:**
- N+1 queries
- Missing caching
- Large payloads

**Code Quality:**
- Missing async keywords
- Flask-RESTful patterns (deprecated)
- No error handling

### Severity Levels

| Level | Action |
|-------|--------|
| Critical | Fix immediately |
| Warning | Fix soon |
| Suggestion | Consider |
| Positive | Good pattern |

---

## Using Skills

Skills are invoked through Claude Code using slash commands:

```bash
# Create new project
/baseweb-create

# Develop features
/baseweb-develop

# Migrate Flask app
/baseweb-migrate

# Review application
/baseweb-review
```

## Version Compatibility

| baseweb Version | Backend | WebSocket | Runner |
|-----------------|---------|-----------|--------|
| `< 0.4.0` | Flask | Flask-SocketIO | eventlet |
| `>= 1.0.0` | Quart | python-socketio | uvicorn |

## Additional Resources

- [Migration Guide](migration-guide.md)
- [API Documentation](api.md)
- [CHANGELOG](../CHANGELOG.md)
- [GitHub Repository](https://github.com/christophevg/baseweb)