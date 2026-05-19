# Consensus Report: task-6.2 - Push Notification Backend Infrastructure

**Created:** 2026-05-19
**Task:** task-6.2
**Status:** Approved for Implementation

---

## Domain Reviews

### API Architect Review

**Agent:** c3:api-architect
**Status:** ✅ Approved
**Analysis:** `analysis/api-push-notifications.md`

**Key Design Decisions:**

1. **RESTful Endpoints:**
   - GET `/api/vapid-public-key` - Return public VAPID key
   - POST `/api/push-subscriptions` - Register new subscription
   - GET `/api/push-subscriptions` - List user's subscriptions
   - DELETE `/api/push-subscriptions/{id}` - Remove subscription
   - POST `/api/push-notifications` - Send notification (202 Accepted)

2. **Async-first Design:**
   - Uses `webpush_async()` from pywebpush 2.1.0+
   - Background worker for notification sending

3. **Data Model:**
   - VAPIDKey: id, private_key, public_key, subject, created_at, is_active
   - PushSubscription: id, user_id, endpoint, keys (p256dh, auth), user_agent, device_name, created_at, last_successful_push, is_active

4. **Dependencies:**
   - py-vapid >= 1.9.0
   - pywebpush >= 2.1.0

### Security Engineer Review

**Agent:** c3:security-engineer
**Status:** ✅ Approved (with critical findings)
**Analysis:** `analysis/security-push-notifications.md`

**Critical Findings (Must Address):**

1. **CRITICAL-01: VAPID Private Key Storage (CVSS 9.1)**
   - Private keys must NEVER be hardcoded or committed
   - Use environment variables or secrets manager
   - Each application should have its own VAPID key pair

2. **CRITICAL-02: Subscription Endpoint Exposure (CVSS 9.0)**
   - Endpoint URLs are capability URLs
   - Must associate subscriptions with authenticated users
   - Must validate endpoints against known push services
   - Encrypt sensitive subscription data at rest

3. **HIGH-01: Rate Limiting (CVSS 7.5)**
   - Chrome enforces 1,000 msgs/min limit
   - Implement rate limiting on notification sending

4. **HIGH-02: VAPID Key Separation (CVSS 7.5)**
   - RFC 8292 requires separate keys for signing vs encryption

5. **HIGH-03: Input Validation (CVSS 7.0)**
   - Validate endpoint URLs
   - Validate key formats
   - Limit request sizes

**Medium Findings:**

6. Safari requires `sub`, `aud`, `exp` JWT claims
7. All subscription endpoints require user authentication
8. Log all push operations for security auditing

---

## Consensus

Both domain agents agree on the overall design with the following requirements:

### Must Implement (Blocking)

| Requirement | Source |
|-------------|--------|
| VAPID keys from environment/secrets | Security |
| Subscription endpoint validation | Security |
| Rate limiting on notification sending | Security |
| Input validation for all endpoints | Security |
| Authentication for subscription ops | Security + API |
| Async notification sending | API |

### Recommended

| Recommendation | Source |
|----------------|--------|
| Encrypt subscription data at rest | Security |
| Audit logging for push operations | Security |
| Mock push service for testing | API |
| Background worker for notifications | API |

---

## Implementation Plan

### Phase 1: VAPID Key Management

1. Add dependencies: py-vapid, pywebpush
2. Create VAPID key generation utility
3. Create environment-based VAPID key storage
4. Create GET /api/vapid-public-key endpoint

### Phase 2: Push Subscription Storage

1. Create PushSubscription data model
2. Create POST /api/push-subscriptions endpoint
3. Create GET /api/push-subscriptions endpoint
4. Create DELETE /api/push-subscriptions/{id} endpoint
5. Add authentication requirement
6. Add endpoint URL validation

### Phase 3: Notification Sending

1. Create PushNotificationSender utility
2. Create POST /api/push-notifications endpoint
3. Add rate limiting
4. Add async notification sending
5. Handle expired subscriptions (410/404 responses)

---

## Security Checklist

- [ ] VAPID private key stored in environment variable (not hardcoded)
- [ ] VAPID public key endpoint is unauthenticated
- [ ] Subscription registration requires authentication
- [ ] Subscription endpoint validated against known push services
- [ ] Notification sending requires admin/sender permission
- [ ] Rate limiting on subscription registration
- [ ] Rate limiting on notification sending
- [ ] Input validation on all endpoints
- [ ] Audit logging for push operations
- [ ] Expired subscriptions handled gracefully

---

## Test Strategy

### Unit Tests

- VAPID key generation
- VAPID key validation
- Subscription data validation
- Endpoint URL validation
- Rate limiting logic

### Integration Tests

- GET /api/vapid-public-key returns public key
- POST /api/push-subscriptions stores subscription
- DELETE /api/push-subscriptions/{id} removes subscription
- POST /api/push-notifications sends notification (mock)
- Authentication required for subscription endpoints
- Rate limiting enforced

### Mock Push Service

- Use pywebpush's mock mode for testing
- Or create fake push service endpoint

---

## Files to Create/Modify

| File | Action | Purpose |
|------|--------|---------|
| `src/baseweb/vapid.py` | Create | VAPID key management |
| `src/baseweb/push.py` | Create | Push notification sender |
| `src/baseweb/resources/push.py` | Create | API resources |
| `src/baseweb/models/push.py` | Create | Data models |
| `pyproject.toml` | Modify | Add dependencies |
| `tests/test_push.py` | Create | Test suite |

---

## Approval

- **API Architect:** ✅ Approved
- **Security Engineer:** ✅ Approved (with critical findings addressed)

**Decision:** Proceed to implementation (Phase 4)

---

*Consensus report prepared by: Project Manager Agent*
*Date: 2026-05-19*