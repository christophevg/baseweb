# Security Analysis: Push Notification Backend Infrastructure

**Task**: task-6.2 Push notification backend infrastructure
**Requirements**: R85, R86, R87, NFR3
**Date**: 2026-05-19

## Executive Summary

This security analysis covers the implementation of push notification backend infrastructure for baseweb. The primary security concerns center on VAPID key management, subscription data protection, and API endpoint security. Push notifications introduce unique security challenges because endpoint URLs function as capability URLs - knowledge of the endpoint alone is sufficient to send messages. This analysis identifies critical vulnerabilities and provides actionable remediation guidance.

---

## STRIDE Threat Model

### Trust Boundaries

```
+-------------------+     +-------------------+     +-------------------+
|   Client (PWA)    |     |   baseweb Server  |     |   Push Service    |
|                   |     |                   |     | (Apple/Google/    |
| - Service Worker  |---->| - VAPID Keys     |---->|  Mozilla)         |
| - PushManager     |     | - Subscriptions  |     |                   |
| - User Auth       |     | - REST APIs      |     | - Validates VAPID |
+-------------------+     +-------------------+     +-------------------+
        |                         |                         |
        | Trust Boundary          | Trust Boundary          |
        +-------------------------+-------------------------+
                    Untrusted Network (Internet)
```

### Threat Analysis

| STRIDE Category | Threat | Mitigation |
|----------------|--------|------------|
| **Spoofing** | Attacker impersonates legitimate notification sender | VAPID authentication, JWT token validation |
| **Tampering** | Notification payload modified in transit | ECDH encryption (RFC 8291), HTTPS |
| **Repudiation** | Malicious actor sends spam via compromised keys | Audit logging, rate limiting, VAPID subject claim |
| **Information Disclosure** | VAPID private key exposed in code/repository | Secrets manager, environment variables, no hardcoded keys |
| **Information Disclosure** | Subscription endpoints leaked to unauthorized parties | Access control, encryption at rest, user association |
| **Denial of Service** | Spam attacks via notification flood | Rate limiting, frequency caps, Chrome enforcement |
| **Elevation of Privilege** | Unauthorized subscription manipulation | Authentication requirement, CSRF protection |

---

## OWASP Top 10:2025 Classification

| ID | Category | Relevant Findings |
|----|----------|-------------------|
| **A01** | Broken Access Control | Subscription endpoints require user authentication |
| **A02** | Security Misconfiguration | VAPID key storage, CORS configuration for push APIs |
| **A03** | Software Supply Chain | Web push library vulnerabilities |
| **A04** | Cryptographic Failures | VAPID key management, ECDH key separation |
| **A05** | Injection | Subscription data validation, endpoint URL injection |
| **A07** | Authentication Failures | VAPID JWT validation, user authentication for subscriptions |
| **A09** | Security Logging Failures | Audit trail for notification sends, failed authentications |

---

## Critical Findings

### CRITICAL-01: VAPID Private Key Storage

**Severity**: Critical (CVSS 9.1)
**OWASP**: A04:2021 - Cryptographic Failures
**STRIDE**: Information Disclosure

#### Description

VAPID private keys must never be hardcoded in source code, configuration files committed to version control, or exposed in client-side applications. If a VAPID private key is compromised, an attacker can:
- Send push notifications appearing to come from your application
- Distribute phishing content or malware links
- Destroy user trust in your platform
- Bypass authentication to push services

#### Impact

- Complete compromise of push notification system
- Attacker can impersonate application to all subscribers
- User data exposure through malicious notifications
- Reputation damage and potential legal liability

#### Remediation

**1. Use environment variables for VAPID private key**

```python
import os
from py_vapid import Vapid

# Never hardcode the private key
# BAD: VAPID_PRIVATE_KEY = "ABcDEfghIjKL1M..."
# GOOD:
VAPID_PRIVATE_KEY = os.environ.get("VAPID_PRIVATE_KEY")

if not VAPID_PRIVATE_KEY:
    raise RuntimeError("VAPID_PRIVATE_KEY environment variable not set")

vapid = Vapid()
vapid.from_pem(VAPID_PRIVATE_KEY.encode())
```

**2. Use secrets manager for production deployments**

```python
# AWS Secrets Manager example
import boto3

def get_vapid_private_key():
    client = boto3.client('secretsmanager')
    response = client.get_secret_value(SecretId='baseweb/vapid/private-key')
    return response['SecretString']

# HashiCorp Vault example
import hvac

def get_vapid_private_key():
    client = hvac.Client(url='https://vault.example.com')
    response = client.secrets.kv.v2.read_secret_version(path='vapid')
    return response['data']['data']['private_key']
```

**3. Generate keys securely**

```python
from py_vapid import Vapid
import os

def generate_vapid_keys():
    """Generate new VAPID key pair and store securely."""
    vapid = Vapid()
    vapid.generate_keys()
    
    private_key_pem = vapid.to_pem(private_key=True)
    public_key_b64 = vapid.to_base64(public_key=True)
    
    # Store private key in secrets manager (NOT in code)
    # Only return public key for client distribution
    return {
        "public_key": public_key_b64,
        "private_key_pem": private_key_pem  # Store in secrets manager!
    }
```

**4. Add to .gitignore**

```gitignore
# VAPID keys - NEVER commit these
*.pem
vapid_private_key*
.env.local
.env.*.local
secrets/
```

#### References

- [RFC 8292: VAPID for Web Push](https://rfc-editor.org/rfc/rfc8292.html)
- [GitGuardian: VAPID Key Security](https://docs.gitguardian.com/secrets-detection/secrets-detection-engine/detectors/specifics/vapid_key)

---

### CRITICAL-02: Push Subscription Endpoint Exposure

**Severity**: Critical (CVSS 9.0)
**OWASP**: A01:2021 - Broken Access Control
**STRIDE**: Information Disclosure

#### Description

From MDN Push API documentation:
> "The endpoint for the subscription is a unique capability URL: **knowledge of the endpoint is all that is necessary to send a message to your application. The endpoint URL therefore needs to be kept secret**, or other applications might be able to send push messages to your application."

Subscription endpoints are bearer tokens. Anyone with the endpoint URL can send push notifications to that subscriber without any additional authentication.

#### Impact

- Unauthorized notification delivery
- Phishing attacks via push notifications
- Spam delivery to users
- Potential for social engineering attacks

#### Remediation

**1. Always associate subscriptions with authenticated users**

```python
from quart import request, current_app
import hashlib

class PushSubscriptionResource(Resource):
    async def post(self):
        """Store a new push subscription - requires authentication."""
        # Require authentication
        user = await get_current_user()
        if not user:
            return {"error": "Authentication required"}, 401
        
        data = await request.get_json()
        
        # Validate subscription data
        subscription = validate_subscription(data)
        if not subscription:
            return {"error": "Invalid subscription data"}, 400
        
        # Validate endpoint is from known push service
        if not is_valid_push_service(subscription['endpoint']):
            return {"error": "Invalid push service endpoint"}, 400
        
        # Store with user association
        subscription_record = {
            "user_id": user.id,
            "endpoint": subscription['endpoint'],
            "keys": {
                "p256dh": subscription['keys']['p256dh'],
                "auth": subscription['keys']['auth']
            },
            "created_at": datetime.utcnow(),
            "user_agent": request.user_agent.string,
            "ip_address": hash_ip(request.remote_addr)  # Hashed for privacy
        }
        
        await store_subscription(subscription_record)
        return {"status": "subscribed"}, 201
```

**2. Validate endpoint URLs against known push services**

```python
from urllib.parse import urlparse

ALLOWED_PUSH_SERVICES = [
    'fcm.googleapis.com',
    'updates.push.services.mozilla.com',
    'web.push.apple.com',
    # Add other legitimate push services
]

def is_valid_push_service(endpoint_url: str) -> bool:
    """Validate that endpoint is from a known push service."""
    try:
        parsed = urlparse(endpoint_url)
        
        # Must be HTTPS
        if parsed.scheme != 'https':
            return False
        
        # Must be from known push service
        for allowed in ALLOWED_PUSH_SERVICES:
            if parsed.netloc == allowed or parsed.netloc.endswith('.' + allowed):
                return True
        
        return False
    except Exception:
        return False
```

**3. Encrypt sensitive subscription data at rest**

```python
from cryptography.fernet import Fernet
import os

# Store encryption key in secrets manager
SUBSCRIPTION_ENCRYPTION_KEY = os.environ.get("SUBSCRIPTION_ENCRYPTION_KEY")

def encrypt_subscription_data(data: dict) -> dict:
    """Encrypt sensitive subscription fields before storage."""
    fernet = Fernet(SUBSCRIPTION_ENCRYPTION_KEY)
    
    return {
        "user_id": data["user_id"],
        "endpoint": data["endpoint"],  # Endpoint can be stored unencrypted for querying
        "keys": {
            "p256dh": fernet.encrypt(data["keys"]["p256dh"].encode()).decode(),
            "auth": fernet.encrypt(data["keys"]["auth"].encode()).decode()
        },
        "created_at": data["created_at"]
    }
```

**4. Implement access control for subscription retrieval**

```python
async def get_user_subscriptions(user_id: str) -> list:
    """Get all subscriptions for a user - requires user context."""
    # Never return subscriptions without authentication
    subscriptions = await db.query(
        "SELECT * FROM push_subscriptions WHERE user_id = ?",
        user_id
    )
    return subscriptions

async def delete_subscription(user_id: str, endpoint: str) -> bool:
    """Delete a subscription - requires user ownership."""
    result = await db.execute(
        "DELETE FROM push_subscriptions WHERE user_id = ? AND endpoint = ?",
        user_id, endpoint
    )
    return result.rowcount > 0
```

#### References

- [MDN Push API](https://developer.mozilla.org/en-US/docs/Web/API/Push_API)
- [W3C Push API Specification](https://www.w3.org/TR/2025/WD-push-api-20251201/)

---

## High Findings

### HIGH-01: Rate Limiting for Push Notifications

**Severity**: High (CVSS 7.5)
**OWASP**: A06:2021 - Vulnerable and Outdated Components (API)
**STRIDE**: Denial of Service

#### Description

Chrome has implemented push message rate limits to combat notification spam. Sites flagged as "disruptive" are limited to 1,000 push messages per minute. Without server-side rate limiting, malicious actors can abuse push notification APIs to send spam or cause denial of service.

#### Impact

- Application blocked by browser rate limits
- Reputation damage from spam classification
- Potential legal liability for harassment
- User trust destruction

#### Remediation

**1. Implement server-side rate limiting**

```python
from datetime import datetime, timedelta
from collections import defaultdict
import asyncio

class PushRateLimiter:
    """Rate limiter for push notifications."""
    
    def __init__(self):
        # In production, use Redis or similar distributed store
        self._send_history = defaultdict(list)
        self._limits = {
            "per_user_per_day": 10,      # Max 10 notifications per user per day
            "per_app_per_minute": 100,    # Max 100 notifications per app per minute
            "per_user_per_hour": 3,       # Max 3 notifications per user per hour
        }
    
    async def can_send(self, user_id: str) -> tuple[bool, str]:
        """Check if we can send a notification to this user."""
        now = datetime.utcnow()
        history = self._send_history[user_id]
        
        # Clean old entries
        self._send_history[user_id] = [
            ts for ts in history if now - ts < timedelta(hours=24)
        ]
        
        # Check daily limit
        daily_count = len([ts for ts in self._send_history[user_id] 
                          if now - ts < timedelta(days=1)])
        if daily_count >= self._limits["per_user_per_day"]:
            return False, "Daily notification limit exceeded"
        
        # Check hourly limit
        hourly_count = len([ts for ts in self._send_history[user_id] 
                           if now - ts < timedelta(hours=1)])
        if hourly_count >= self._limits["per_user_per_hour"]:
            return False, "Hourly notification limit exceeded"
        
        return True, ""
    
    async def record_send(self, user_id: str):
        """Record a notification send."""
        self._send_history[user_id].append(datetime.utcnow())
    
    async def cleanup(self):
        """Periodic cleanup of old entries."""
        now = datetime.utcnow()
        for user_id in list(self._send_history.keys()):
            self._send_history[user_id] = [
                ts for ts in self._send_history[user_id]
                if now - ts < timedelta(days=1)
            ]
            if not self._send_history[user_id]:
                del self._send_history[user_id]

# Use in notification sending
rate_limiter = PushRateLimiter()

async def send_push_notification(user_id: str, payload: dict):
    """Send push notification with rate limiting."""
    can_send, reason = await rate_limiter.can_send(user_id)
    if not can_send:
        return {"error": reason}, 429
    
    # Proceed with sending
    subscription = await get_user_subscription(user_id)
    await webpush(subscription, payload, vapid_claims)
    await rate_limiter.record_send(user_id)
```

**2. Use Redis for distributed rate limiting**

```python
import aioredis

class RedisRateLimiter:
    """Distributed rate limiter using Redis."""
    
    def __init__(self, redis_url: str):
        self.redis = aioredis.from_url(redis_url)
    
    async def can_send(self, user_id: str, limit: int, window: int) -> bool:
        """
        Check rate limit using sliding window.
        
        Args:
            user_id: User identifier
            limit: Maximum requests allowed
            window: Time window in seconds
        
        Returns:
            True if request is allowed
        """
        key = f"push_limit:{user_id}"
        now = int(time.time())
        
        # Remove old entries
        await self.redis.zremrangebyscore(key, 0, now - window)
        
        # Count current entries
        count = await self.redis.zcard(key)
        
        if count >= limit:
            return False
        
        # Add new entry
        await self.redis.zadd(key, {str(now): now})
        await self.redis.expire(key, window)
        
        return True
```

**3. Implement exponential backoff for retries**

```python
import asyncio
import random

async def send_with_retry(subscription: dict, payload: dict, max_retries: int = 3):
    """Send push notification with exponential backoff."""
    for attempt in range(max_retries):
        try:
            await webpush(subscription, payload, vapid_claims)
            return True
        except Exception as e:
            if attempt == max_retries - 1:
                raise
            
            # Exponential backoff with jitter
            delay = (2 ** attempt) + random.uniform(0, 1)
            await asyncio.sleep(delay)
    
    return False
```

#### References

- [Chrome Push Notification Rate Limits](https://developer.chrome.com/blog/web-push-rate-limits)
- [OneSignal Rate Limits Documentation](https://documentation.onesignal.com/reference/rate-limits)

---

### HIGH-02: VAPID Key Separation

**Severity**: High (CVSS 7.5)
**OWASP**: A04:2021 - Cryptographic Failures
**STRIDE**: Spoofing

#### Description

RFC 8292 explicitly states:
> "An application server MUST select a different private key for key exchange (RFC 8291) and signing the authentication token."

Using the same key for both purposes can result in 400 Bad Request rejections from push services and weakens the overall security model.

#### Impact

- Push service rejections (400 Bad Request)
- Weakened cryptographic security
- Potential for key compromise to affect multiple security layers

#### Remediation

**1. Use separate keys for VAPID and content encryption**

```python
from py_vapid import Vapid
from pywebpush import webpush

# Generate and store separate key pairs
class VAPIDKeyManager:
    """Manage VAPID keys with proper separation."""
    
    def __init__(self):
        self.vapid_key = None  # For JWT signing
        self.content_key = None  # For ECDH content encryption (per subscription)
    
    async def initialize(self):
        """Load keys from secure storage."""
        # VAPID key for signing JWT tokens
        vapid_private_pem = await secrets_manager.get("vapid/signing_key")
        self.vapid_key = Vapid()
        self.vapid_key.from_pem(vapid_private_pem.encode())
        
        # Note: Content encryption uses per-subscription ECDH keys
        # generated from the subscription's p256dh key
    
    def get_vapid_claims(self, push_service_url: str) -> dict:
        """Generate VAPID claims for JWT token."""
        import time
        
        return {
            "sub": "mailto:admin@yourdomain.com",  # Required by Safari
            "aud": push_service_url,  # e.g., "https://web.push.apple.com"
            "exp": int(time.time()) + 86400,  # Max 24 hours
        }
    
    def get_public_key(self) -> str:
        """Get public key for client distribution."""
        return self.vapid_key.to_base64(public_key=True)
```

**2. Never reuse or share keys between applications**

```python
# BAD - Don't do this
SHARED_VAPID_KEY = Vapid()
SHARED_VAPID_KEY.from_pem(shared_key_pem)  # Used by multiple apps

# GOOD - Each application has its own key
class ApplicationVAPIDKeys:
    """Each application has its own VAPID key pair."""
    
    def __init__(self, app_id: str):
        self.app_id = app_id
        self._load_keys()
    
    async def _load_keys(self):
        """Load app-specific keys from secrets manager."""
        key_path = f"apps/{self.app_id}/vapid/private_key"
        self.vapid_key = Vapid()
        private_pem = await secrets_manager.get(key_path)
        self.vapid_key.from_pem(private_pem.encode())
```

#### References

- [RFC 8292: VAPID for Web Push](https://rfc-editor.org/rfc/rfc8292.html)
- [Apple Developer: Sending Web Push Notifications](https://developer.apple.com/documentation/usernotifications/sending_web_push_notifications_in_web_apps_safari_and_other_browsers)

---

### HIGH-03: Input Validation for Subscription Data

**Severity**: High (CVSS 7.0)
**OWASP**: A03:2021 - Injection
**STRIDE**: Tampering

#### Description

Subscription data from clients must be thoroughly validated before storage. Malicious input could include:
- Invalid endpoint URLs (pointing to attacker-controlled servers)
- Oversized keys causing storage issues
- Malformed JSON causing parsing errors
- XSS payloads in user agent strings

#### Impact

- Data corruption
- SSRF attacks via crafted endpoints
- Storage exhaustion
- Potential XSS in admin interfaces

#### Remediation

**1. Validate all subscription fields**

```python
from urllib.parse import urlparse
import re
from typing import Optional

class SubscriptionValidator:
    """Validate push subscription data."""
    
    # Base64url pattern for p256dh and auth keys
    BASE64URL_PATTERN = re.compile(r'^[A-Za-z0-9_-]+$')
    MAX_KEY_LENGTH = 200  # Reasonable limit for base64 encoded keys
    MAX_ENDPOINT_LENGTH = 500
    
    @classmethod
    def validate(cls, data: dict) -> tuple[bool, Optional[str], Optional[dict]]:
        """
        Validate subscription data.
        
        Returns:
            (is_valid, error_message, cleaned_data)
        """
        if not isinstance(data, dict):
            return False, "Subscription must be a JSON object", None
        
        # Validate endpoint
        endpoint = data.get('endpoint')
        if not endpoint:
            return False, "Endpoint is required", None
        
        if not isinstance(endpoint, str):
            return False, "Endpoint must be a string", None
        
        if len(endpoint) > cls.MAX_ENDPOINT_LENGTH:
            return False, "Endpoint too long", None
        
        try:
            parsed = urlparse(endpoint)
            if parsed.scheme != 'https':
                return False, "Endpoint must use HTTPS", None
            if not parsed.netloc:
                return False, "Invalid endpoint URL", None
        except Exception:
            return False, "Invalid endpoint URL format", None
        
        # Validate push service domain
        if not cls.is_valid_push_service(endpoint):
            return False, "Endpoint must be from a known push service", None
        
        # Validate keys
        keys = data.get('keys')
        if not keys or not isinstance(keys, dict):
            return False, "Keys object is required", None
        
        p256dh = keys.get('p256dh')
        auth = keys.get('auth')
        
        if not p256dh or not auth:
            return False, "Both p256dh and auth keys are required", None
        
        if not isinstance(p256dh, str) or not isinstance(auth, str):
            return False, "Keys must be strings", None
        
        if len(p256dh) > cls.MAX_KEY_LENGTH or len(auth) > cls.MAX_KEY_LENGTH:
            return False, "Key values too long", None
        
        if not cls.BASE64URL_PATTERN.match(p256dh):
            return False, "p256dh must be base64url encoded", None
        
        if not cls.BASE64URL_PATTERN.match(auth):
            return False, "auth must be base64url encoded", None
        
        # Return cleaned data
        cleaned = {
            'endpoint': endpoint,
            'keys': {
                'p256dh': p256dh,
                'auth': auth
            }
        }
        
        return True, None, cleaned
    
    @classmethod
    def is_valid_push_service(cls, endpoint: str) -> bool:
        """Check if endpoint is from a known push service."""
        KNOWN_PUSH_SERVICES = [
            'fcm.googleapis.com',
            'updates.push.services.mozilla.com',
            'web.push.apple.com',
        ]
        
        parsed = urlparse(endpoint)
        for service in KNOWN_PUSH_SERVICES:
            if parsed.netloc == service or parsed.netloc.endswith('.' + service):
                return True
        return False
```

**2. Sanitize user agent and IP for logging**

```python
import hashlib
import re

def sanitize_user_agent(user_agent: str) -> str:
    """Remove potentially malicious content from user agent."""
    # Limit length
    user_agent = user_agent[:500]
    # Remove control characters
    user_agent = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', user_agent)
    return user_agent

def hash_ip(ip_address: str) -> str:
    """Hash IP address for privacy-preserving logging."""
    # Add salt from environment
    salt = os.environ.get('IP_HASH_SALT', 'default-salt-change-in-production')
    return hashlib.sha256(f"{salt}{ip_address}".encode()).hexdigest()[:16]
```

**3. Implement request size limits**

```python
from quart import request, abort

class PushSubscriptionResource(Resource):
    async def post(self):
        """Store push subscription with input validation."""
        # Limit request size
        if request.content_length > 1024:  # 1KB limit
            abort(413, "Request too large")
        
        data = await request.get_json()
        
        if not data:
            return {"error": "Invalid JSON"}, 400
        
        is_valid, error, cleaned = SubscriptionValidator.validate(data)
        if not is_valid:
            return {"error": error}, 400
        
        # Use cleaned data
        await store_subscription(cleaned)
        return {"status": "subscribed"}, 201
```

#### References

- [OWASP Input Validation Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Input_Validation_Cheat_Sheet.html)
- [W3C Push API Security](https://www.w3.org/TR/2025/WD-push-api-20251201/)

---

## Medium Findings

### MEDIUM-01: Safari-Specific VAPID Requirements

**Severity**: Medium (CVSS 5.3)
**OWASP**: A07:2021 - Identification and Authentication Failures
**STRIDE**: Spoofing

#### Description

Safari requires specific VAPID JWT claims that are optional in the Web Push specification:
- **`sub` claim**: Must include a contact URI (mailto: or https:)
- **`aud` claim**: Must be the exact push service origin
- **`exp` claim**: Must not exceed 24 hours

Missing these claims results in `BadJwtToken` errors from Safari, breaking iOS push notification functionality.

#### Impact

- Push notifications fail on iOS Safari
- Poor user experience
- Debugging difficulty (errors don't clearly indicate missing claims)

#### Remediation

**1. Implement Safari-compatible VAPID claims**

```python
import time
from datetime import datetime, timedelta

def get_vapid_claims(push_service_url: str, contact_email: str) -> dict:
    """
    Generate VAPID claims compatible with all browsers including Safari.
    
    Args:
        push_service_url: The push service endpoint (e.g., "https://web.push.apple.com")
        contact_email: Contact email for the application maintainer
    
    Returns:
        VAPID claims dictionary
    """
    # Parse the push service URL to get origin
    from urllib.parse import urlparse
    parsed = urlparse(push_service_url)
    audience = f"{parsed.scheme}://{parsed.netloc}"
    
    claims = {
        "sub": f"mailto:{contact_email}",  # Required by Safari
        "aud": audience,  # Must match push service origin exactly
        "exp": int(time.time()) + 43200,  # 12 hours (max is 24)
    }
    
    return claims

# Usage example
async def send_notification(subscription: dict, payload: dict):
    """Send notification with proper VAPID claims."""
    endpoint = subscription['endpoint']
    
    # Determine push service URL from endpoint
    if 'apple.com' in endpoint:
        push_service = "https://web.push.apple.com"
    elif 'googleapis.com' in endpoint:
        push_service = "https://fcm.googleapis.com"
    elif 'mozilla.com' in endpoint:
        push_service = "https://updates.push.services.mozilla.com"
    else:
        # Fallback - extract origin from endpoint
        from urllib.parse import urlparse
        parsed = urlparse(endpoint)
        push_service = f"{parsed.scheme}://{parsed.netloc}"
    
    claims = get_vapid_claims(push_service, "admin@yourdomain.com")
    
    await webpush(
        subscription_info=subscription,
        data=json.dumps(payload),
        vapid_private_key=vapid_private_key,
        vapid_claims=claims
    )
```

**2. Cache VAPID tokens appropriately**

```python
import time
from functools import lru_cache

# VAPID tokens can be reused within their validity window
# Don't refresh more than once per hour (Safari recommendation)

VAPID_TOKEN_CACHE = {}
VAPID_TOKEN_TTL = 3600  # 1 hour

def get_cached_vapid_claims(push_service_url: str) -> dict:
    """Get VAPID claims with caching."""
    cache_key = push_service_url
    now = time.time()
    
    if cache_key in VAPID_TOKEN_CACHE:
        cached = VAPID_TOKEN_CACHE[cache_key]
        if now - cached['created'] < VAPID_TOKEN_TTL:
            return cached['claims']
    
    # Generate new claims
    claims = get_vapid_claims(push_service_url, "admin@yourdomain.com")
    VAPID_TOKEN_CACHE[cache_key] = {
        'claims': claims,
        'created': now
    }
    
    return claims
```

#### References

- [Apple Developer: Sending Web Push Notifications](https://developer.apple.com/documentation/usernotifications/sending_web_push_notifications_in_web_apps_safari_and_other_browsers)
- [WebKit Blog: Web Push for iOS](https://webkit.org/blog/13878/web-push-for-web-apps-on-ios-and-ipados)

---

### MEDIUM-02: Authentication Requirements for Subscription Endpoints

**Severity**: Medium (CVSS 6.5)
**OWASP**: A01:2021 - Broken Access Control
**STRIDE**: Elevation of Privilege

#### Description

Push subscription endpoints must require user authentication to prevent:
- Anonymous users flooding subscription storage
- Subscription hijacking
- Unauthorized notification targeting

#### Impact

- Storage exhaustion from anonymous subscriptions
- Spam vector through anonymous notification registration
- Difficulty tracking notification permissions

#### Remediation

**1. Require authentication for all subscription operations**

```python
from baseweb import Baseweb
from baseweb.resource import Resource

server = Baseweb()

# Set up authentication
async def authenticator(scope, request, *args, **kwargs):
    """Authenticate user for push subscription operations."""
    # Integrate with your authentication system
    auth_header = request.headers.get('Authorization')
    if not auth_header:
        return False
    
    # Validate token (e.g., JWT, session cookie)
    user = await validate_auth_token(auth_header)
    if not user:
        return False
    
    # Store user in request context
    request.user = user
    return True

server.authenticator = authenticator

class PushSubscriptionResource(Resource):
    """RESTful resource for push subscriptions."""
    
    async def post(self):
        """Subscribe to push notifications - requires authentication."""
        # Authentication already verified by decorator
        user = request.user
        
        data = await request.get_json()
        is_valid, error, cleaned = SubscriptionValidator.validate(data)
        if not is_valid:
            return {"error": error}, 400
        
        # Store subscription with user association
        await store_subscription(user.id, cleaned)
        return {"status": "subscribed"}, 201
    
    async def get(self):
        """Get user's subscriptions - requires authentication."""
        user = request.user
        subscriptions = await get_user_subscriptions(user.id)
        return {"subscriptions": subscriptions}, 200
    
    async def delete(self):
        """Unsubscribe - requires authentication."""
        user = request.user
        data = await request.get_json()
        endpoint = data.get('endpoint')
        
        if not endpoint:
            return {"error": "endpoint required"}, 400
        
        await delete_subscription(user.id, endpoint)
        return {"status": "unsubscribed"}, 200

# Register with authentication requirement
server.add_resource(
    PushSubscriptionResource,
    '/api/push/subscription',
    endpoint='push-subscription',
    security_scope='api.push.subscription'
)
```

**2. Implement CSRF protection for subscription endpoints**

```python
from quart import request, abort
import secrets

# CSRF token management
CSRF_TOKEN_HEADER = 'X-CSRF-Token'

async def validate_csrf_token():
    """Validate CSRF token for state-changing operations."""
    if request.method in ['POST', 'PUT', 'DELETE', 'PATCH']:
        token = request.headers.get(CSRF_TOKEN_HEADER)
        session_token = getattr(request, 'csrf_token', None)
        
        if not token or not session_token or not secrets.compare_digest(token, session_token):
            abort(403, "Invalid CSRF token")

# Apply to subscription endpoints
@server.before_request
async def check_csrf():
    if request.path.startswith('/api/push/'):
        await validate_csrf_token()
```

**3. Use baseweb's existing authentication pattern**

```python
# Leverage baseweb's authenticated decorator
@server.authenticated('api.push.subscription')
async def send_push_endpoint(user_id: str, payload: dict):
    """Send push notification - requires authentication."""
    # Authentication verified by decorator
    subscriptions = await get_user_subscriptions(user_id)
    
    for subscription in subscriptions:
        await send_push_notification(subscription, payload)
    
    return {"sent": len(subscriptions)}, 200
```

#### References

- [MDN Push API Best Practices](https://developer.mozilla.org/en-US/docs/Web/API/Push_API/Best_Practices)
- [OWASP CSRF Prevention Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Cross-Site_Request_Forgery_Prevention_Cheat_Sheet.html)

---

### MEDIUM-03: Audit Logging for Push Operations

**Severity**: Medium (CVSS 5.0)
**OWASP**: A09:2021 - Security Logging and Monitoring Failures
**STRIDE**: Repudiation

#### Description

Push notification operations must be logged for security auditing, debugging, and compliance. Without proper logging:
- Cannot detect abuse patterns
- Cannot debug failed deliveries
- Cannot trace notification history
- Cannot comply with data protection regulations

#### Impact

- Unable to investigate security incidents
- No visibility into notification delivery failures
- Compliance violations
- Difficulty debugging user issues

#### Remediation

**1. Implement comprehensive audit logging**

```python
import logging
from datetime import datetime
from dataclasses import dataclass
from typing import Optional
import json

# Dedicated logger for push operations
push_logger = logging.getLogger('baseweb.push')
push_logger.setLevel(logging.INFO)

# Add structured handler
handler = logging.FileHandler('/var/log/baseweb/push_audit.log')
handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
push_logger.addHandler(handler)

@dataclass
class PushAuditEvent:
    """Audit event for push operations."""
    event_type: str  # subscribe, unsubscribe, send, error
    user_id: str
    endpoint: Optional[str] = None
    success: bool = True
    error_message: Optional[str] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    notification_type: Optional[str] = None
    
    def to_json(self) -> str:
        return json.dumps({
            "timestamp": datetime.utcnow().isoformat(),
            "event_type": self.event_type,
            "user_id": self.user_id,
            "endpoint_hash": hash_ip(self.endpoint) if self.endpoint else None,
            "success": self.success,
            "error_message": self.error_message,
            "ip_hash": hash_ip(self.ip_address) if self.ip_address else None,
            "user_agent": sanitize_user_agent(self.user_agent) if self.user_agent else None,
            "notification_type": self.notification_type
        })

async def log_push_event(event: PushAuditEvent):
    """Log a push notification event."""
    push_logger.info(event.to_json())

# Usage in subscription operations
async def subscribe_user(user_id: str, subscription: dict, request):
    """Subscribe user with audit logging."""
    try:
        await store_subscription(user_id, subscription)
        await log_push_event(PushAuditEvent(
            event_type="subscribe",
            user_id=user_id,
            endpoint=subscription['endpoint'],
            success=True,
            ip_address=request.remote_addr,
            user_agent=request.user_agent.string
        ))
    except Exception as e:
        await log_push_event(PushAuditEvent(
            event_type="subscribe",
            user_id=user_id,
            endpoint=subscription.get('endpoint'),
            success=False,
            error_message=str(e),
            ip_address=request.remote_addr,
            user_agent=request.user_agent.string
        ))
        raise

# Usage in send operations
async def send_notification(user_id: str, payload: dict, notification_type: str):
    """Send notification with audit logging."""
    try:
        result = await webpush(subscription, payload, vapid_claims)
        await log_push_event(PushAuditEvent(
            event_type="send",
            user_id=user_id,
            endpoint=subscription['endpoint'],
            success=True,
            notification_type=notification_type
        ))
        return result
    except Exception as e:
        await log_push_event(PushAuditEvent(
            event_type="send",
            user_id=user_id,
            endpoint=subscription.get('endpoint'),
            success=False,
            error_message=str(e),
            notification_type=notification_type
        ))
        raise
```

**2. Log failed delivery responses**

```python
async def handle_push_response(response, subscription):
    """Handle push service response and log appropriately."""
    status_code = response.status_code
    
    if status_code == 201:
        # Success - notification created
        return True
    
    elif status_code == 429:
        # Rate limited
        push_logger.warning(f"Rate limited for subscription")
        await handle_rate_limit(subscription)
        return False
    
    elif status_code == 410:
        # Subscription no longer valid
        push_logger.info(f"Subscription expired, removing")
        await delete_invalid_subscription(subscription['endpoint'])
        return False
    
    elif status_code == 404:
        # Subscription not found
        push_logger.info(f"Subscription not found, removing")
        await delete_invalid_subscription(subscription['endpoint'])
        return False
    
    elif status_code == 400:
        # Invalid request
        push_logger.error(f"Invalid push request: {response.text}")
        return False
    
    else:
        push_logger.error(f"Unexpected push response: {status_code}")
        return False
```

**3. Security event alerts**

```python
from datetime import datetime, timedelta
from collections import defaultdict

# Alert thresholds
ALERT_THRESHOLDS = {
    "failed_sends_per_hour": 100,
    "rate_limits_per_hour": 10,
    "invalid_subscriptions_per_hour": 50,
}

# Track security events
security_events = defaultdict(list)

async def check_security_alerts():
    """Check for security anomalies."""
    now = datetime.utcnow()
    one_hour_ago = now - timedelta(hours=1)
    
    # Count recent failures
    recent_failures = [e for e in security_events['send_failure'] if e > one_hour_ago]
    if len(recent_failures) > ALERT_THRESHOLDS['failed_sends_per_hour']:
        await send_alert("High rate of push send failures detected")
    
    recent_rate_limits = [e for e in security_events['rate_limit'] if e > one_hour_ago]
    if len(recent_rate_limits) > ALERT_THRESHOLDS['rate_limits_per_hour']:
        await send_alert("High rate of push rate limiting detected")
    
    # Clean old events
    for event_type in security_events:
        security_events[event_type] = [
            e for e in security_events[event_type] if e > one_hour_ago
        ]
```

#### References

- [OWASP Logging Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Logging_Cheat_Sheet.html)
- [NIST SP 800-92 Guide to Computer Security Log Management](https://csrc.nist.gov/publications/detail/sp/800-92/final)

---

## Low Findings

### LOW-01: Expired Subscription Cleanup

**Severity**: Low (CVSS 3.5)
**OWASP**: A05:2021 - Security Misconfiguration

#### Description

Push subscriptions can become invalid over time. Push services return 410 Gone or 404 Not Found for expired subscriptions. These should be cleaned up to prevent:
- Wasted storage
- Unnecessary failed send attempts
- Accumulation of stale data

#### Impact

- Storage bloat
- Decreased notification delivery performance
- Log noise from failed sends

#### Remediation

**1. Implement cleanup for invalid subscriptions**

```python
async def cleanup_invalid_subscriptions():
    """Remove invalid subscriptions based on push service responses."""
    # Called when receiving 410 or 404 from push service
    pass

async def periodic_cleanup():
    """Periodic task to clean up old unused subscriptions."""
    # Remove subscriptions older than X days with no successful delivery
    pass
```

---

### LOW-02: Content Security Policy for Push

**Severity**: Low (CVSS 3.0)
**OWASP**: A05:2021 - Security Misconfiguration

#### Description

Service Workers and push event handlers should be served with appropriate Content Security Policy headers.

#### Remediation

**Add CSP headers for service worker and push endpoints**

```python
@server.after_request
async def add_security_headers(response):
    """Add security headers to responses."""
    if request.path == '/sw.js':
        response.headers['Content-Security-Policy'] = (
            "default-src 'self'; "
            "script-src 'self'; "
            "worker-src 'self';"
        )
    return response
```

---

## Summary Table

| ID | Severity | Finding | Classification | Action |
|----|----------|---------|----------------|--------|
| CRITICAL-01 | Critical (9.1) | VAPID private key storage | Blocking | Must fix before task completion |
| CRITICAL-02 | Critical (9.0) | Subscription endpoint exposure | Blocking | Must fix before task completion |
| HIGH-01 | High (7.5) | Rate limiting | Blocking | Implement in current task |
| HIGH-02 | High (7.5) | VAPID key separation | Blocking | Implement in current task |
| HIGH-03 | High (7.0) | Input validation | Blocking | Implement in current task |
| MEDIUM-01 | Medium (5.3) | Safari VAPID requirements | Related | Implement in current task |
| MEDIUM-02 | Medium (6.5) | Authentication requirements | Related | Implement in current task |
| MEDIUM-03 | Medium (5.0) | Audit logging | Related | Implement in current task |
| LOW-01 | Low (3.5) | Expired subscription cleanup | New | Add to backlog |
| LOW-02 | Low (3.0) | CSP headers | New | Add to backlog |

---

## Security Architecture Recommendations

### 1. Key Management Architecture

```
+------------------+     +-------------------+     +------------------+
| Secrets Manager  |     |   baseweb Server  |     |   Push Service   |
| (Vault/AWS SM)   |     |                   |     |                  |
|                  |---->| VAPID Key Cache   |---->| Validates JWT    |
| - Private Key    |     | - Public Key API  |     | - Delivers Push  |
| - Encryption Key |     | - JWT Generation  |     |                  |
+------------------+     +-------------------+     +------------------+
```

### 2. Subscription Storage Architecture

```
+------------------+     +-------------------+     +------------------+
|   Client (PWA)   |     |   baseweb Server  |     |   Database       |
|                  |     |                   |     |                  |
| Subscribe()      |---->| Validate          |---->| Store Encrypted  |
|                  |     | - Endpoint URL    |     | - User ID       |
|                  |     | - Keys format     |     | - Endpoint       |
|                  |     | - User auth       |     | - Encrypted keys |
|                  |     | - Rate limits      |     | - Audit trail    |
+------------------+     +-------------------+     +------------------+
```

### 3. Rate Limiting Architecture

```
+------------------+     +-------------------+     +------------------+
| Notification     |     |   Rate Limiter    |     |   Redis          |
| Request          |     |                   |     |                  |
|                  |---->| - Per user/hour    |<--->| - Counters       |
|                  |     | - Per app/minute   |     | - Sliding window |
|                  |     | - Global/second    |     | - TTL management |
+------------------+     +-------------------+     +------------------+
                                |
                                v
                         +------------------+
                         | Send/Deny Queue  |
                         +------------------+
```

---

## Implementation Priorities

### Phase 1: Critical Security (Must implement before task completion)

1. **VAPID Key Management**
   - Generate VAPID key pair
   - Store private key in environment variable/secrets manager
   - Never commit to version control
   - Implement public key endpoint for clients

2. **Subscription Security**
   - Require authentication for all subscription operations
   - Validate endpoint URLs against known push services
   - Implement CSRF protection
   - Associate subscriptions with authenticated users

3. **Input Validation**
   - Validate all subscription data fields
   - Sanitize user agent and IP addresses
   - Implement request size limits

### Phase 2: High Priority (Implement in current task)

4. **Rate Limiting**
   - Implement per-user rate limits (e.g., 10/day, 3/hour)
   - Implement per-application limits (e.g., 100/minute)
   - Use Redis for distributed rate limiting
   - Implement exponential backoff for retries

5. **VAPID Implementation**
   - Use separate keys for signing and content encryption
   - Implement Safari-compatible VAPID claims
   - Cache VAPID tokens appropriately
   - Handle Safari-specific error codes

### Phase 3: Medium Priority (Implement in current task)

6. **Audit Logging**
   - Log all subscription operations
   - Log all send operations with results
   - Log failed authentications
   - Implement security event alerting

7. **Authentication Integration**
   - Integrate with baseweb's existing authentication
   - Implement subscription ownership verification
   - Add user context to all operations

### Phase 4: Future Enhancements (Backlog)

8. **Subscription Cleanup**
   - Implement automatic cleanup of expired subscriptions
   - Handle 410 Gone and 404 Not Found responses
   - Add periodic cleanup task

9. **Security Headers**
   - Add Content-Security-Policy headers
   - Add additional security headers for Service Worker

---

## References

### Standards and Specifications
- [RFC 8292: VAPID for Web Push](https://rfc-editor.org/rfc/rfc8292.html)
- [RFC 8291: Message Encryption for Web Push](https://rfc-editor.org/rfc/rfc8291.html)
- [W3C Push API Specification](https://www.w3.org/TR/2025/WD-push-api-20251201/)
- [MDN Push API Documentation](https://developer.mozilla.org/en-US/docs/Web/API/Push_API)

### Browser-Specific Documentation
- [Apple Developer: Sending Web Push Notifications](https://developer.apple.com/documentation/usernotifications/sending_web_push_notifications_in_web_apps_safari_and_other_browsers)
- [WebKit Blog: Web Push for iOS](https://webkit.org/blog/13878/web-push-for-web-apps-on-ios-and-ipados)
- [Chrome Push Notification Rate Limits](https://developer.chrome.com/blog/web-push-rate-limits)

### Security Best Practices
- [OWASP Top 10:2021](https://owasp.org/Top10/)
- [OWASP Input Validation Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Input_Validation_Cheat_Sheet.html)
- [OWASP CSRF Prevention Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Cross-Site_Request_Forgery_Prevention_Cheat_Sheet.html)
- [GitGuardian: VAPID Key Security](https://docs.gitguardian.com/secrets-detection/secrets-detection-engine/detectors/specifics/vapid_key)
- [Spomky-Labs: Web Push Subscription Security](https://web-push.spomky-labs.com/common-concepts/the-subscription)

---

## Next Steps

1. **Create `analysis/security-push-notifications.md`** - This document
2. **Implement Phase 1 Critical Security** - Before any code deployment
3. **Implement Phase 2 High Priority** - During task-6.2 development
4. **Implement Phase 3 Medium Priority** - During task-6.2 development
5. **Add LOW-01 and LOW-02 to backlog** - For future sprint

---

*Security analysis completed: 2026-05-19*
*Analyzed by: Security Engineer Agent*