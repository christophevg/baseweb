---
name: baseweb-review
description: Review baseweb applications and propose improvements
triggers:
  - when asked to review a baseweb application
  - when auditing a baseweb codebase
  - when improving an existing baseweb project
---

# Baseweb Review Skill

Review baseweb applications for best practices, security, performance, and code quality.

## Overview

This skill performs comprehensive reviews of baseweb applications:

| Review Area | Description |
|-------------|-------------|
| Architecture | Project structure, patterns, organization |
| Security | Authentication, authorization, input validation |
| Performance | Async patterns, database queries, caching |
| Code Quality | Style, maintainability, testing |
| Frontend | Vue components, state management, UX |

## When to Use

- Auditing existing baseweb applications
- Before deploying to production
- When inheriting a codebase
- During refactoring planning

## Review Checklist

### 1. Project Structure

```
✓ Check project follows standard baseweb structure
✓ app/ contains main application code
✓ pages/ organized by feature
✓ components/ for shared Vue components
✓ tests/ with comprehensive coverage
✓ pyproject.toml with proper dependencies
✓ .env for configuration (not hardcoded)
```

**Issues to flag:**
- Missing `asgi_app` entry point
- Hardcoded configuration
- Missing tests directory
- Outdated dependencies

### 2. Backend Code Quality

**Async Patterns:**
```python
# ✓ Correct
async def get(self):
    data = await request.get_json()
    return {"data": data}

# ✗ Wrong - missing async
def get(self):
    data = request.get_json()  # Will fail
    return {"data": data}

# ✗ Wrong - missing await
async def get(self):
    data = request.get_json()  # Returns coroutine, not data
    return {"data": data}
```

**Resource Registration:**
```python
# ✓ Correct - using native baseweb pattern
server.add_resource(MyResource, "/api/resource")

# ✗ Wrong - using deprecated Flask-RESTful pattern
from flask_restful import Api
api = Api(server)
api.add_resource(MyResource, "/api/resource")
```

**Socket.IO Handlers:**
```python
# ✓ Correct - async with sid parameter
@server.socketio.on("message")
async def on_message(sid, data):
    return {"echo": data}

# ✗ Wrong - sync, no sid
@server.socketio.on("message")
def on_message(data):
    return {"echo": data}
```

**Authentication:**
```python
# ✓ Correct - works for both HTTP and Socket.IO
@server.authenticated("app.resource.get")
async def get(self):
    return {"protected": "data"}

# ✗ Wrong - manual auth check
async def get(self):
    if not current_user:
        abort(401)
    return {"data": "value"}
```

### 3. Security Review

**Input Validation:**
```python
# ✓ Correct - validate input
async def post(self):
    data = await request.get_json()
    if "name" not in data:
        return {"error": "name required"}, 400
    if len(data["name"]) > 100:
        return {"error": "name too long"}, 400
    return {"created": data}

# ✗ Wrong - no validation
async def post(self):
    data = await request.get_json()
    return {"created": data}  # Accepts anything
```

**SQL/NoSQL Injection:**
```python
# ✓ Correct - parameterized
user = await db.users.find_one({"_id": user_id})

# ✗ Wrong - string concatenation
query = f"SELECT * FROM users WHERE id = {user_id}"
```

**Error Handling:**
```python
# ✓ Correct - don't leak internals
async def get(self, user_id):
    try:
        user = await get_user(user_id)
        return user
    except NotFoundError:
        return {"error": "Not found"}, 404
    except Exception:
        logger.exception("Unexpected error")
        return {"error": "Internal error"}, 500

# ✗ Wrong - exposes internals
async def get(self, user_id):
    user = await get_user(user_id)
    return user  # Might raise unhandled exception
```

**Secrets Management:**
```python
# ✓ Correct - from environment
SECRET_KEY = os.environ.get("SECRET_KEY")

# ✗ Wrong - hardcoded
SECRET_KEY = "super-secret-key-123"
```

### 4. Frontend Review

**Component Structure:**
```javascript
// ✓ Correct - proper structure
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

// ✗ Wrong - missing navigation
var MyPage = {
  template: `<div>...</div>`
};
// Page not in navigation
```

**API Error Handling:**
```javascript
// ✓ Correct - handles errors
loadData: function() {
  $.ajax({
    url: "/api/data",
    success: (response) => {
      this.data = response;
    },
    error: (xhr) => {
      app.$notify({
        group: "notifications",
        title: "Error",
        text: xhr.responseText,
        type: "error"
      });
    }
  });
}

// ✗ Wrong - no error handling
loadData: function() {
  $.ajax({
    url: "/api/data",
    success: (response) => {
      this.data = response;
    }
  });
}
```

**Socket.IO Connection:**
```javascript
// ✓ Correct - check connection
mounted: function() {
  socket.on("message", (data) => {
    this.messages.push(data);
  });
}

// ✗ Wrong - assumes socket exists
mounted: function() {
  socket.on("message", (data) => {
    // Will fail if socketio disabled
  });
}
```

### 5. Performance Review

**Database Queries:**
```python
# ✓ Correct - efficient query
users = await db.users.find({"active": True}).limit(100)

# ✗ Wrong - fetch all, filter in Python
users = await db.users.find()
active_users = [u for u in users if u["active"]]
```

**Caching:**
```python
# ✓ Correct - use caching for expensive operations
@cache.memoize(timeout=300)
async def get_expensive_data():
    return await compute_something()

# ✗ Wrong - recompute every time
async def get_expensive_data():
    return await compute_something()
```

**N+1 Queries:**
```python
# ✗ Wrong - N+1 problem
users = await db.users.find()
for user in users:
    posts = await db.posts.find({"user_id": user["_id"]})

# ✓ Correct - fetch related data together
users = await db.users.aggregate([
    {"$lookup": {
        "from": "posts",
        "localField": "_id",
        "foreignField": "user_id",
        "as": "posts"
    }}
])
```

### 6. Testing Review

**Test Coverage:**
```python
# ✓ Good coverage
- Unit tests for Resources
- Integration tests for API endpoints
- WebSocket handler tests
- Authentication tests

# ✗ Missing coverage
- No tests
- Only happy path tests
- Missing async test markers
```

**Async Test Patterns:**
```python
# ✓ Correct
@pytest.mark.asyncio
async def test_endpoint():
    async with app.test_app() as test_app:
        client = test_app.test_client()
        response = await client.get("/api/test")
        assert response.status_code == 200

# ✗ Wrong - missing async marker
def test_endpoint():
    response = client.get("/api/test")  # Won't work
```

## Review Report Template

Generate a structured report:

```markdown
# Baseweb Application Review: {app_name}

## Summary
- Overall Score: {score}/10
- Critical Issues: {count}
- Warnings: {count}
- Suggestions: {count}

## Critical Issues
1. [SECURITY] Description
   - Location: file:line
   - Fix: How to fix

## Warnings
1. [PERFORMANCE] Description
   - Location: file:line
   - Fix: How to fix

## Suggestions
1. [STYLE] Description
   - Location: file:line
   - Fix: How to fix

## Positive Findings
- Well-structured project
- Good test coverage
- Proper async patterns
```

## Severity Levels

| Level | Description | Action |
|-------|-------------|--------|
| **Critical** | Security vulnerability, data loss risk | Fix immediately |
| **Warning** | Performance issue, code smell | Fix soon |
| **Suggestion** | Style, maintainability | Consider fixing |
| **Positive** | Good pattern observed | Note as example |

## Common Issues by Category

### Architecture
- Missing `asgi_app` entry point
- Flask-RESTful imports (deprecated)
- Hardcoded configuration
- Missing error handling

### Security
- Hardcoded secrets
- No input validation
- SQL/NoSQL injection risk
- Missing authentication checks

### Performance
- N+1 queries
- Missing database indexes
- No caching
- Large response payloads

### Frontend
- Missing error handling
- No loading states
- Missing navigation config
- Socket.IO without fallback

## See Also

- `/baseweb-develop` - Development patterns
- `/baseweb-migrate` - Migration from Flask
- `/baseweb-create` - Project setup