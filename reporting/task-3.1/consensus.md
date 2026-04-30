# Consensus Report: Task 3.1 - Migrate Core Baseweb Class

**Created:** 2026-04-30
**Task:** task-3.1: Migrate core Baseweb class from Flask to Quart

---

## Domain Agent Reviews

### API Architect Analysis

**File:** `analysis/api-quart-migration.md`

**Key Findings:**
1. 6 internal route handlers must be converted to async
2. Critical async patterns needed:
   - `render_template()` → `await render_template()`
   - `send_from_directory()` → `await send_from_directory()`
   - Authentication decorator → async-aware
3. Public API surface remains synchronous (no breaking changes)
4. High-risk areas:
   - Flask-SocketIO (breaking change)
   - Authentication decorator
   - Flask-RESTful (requires quart-flask-patch)

### Security Engineer Analysis

**File:** `analysis/security-auth-migration.md`

**Key Findings:**
1. Authentication decorator must become async
2. Support both sync and async authenticators for backward compatibility
3. Critical: WebSocket session handling changes
4. Remove `self.request` instance attribute (race condition risk)
5. Add security logging for auth events

---

## Consensus Points

Both domain agents agree on the following:

### 1. Async Handler Conversion (P0)

| Handler | Current | Required |
|---------|---------|----------|
| Landing page | `def handler` | `async def handler` |
| Store | `def handler` | `async def handler` |
| Manifest | `def handler` | `async def handler` |
| Components | `def handler` | `async def handler` |
| Stylesheets | `def handler` | `async def handler` |
| Static files | `def handler` | `async def handler` |

### 2. Authentication Decorator (P0)

Both agents identify this as critical:

```python
# Required pattern
def authenticated(self, scope):
    def decorator(f):
        @wraps(f)
        async def wrapper(*args, **kwargs):
            if not await self._valid_credentials(scope, *args, **kwargs):
                return await self._return_401()
            return await f(*args, **kwargs)
        return wrapper
    return decorator
```

### 3. Backward Compatibility (P1)

- Public API methods remain synchronous
- Authenticator must support both sync and async callables
- Use `asyncio.iscoroutine()` to detect async authenticators

### 4. Testing Strategy (P1)

- 55 test stubs created
- Critical tests: async handlers, authentication
- Integration tests: concurrent requests, request isolation

---

## Migration Approach

### Phase A: Core Class Migration

1. Import Quart instead of Flask
2. Convert all route handlers to async
3. Add `await` to all I/O operations:
   - `render_template()`
   - `send_from_directory()`
   - `request.get_json()` (if used)

### Phase B: Authentication Migration

1. Convert `_valid_credentials()` to async
2. Convert `_return_401()` to async
3. Update `authenticated()` decorator for async
4. Support both sync and async authenticators

### Phase C: Testing

1. Run test suite (55 tests)
2. Fix any failing tests
3. Verify all routes work
4. Verify backward compatibility

---

## Risks and Mitigations

| Risk | Severity | Mitigation |
|------|----------|------------|
| Breaking sync authenticators | HIGH | Use `asyncio.iscoroutine()` for compatibility |
| Missing `await` keywords | MEDIUM | Test coverage + type checking |
| Request context race conditions | MEDIUM | Remove `self.request` storage |
| WebSocket session loss | HIGH | Document limitation, token-based auth |

---

## Test Coverage Requirements

| Category | Tests | Status |
|----------|-------|--------|
| Async handlers | 6 | Stubs created |
| Render template async | 4 | Stubs created |
| Send from directory async | 3 | Stubs created |
| Authentication | 8 | Stubs created |
| Valid credentials | 3 | Stubs created |
| Route handlers | 19 | Stubs created |
| Public API sync | 7 | Stubs created |
| Inheritance | 2 | Stubs created |
| Integration | 4 | Stubs created |
| Backward compatibility | 5 | Stubs created |
| Error handling | 3 | Stubs created |
| Responses | 3 | Stubs created |
| **Total** | **55** | **Stubs created** |

---

## Implementation Sign-Off

| Agent | Status | Notes |
|-------|--------|-------|
| c3:api-architect | ✓ APPROVED | Migration approach defined |
| c3:security-engineer | ✓ APPROVED | Security considerations documented |
| c3:testing-engineer | ✓ APPROVED | Test stubs created |

**Consensus:** All domain agents approve proceeding to implementation.

---

## Next Steps

1. **Phase 4:** Implement migration (c3:python-developer)
2. **Phase 5:** Review cycle
3. **Phase 6:** Complete task