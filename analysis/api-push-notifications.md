# API Analysis: Push Notification Backend Infrastructure

**Created:** 2026-05-19
**Task:** task-6.2 - Push notification backend infrastructure
**Status:** Design

---

## Executive Summary

This document defines the RESTful API for push notification backend infrastructure in baseweb. The API follows RESTful design principles and provides endpoints for VAPID key management, push subscription storage, and notification delivery. The design prioritizes security, iOS Safari PWA compatibility, and graceful handling of expired subscriptions.

---

## Requirements Reference

| Requirement | Description |
|-------------|-------------|
| R85 | Backend VAPID key generation and management |
| R86 | Push subscription storage and retrieval |
| R87 | Push notification sending functionality |
| NFR3 | Push notification authentication uses VAPID keys securely |

---

## Architecture Overview

### Component Interaction

```
┌────────────────┐         ┌──────────────────┐         ┌─────────────────┐
│  Client (PWA)  │◄───────►│  baseweb API     │◄───────►│ Push Service    │
│                │         │                  │         │ (APNs/FCM/etc)  │
│  - Subscribe   │         │  - VAPID keys    │         │                 │
│  - Receive     │         │  - Subscriptions │         │                 │
└────────────────┘         │  - Send push    │         └─────────────────┘
                           └──────────────────┘
                                    │
                           ┌────────▼────────┐
                           │    Database     │
                           │  - VAPID keys   │
                           │  - Subscriptions│
                           └─────────────────┘
```

### Technology Stack

| Component | Technology | Purpose |
|-----------|------------|---------|
| VAPID Keys | py-vapid (Vapid01/Vapid) | Key generation and signing |
| Push Sending | pywebpush (webpush_async) | Async notification delivery |
| Database | Application-defined | Subscription and key storage |
| Encryption | ECDH (via pywebpush) | Payload encryption |

---

## API Design Principles

### RESTful Endpoints

All endpoints follow RESTful conventions:

| HTTP Method | Endpoint | Action |
|-------------|----------|--------|
| GET | `/api/vapid-public-key` | Retrieve public VAPID key |
| POST | `/api/push-subscriptions` | Create subscription |
| GET | `/api/push-subscriptions` | List user's subscriptions |
| DELETE | `/api/push-subscriptions/{id}` | Remove subscription |
| POST | `/api/push-notifications` | Send notification |

### Async-First Design

Following baseweb's async-first architecture:

- All endpoints use async handlers (`async def get(self): ...`)
- Push sending uses `webpush_async()` from pywebpush 2.1.0+
- Database operations should use async database drivers (asyncpg, motor, etc.)

---

## Data Models

### VAPID Key

VAPID keys identify the application server to push services. Each baseweb application should have at least one VAPID key pair.

```yaml
VAPIDKey:
  id: string (UUID)
  private_key: string (PEM or base64url-encoded DER)
  public_key: string (base64url-encoded, 65 bytes uncompressed)
  subject: string (mailto: or https: URL)
  created_at: datetime
  updated_at: datetime
  is_active: boolean
```

**Key Generation:**

```python
from py_vapid import Vapid01

vapid = Vapid01()
vapid.generate_keys()

# Store private key securely (PEM format)
private_key_pem = vapid.private_key_pem()

# Public key for clients (base64url-encoded)
public_key = vapid.public_key_pem()  # or .public_key_raw()
```

**Security Considerations:**
- Private keys must be stored securely (environment variables, secrets manager, encrypted database field)
- Never expose private keys via API
- Public key is safe to distribute to clients

### Push Subscription

Push subscriptions represent a user's device/browser registered to receive notifications.

```yaml
PushSubscription:
  id: string (UUID)
  user_id: string (foreign key to user, optional for anonymous)
  endpoint: string (URL from push service)
  keys:
    p256dh: string (client's ECDH public key, base64url)
    auth: string (client's auth secret, base64url)
  user_agent: string (browser identification)
  device_name: string (optional user-friendly name)
  created_at: datetime
  updated_at: datetime
  last_successful_push: datetime (optional)
  is_active: boolean
```

**Subscription Lifecycle:**

```
┌─────────┐     POST /push-subscriptions     ┌──────────────┐
│ Client  │ ───────────────────────────────► │   baseweb    │
│         │                                   │              │
│         │     Store subscription            │              │
│         │                                   │              │
│         │     POST /push-notifications      │              │
│         │ ◄─────────────────────────────────│              │
│         │     Push via endpoint             │              │
│         │                                   │              │
│         │     410/404 response              │              │
│         │ ◄─────────────────────────────────│              │
│         │     DELETE /push-subscriptions    │              │
│         │ ──────────────────────────────────►│              │
└─────────┘                                   └──────────────┘
```

---

## API Endpoints

### 1. GET /api/vapid-public-key

Retrieve the public VAPID key for client subscription.

**Request:**

```http
GET /api/vapid-public-key HTTP/1.1
Accept: application/json
```

**Response (200 OK):**

```json
{
  "public_key": "BH1x...your-public-key-here",
  "subject": "mailto:admin@example.com"
}
```

**Response (404 Not Found):**

```json
{
  "type": "https://api.baseweb.io/errors/vapid-not-configured",
  "title": "VAPID Not Configured",
  "status": 404,
  "detail": "VAPID keys have not been configured for this application."
}
```

**Design Notes:**
- Public endpoint (no authentication required)
- Returns the active VAPID public key
- Subject is included for client-side verification (optional)
- Should be cached by clients (keys don't change frequently)

**Implementation:**

```python
from baseweb import Resource
from quart import Response, json

class VAPIDPublicKeyResource(Resource):
    """Return the public VAPID key for client subscriptions."""
    
    async def get(self):
        """
        Get the active VAPID public key.
        
        Returns:
            JSON with public_key and subject fields
        """
        # Retrieve from storage (environment, database, etc.)
        vapid_key = await self._get_active_vapid_key()
        
        if vapid_key is None:
            return {
                "type": "https://api.baseweb.io/errors/vapid-not-configured",
                "title": "VAPID Not Configured",
                "status": 404,
                "detail": "VAPID keys have not been configured for this application."
            }, 404
        
        return {
            "public_key": vapid_key.public_key,
            "subject": vapid_key.subject
        }
    
    async def _get_active_vapid_key(self):
        """
        Retrieve the active VAPID key from storage.
        
        Override this method in your application to integrate
        with your key management system.
        """
        raise NotImplementedError(
            "Subclass must implement _get_active_vapid_key()"
        )
```

---

### 2. POST /api/push-subscriptions

Register a new push subscription for the authenticated user.

**Request:**

```http
POST /api/push-subscriptions HTTP/1.1
Content-Type: application/json
Authorization: Bearer <token>

{
  "endpoint": "https://fcm.googleapis.com/fcm/send/...",
  "keys": {
    "p256dh": "BDDzh...user-public-key",
    "auth": "GH2F...auth-secret"
  },
  "device_name": "iPhone 15 Pro",
  "user_agent": "Mozilla/5.0..."
}
```

**Request Body Schema:**

```yaml
PushSubscriptionCreate:
  endpoint:
    type: string
    format: uri
    required: true
    description: Push service endpoint URL from the browser
  keys:
    type: object
    required: true
    properties:
      p256dh:
        type: string
        format: base64url
        description: Client's ECDH public key
      auth:
        type: string
        format: base64url
        description: Client's auth secret
  device_name:
    type: string
    maxLength: 100
    description: User-friendly device name
  user_agent:
    type: string
    description: Browser user agent string
```

**Response (201 Created):**

```json
{
  "id": "sub_abc123",
  "endpoint": "https://fcm.googleapis.com/fcm/send/...",
  "device_name": "iPhone 15 Pro",
  "created_at": "2026-05-19T10:30:00Z",
  "is_active": true
}
```

**Response (400 Bad Request):**

```json
{
  "type": "https://api.baseweb.io/errors/invalid-subscription",
  "title": "Invalid Subscription",
  "status": 400,
  "detail": "Subscription endpoint is not a valid URL.",
  "field": "endpoint"
}
```

**Response (409 Conflict):**

```json
{
  "type": "https://api.baseweb.io/errors/subscription-exists",
  "title": "Subscription Already Exists",
  "status": 409,
  "detail": "This subscription is already registered."
}
```

**Response (401 Unauthorized):**

```json
{
  "type": "https://api.baseweb.io/errors/unauthorized",
  "title": "Unauthorized",
  "status": 401,
  "detail": "Authentication required to register subscriptions."
}
```

**Security Considerations:**
- Requires authentication (user must be logged in)
- Validate endpoint URL is from a known push service
- Rate limit subscriptions per user to prevent abuse
- Check for duplicate subscriptions by endpoint

**Implementation:**

```python
import json
from datetime import datetime
from baseweb import Resource
from quart import request

class PushSubscriptionResource(Resource):
    """Manage push subscriptions."""
    
    async def post(self):
        """
        Register a new push subscription.
        
        Request body:
            endpoint: Push service URL
            keys: { p256dh: str, auth: str }
            device_name: Optional user-friendly name
            user_agent: Optional browser identification
        
        Returns:
            201: Created subscription
            400: Invalid subscription data
            409: Subscription already exists
            401: Authentication required
        """
        # Get authenticated user
        user_id = await self._get_current_user_id()
        if user_id is None:
            return {
                "type": "https://api.baseweb.io/errors/unauthorized",
                "title": "Unauthorized",
                "status": 401,
                "detail": "Authentication required to register subscriptions."
            }, 401
        
        # Parse and validate request
        data = await request.get_json()
        
        # Validate required fields
        if not data.get("endpoint"):
            return {
                "type": "https://api.baseweb.io/errors/invalid-subscription",
                "title": "Invalid Subscription",
                "status": 400,
                "detail": "Subscription endpoint is required.",
                "field": "endpoint"
            }, 400
        
        if not data.get("keys", {}).get("p256dh") or not data.get("keys", {}).get("auth"):
            return {
                "type": "https://api.baseweb.io/errors/invalid-subscription",
                "title": "Invalid Subscription",
                "status": 400,
                "detail": "Both p256dh and auth keys are required."
            }, 400
        
        # Check for duplicate
        existing = await self._find_subscription_by_endpoint(data["endpoint"])
        if existing:
            return {
                "type": "https://api.baseweb.io/errors/subscription-exists",
                "title": "Subscription Already Exists",
                "status": 409,
                "detail": "This subscription is already registered.",
                "subscription_id": existing["id"]
            }, 409
        
        # Store subscription
        subscription = await self._create_subscription(
            user_id=user_id,
            endpoint=data["endpoint"],
            p256dh=data["keys"]["p256dh"],
            auth=data["keys"]["auth"],
            device_name=data.get("device_name"),
            user_agent=data.get("user_agent", request.user_agent.string)
        )
        
        return {
            "id": subscription["id"],
            "endpoint": subscription["endpoint"],
            "device_name": subscription.get("device_name"),
            "created_at": subscription["created_at"],
            "is_active": True
        }, 201
    
    async def _get_current_user_id(self):
        """Get the authenticated user ID. Override in your app."""
        raise NotImplementedError(
            "Subclass must implement _get_current_user_id()"
        )
    
    async def _find_subscription_by_endpoint(self, endpoint):
        """Find existing subscription by endpoint. Override in your app."""
        raise NotImplementedError(
            "Subclass must implement _find_subscription_by_endpoint()"
        )
    
    async def _create_subscription(self, user_id, endpoint, p256dh, auth, 
                                    device_name, user_agent):
        """Create a new subscription. Override in your app."""
        raise NotImplementedError(
            "Subclass must implement _create_subscription()"
        )
```

---

### 3. GET /api/push-subscriptions

List all push subscriptions for the authenticated user.

**Request:**

```http
GET /api/push-subscriptions HTTP/1.1
Accept: application/json
Authorization: Bearer <token>
```

**Query Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `limit` | integer | 20 | Maximum results per page (max 100) |
| `cursor` | string | null | Pagination cursor for next page |
| `is_active` | boolean | null | Filter by active status |

**Response (200 OK):**

```json
{
  "data": [
    {
      "id": "sub_abc123",
      "endpoint": "https://fcm.googleapis.com/fcm/send/...",
      "device_name": "iPhone 15 Pro",
      "user_agent": "Mozilla/5.0 (iPhone...)",
      "created_at": "2026-05-19T10:30:00Z",
      "last_successful_push": "2026-05-19T12:00:00Z",
      "is_active": true
    },
    {
      "id": "sub_def456",
      "endpoint": "https://updates.push.services.mozilla.com/...",
      "device_name": "Firefox Desktop",
      "user_agent": "Mozilla/5.0 (Windows...)",
      "created_at": "2026-05-18T14:00:00Z",
      "last_successful_push": null,
      "is_active": true
    }
  ],
  "pagination": {
    "next_cursor": "eyJpZCI6InN1Yl9kZWY0NTYifQ",
    "has_more": false
  }
}
```

**Response (401 Unauthorized):**

```json
{
  "type": "https://api.baseweb.io/errors/unauthorized",
  "title": "Unauthorized",
  "status": 401,
  "detail": "Authentication required."
}
```

**Implementation:**

```python
from baseweb import Resource
from quart import request

class PushSubscriptionListResource(Resource):
    """List push subscriptions for authenticated user."""
    
    async def get(self):
        """
        List subscriptions for the current user.
        
        Query params:
            limit: Max results (default 20, max 100)
            cursor: Pagination cursor
            is_active: Filter by active status
        
        Returns:
            200: List of subscriptions
            401: Authentication required
        """
        user_id = await self._get_current_user_id()
        if user_id is None:
            return {
                "type": "https://api.baseweb.io/errors/unauthorized",
                "title": "Unauthorized",
                "status": 401,
                "detail": "Authentication required."
            }, 401
        
        # Parse query parameters
        limit = min(int(request.args.get("limit", 20)), 100)
        cursor = request.args.get("cursor")
        is_active = request.args.get("is_active")
        
        if is_active is not None:
            is_active = is_active.lower() == "true"
        
        subscriptions, next_cursor = await self._list_subscriptions(
            user_id=user_id,
            limit=limit,
            cursor=cursor,
            is_active=is_active
        )
        
        return {
            "data": subscriptions,
            "pagination": {
                "next_cursor": next_cursor,
                "has_more": next_cursor is not None
            }
        }
    
    async def _get_current_user_id(self):
        """Override in your application."""
        raise NotImplementedError()
    
    async def _list_subscriptions(self, user_id, limit, cursor, is_active):
        """Override in your application."""
        raise NotImplementedError()
```

---

### 4. DELETE /api/push-subscriptions/{id}

Remove a push subscription.

**Request:**

```http
DELETE /api/push-subscriptions/sub_abc123 HTTP/1.1
Authorization: Bearer <token>
```

**Response (204 No Content):**

Empty body with 204 status code.

**Response (404 Not Found):**

```json
{
  "type": "https://api.baseweb.io/errors/subscription-not-found",
  "title": "Subscription Not Found",
  "status": 404,
  "detail": "Subscription sub_abc123 does not exist or you do not have access."
}
```

**Response (401 Unauthorized):**

```json
{
  "type": "https://api.baseweb.io/errors/unauthorized",
  "title": "Unauthorized",
  "status": 401,
  "detail": "Authentication required."
}
```

**Security Considerations:**
- Users can only delete their own subscriptions
- Returns 404 for non-existent or non-owned subscriptions (same error to prevent enumeration)

**Implementation:**

```python
from baseweb import Resource

class PushSubscriptionDetailResource(Resource):
    """Manage individual push subscription."""
    
    async def delete(self, subscription_id):
        """
        Delete a push subscription.
        
        Path params:
            subscription_id: Subscription ID to delete
        
        Returns:
            204: Deleted successfully
            401: Authentication required
            404: Subscription not found
        """
        user_id = await self._get_current_user_id()
        if user_id is None:
            return {
                "type": "https://api.baseweb.io/errors/unauthorized",
                "title": "Unauthorized",
                "status": 401,
                "detail": "Authentication required."
            }, 401
        
        # Find and verify ownership
        subscription = await self._find_subscription(subscription_id)
        
        if subscription is None or subscription["user_id"] != user_id:
            # Return same error for not found and not owned
            return {
                "type": "https://api.baseweb.io/errors/subscription-not-found",
                "title": "Subscription Not Found",
                "status": 404,
                "detail": f"Subscription {subscription_id} does not exist or you do not have access."
            }, 404
        
        # Delete subscription
        await self._delete_subscription(subscription_id)
        
        return None, 204
    
    async def _get_current_user_id(self):
        """Override in your application."""
        raise NotImplementedError()
    
    async def _find_subscription(self, subscription_id):
        """Override in your application."""
        raise NotImplementedError()
    
    async def _delete_subscription(self, subscription_id):
        """Override in your application."""
        raise NotImplementedError()
```

---

### 5. POST /api/push-notifications

Send a push notification to one or more subscriptions.

**Request:**

```http
POST /api/push-notifications HTTP/1.1
Content-Type: application/json
Authorization: Bearer <admin-token>

{
  "subscription_ids": ["sub_abc123", "sub_def456"],
  "title": "New Message",
  "body": "You have a new message from John",
  "icon": "/static/images/icons/icon-192x192.png",
  "badge": "/static/images/icons/badge-72x72.png",
  "url": "/messages/123",
  "actions": [
    {"action": "open", "title": "Open"},
    {"action": "dismiss", "title": "Dismiss"}
  ],
  "tag": "message-notification",
  "require_interaction": false,
  "ttl": 86400
}
```

**Request Body Schema:**

```yaml
PushNotificationCreate:
  subscription_ids:
    type: array
    items:
      type: string
    required: true
    description: List of subscription IDs to send to
  title:
    type: string
    required: true
    maxLength: 50
    description: Notification title
  body:
    type: string
    required: true
    maxLength: 200
    description: Notification body text
  icon:
    type: string
    format: uri
    description: URL for notification icon (192x192 recommended)
  badge:
    type: string
    format: uri
    description: URL for notification badge (72x72 for Android)
  url:
    type: string
    description: URL to open when notification is clicked
  actions:
    type: array
    items:
      type: object
      properties:
        action: string
        title: string
        icon: string (optional)
    description: Action buttons for notification
  tag:
    type: string
    description: Tag to group notifications (newer replaces older)
  require_interaction:
    type: boolean
    default: false
    description: Keep notification until user interacts
  ttl:
    type: integer
    minimum: 0
    maximum: 2592000
    default: 86400
    description: Time-to-live in seconds (0 = immediate, max 30 days)
  urgency:
    type: string
    enum: [very-low, low, normal, high]
    default: normal
    description: Delivery urgency hint
```

**Response (202 Accepted):**

```json
{
  "notification_id": "notif_xyz789",
  "status": "processing",
  "subscription_count": 2,
  "created_at": "2026-05-19T14:00:00Z",
  "_links": {
    "self": "/api/push-notifications/notif_xyz789"
  }
}
```

**Response (400 Bad Request):**

```json
{
  "type": "https://api.baseweb.io/errors/invalid-notification",
  "title": "Invalid Notification",
  "status": 400,
  "detail": "Notification body exceeds 200 character limit.",
  "field": "body"
}
```

**Response (401 Unauthorized):**

```json
{
  "type": "https://api.baseweb.io/errors/unauthorized",
  "title": "Unauthorized",
  "status": 401,
  "detail": "Authentication required."
}
```

**Response (403 Forbidden):**

```json
{
  "type": "https://api.baseweb.io/errors/forbidden",
  "title": "Forbidden",
  "status": 403,
  "detail": "You do not have permission to send push notifications."
}
```

**Design Notes:**
- Returns 202 Accepted because push sending is async
- Use background task to send notifications
- Track delivery status per subscription
- Handle expired subscriptions gracefully (410/404 from push service)

**Implementation:**

```python
import json
from datetime import datetime
from baseweb import Resource
from quart import request
from pywebpush import webpush_async

class PushNotificationResource(Resource):
    """Send push notifications."""
    
    async def post(self):
        """
        Send a push notification.
        
        Request body:
            subscription_ids: List of subscription IDs
            title: Notification title
            body: Notification body
            icon: Optional icon URL
            badge: Optional badge URL
            url: Optional click URL
            actions: Optional action buttons
            tag: Optional notification tag
            require_interaction: Optional, default false
            ttl: Time-to-live in seconds, default 86400
            urgency: Optional urgency hint
        
        Returns:
            202: Notification queued for sending
            400: Invalid notification data
            401: Authentication required
            403: Permission denied
        """
        # Verify admin/sender permission
        if not await self._can_send_notifications():
            return {
                "type": "https://api.baseweb.io/errors/forbidden",
                "title": "Forbidden",
                "status": 403,
                "detail": "You do not have permission to send push notifications."
            }, 403
        
        # Parse and validate request
        data = await request.get_json()
        
        # Validate required fields
        if not data.get("subscription_ids"):
            return {
                "type": "https://api.baseweb.io/errors/invalid-notification",
                "title": "Invalid Notification",
                "status": 400,
                "detail": "At least one subscription_id is required."
            }, 400
        
        if not data.get("title") or not data.get("body"):
            return {
                "type": "https://api.baseweb.io/errors/invalid-notification",
                "title": "Invalid Notification",
                "status": 400,
                "detail": "Both title and body are required."
            }, 400
        
        # Validate lengths (Safari has 2KB payload limit)
        if len(data["title"]) > 50:
            return {
                "type": "https://api.baseweb.io/errors/invalid-notification",
                "title": "Invalid Notification",
                "status": 400,
                "detail": "Notification title exceeds 50 character limit.",
                "field": "title"
            }, 400
        
        if len(data["body"]) > 200:
            return {
                "type": "https://api.baseweb.io/errors/invalid-notification",
                "title": "Invalid Notification",
                "status": 400,
                "detail": "Notification body exceeds 200 character limit.",
                "field": "body"
            }, 400
        
        # Create notification record
        notification_id = await self._create_notification(
            subscription_ids=data["subscription_ids"],
            payload={
                "title": data["title"],
                "body": data["body"],
                "icon": data.get("icon"),
                "badge": data.get("badge"),
                "url": data.get("url"),
                "actions": data.get("actions", []),
                "tag": data.get("tag"),
                "require_interaction": data.get("require_interaction", False)
            },
            ttl=data.get("ttl", 86400),
            urgency=data.get("urgency", "normal")
        )
        
        # Queue background task to send notifications
        await self._queue_notification_task(notification_id)
        
        return {
            "notification_id": notification_id,
            "status": "processing",
            "subscription_count": len(data["subscription_ids"]),
            "created_at": datetime.utcnow().isoformat() + "Z",
            "_links": {
                "self": f"/api/push-notifications/{notification_id}"
            }
        }, 202
    
    async def _can_send_notifications(self):
        """Check if current user can send notifications. Override in your app."""
        raise NotImplementedError()
    
    async def _create_notification(self, subscription_ids, payload, ttl, urgency):
        """Create notification record. Override in your app."""
        raise NotImplementedError()
    
    async def _queue_notification_task(self, notification_id):
        """Queue background task. Override in your app."""
        raise NotImplementedError()


class PushNotificationSender:
    """Background worker for sending push notifications."""
    
    async def send_notification(self, subscription, payload, vapid_key):
        """
        Send a push notification to a single subscription.
        
        Args:
            subscription: PushSubscription dict with endpoint and keys
            payload: Dict with title, body, etc.
            vapid_key: VAPIDKey dict with private_key and subject
        
        Returns:
            True if sent successfully, False if subscription is expired
        
        Raises:
            Exception: On transient errors (retry later)
        """
        try:
            response = await webpush_async(
                subscription_info={
                    "endpoint": subscription["endpoint"],
                    "keys": {
                        "p256dh": subscription["p256dh"],
                        "auth": subscription["auth"]
                    }
                },
                data=json.dumps(payload),
                vapid_private_key=vapid_key["private_key"],
                vapid_claims={
                    "sub": vapid_key["subject"]
                },
                ttl=86400  # 24 hours default
            )
            return True
        
        except Exception as error:
            # Check for permanent failures
            if hasattr(error, 'status_code'):
                if error.status_code in (404, 410):
                    # Subscription expired/invalid
                    await self._mark_subscription_expired(subscription["id"])
                    return False
            
            # Transient error - log and re-raise
            await self._log_push_error(subscription["id"], str(error))
            raise
    
    async def _mark_subscription_expired(self, subscription_id):
        """Mark subscription as inactive. Override in your app."""
        raise NotImplementedError()
    
    async def _log_push_error(self, subscription_id, error):
        """Log push error. Override in your app."""
        raise NotImplementedError()
```

---

## VAPID Key Management

### Key Storage Options

| Option | Security | Ease of Use | Use Case |
|--------|----------|-------------|----------|
| Environment Variables | Medium | Easy | Development, simple apps |
| Secrets Manager | High | Medium | Production, cloud deployments |
| Encrypted Database | High | Medium | Multi-tenant apps |
| File System (PEM) | Low-Medium | Easy | Development only |

### Recommended Pattern for baseweb

```python
import os
from pathlib import Path
from py_vapid import Vapid01

class VAPIDKeyManager:
    """Manage VAPID keys for the application."""
    
    def __init__(self, storage_backend=None):
        self.storage = storage_backend or EnvironmentVAPIDStorage()
        self._vapid_instance = None
    
    async def get_or_create_keys(self):
        """
        Get existing VAPID keys or generate new ones.
        
        Returns:
            Dict with private_key, public_key, and subject
        """
        if self._vapid_instance:
            return self._vapid_instance
        
        # Try to load existing keys
        private_key = await self.storage.load_private_key()
        
        if private_key:
            self._vapid_instance = Vapid01.from_pem(private_key)
        else:
            # Generate new keys
            self._vapid_instance = Vapid01()
            self._vapid_instance.generate_keys()
            
            # Save to storage
            await self.storage.save_private_key(
                self._vapid_instance.private_key_pem()
            )
        
        return self._vapid_instance
    
    def get_public_key(self):
        """Get the public key for client distribution."""
        if not self._vapid_instance:
            raise RuntimeError("Keys not initialized. Call get_or_create_keys() first.")
        return self._vapid_instance.public_key_pem()
    
    def get_vapid_claims(self, audience=None):
        """
        Generate VAPID claims for signing.
        
        Args:
            audience: Push service URL (auto-detected if not provided)
        
        Returns:
            Dict with sub, aud, and exp claims
        """
        import time
        
        return {
            "sub": self.storage.get_subject(),
            "aud": audience,  # Will be auto-filled by pywebpush if None
            "exp": int(time.time()) + 12 * 60 * 60  # 12 hours
        }


class EnvironmentVAPIDStorage:
    """Store VAPID keys in environment variables."""
    
    def __init__(self):
        self.subject = os.environ.get(
            "VAPID_SUBJECT",
            "mailto:admin@localhost"
        )
    
    async def load_private_key(self):
        """Load private key from environment."""
        key = os.environ.get("VAPID_PRIVATE_KEY")
        if key and Path(key).is_file():
            # It's a file path
            return Path(key).read_text()
        return key
    
    async def save_private_key(self, key_pem):
        """
        Save private key (not recommended for env vars).
        
        This method logs a warning because env vars should be
        set externally, not modified at runtime.
        """
        import logging
        logging.warning(
            "Cannot save VAPID key to environment. "
            "Set VAPID_PRIVATE_KEY environment variable manually."
        )
    
    def get_subject(self):
        """Get the VAPID subject (contact email/URL)."""
        return self.subject


class FileVAPIDStorage:
    """Store VAPID keys in files."""
    
    def __init__(self, private_key_path="vapid_private.pem", 
                 public_key_path="vapid_public.pem"):
        self.private_key_path = Path(private_key_path)
        self.public_key_path = Path(public_key_path)
        self.subject = os.environ.get(
            "VAPID_SUBJECT",
            "mailto:admin@localhost"
        )
    
    async def load_private_key(self):
        """Load private key from file."""
        if not self.private_key_path.exists():
            return None
        return self.private_key_path.read_text()
    
    async def save_private_key(self, key_pem):
        """Save private key to file."""
        self.private_key_path.write_text(key_pem)
        # Set restrictive permissions
        self.private_key_path.chmod(0o600)
    
    def get_subject(self):
        return self.subject
```

---

## Security Considerations

### VAPID Key Security

| Threat | Mitigation |
|--------|-------------|
| Private key exposure | Store in secrets manager, never in code |
| Key rotation | Generate new key, migrate subscriptions |
| Key theft | Use encrypted storage, audit access |

### Subscription Security

| Threat | Mitigation |
|--------|-------------|
| Unauthorized registration | Require authentication, rate limit |
| Subscription enumeration | Use UUIDs, return 404 for not-owned |
| Replay attacks | Validate endpoint authenticity |

### Notification Security

| Threat | Mitigation |
|--------|-------------|
| Spam/abuse | Rate limit per user, admin-only sending |
| Large payloads | Validate size (Safari: 2KB, Chrome: 4KB) |
| Expired subscriptions | Handle 410/404, mark inactive |

### Implementation Checklist

- [ ] VAPID private keys stored in secrets manager or encrypted storage
- [ ] Public key endpoint has no authentication requirement
- [ ] Subscription registration requires authentication
- [ ] Notification sending requires admin/sender permission
- [ ] Rate limiting on subscription registration (prevent abuse)
- [ ] Rate limiting on notification sending (prevent spam)
- [ ] Expired subscriptions marked inactive (410/404 responses)
- [ ] Payload size validation before sending
- [ ] HTTPS enforced for all endpoints
- [ ] CORS configured for client origin only

---

## iOS Safari PWA Requirements

### Platform Constraints

| Requirement | Details |
|-------------|---------|
| iOS Version | 16.4+ |
| Browser | Safari only (not Chrome/Firefox on iOS) |
| Installation | Must be installed as PWA (added to home screen) |
| Permission | User gesture required (button click) |
| Encryption | VAPID required (no legacy keys) |

### Subscription Flow for iOS

```
1. User opens Safari
2. User taps "Share" → "Add to Home Screen"
3. User launches PWA from home screen
4. User taps "Enable Notifications" button (user gesture)
5. Browser shows permission prompt
6. User grants permission
7. Service Worker registers push subscription
8. POST /api/push-subscriptions with subscription
9. Server stores subscription
10. Push notifications can be sent
```

### Client-Side Requirements

```javascript
// Check iOS PWA requirements
function canUsePushNotifications() {
  // Check for Push API support
  if (!('PushManager' in window)) {
    return { supported: false, reason: 'Push API not supported' };
  }
  
  // Check for Service Worker support
  if (!('serviceWorker' in navigator)) {
    return { supported: false, reason: 'Service Worker not supported' };
  }
  
  // Check if running as PWA on iOS
  const isIOS = /iPad|iPhone|iPod/.test(navigator.userAgent);
  const isStandalone = window.matchMedia('(display-mode: standalone)').matches 
                    || window.navigator.standalone === true;
  
  if (isIOS && !isStandalone) {
    return { 
      supported: false, 
      reason: 'iOS requires PWA installation. Add to home screen first.' 
    };
  }
  
  // Check iOS version
  if (isIOS) {
    const iOSVersion = parseFloat(
      ('' + (/CPU.*OS ([0-9_]+)/.exec(navigator.userAgent) || [0,''])[1])
        .replace('_', '.')
    );
    if (iOSVersion < 16.4) {
      return { 
        supported: false, 
        reason: 'iOS 16.4+ required for push notifications' 
      };
    }
  }
  
  return { supported: true };
}

// Subscribe to push notifications
async function subscribeToPush(vapidPublicKey) {
  // Check support
  const check = canUsePushNotifications();
  if (!check.supported) {
    throw new Error(check.reason);
  }
  
  // Request permission (must be from user gesture)
  const permission = await Notification.requestPermission();
  if (permission !== 'granted') {
    throw new Error('Notification permission denied');
  }
  
  // Register service worker
  const registration = await navigator.serviceWorker.ready;
  
  // Subscribe
  const subscription = await registration.pushManager.subscribe({
    userVisibleOnly: true,
    applicationServerKey: urlBase64ToUint8Array(vapidPublicKey)
  });
  
  // Send to server
  const response = await fetch('/api/push-subscriptions', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      endpoint: subscription.endpoint,
      keys: {
        p256dh: btoa(String.fromCharCode(...new Uint8Array(subscription.getKey('p256dh')))),
        auth: btoa(String.fromCharCode(...new Uint8Array(subscription.getKey('auth'))))
      },
      device_name: navigator.userAgent,
      user_agent: navigator.userAgent
    })
  });
  
  return response.json();
}

// Helper to convert VAPID key
function urlBase64ToUint8Array(base64String) {
  const padding = '='.repeat((4 - base64String.length % 4) % 4);
  const base64 = (base64String + padding)
    .replace(/-/g, '+')
    .replace(/_/g, '/');
  const rawData = window.atob(base64);
  const outputArray = new Uint8Array(rawData.length);
  for (let i = 0; i < rawData.length; ++i) {
    outputArray[i] = rawData.charCodeAt(i);
  }
  return outputArray;
}
```

---

## Dependencies

### Required Python Packages

```toml
[project.dependencies]
py-vapid = ">=1.9.0"
pywebpush = ">=2.1.0"

# Optional async database drivers (choose based on your database)
# asyncpg = ">=0.28.0"  # PostgreSQL
# motor = ">=3.3.0"      # MongoDB
# aiosqlite = ">=0.19.0" # SQLite
```

### pywebpush Version Requirements

**Minimum:** pywebpush 2.1.0+ (for `webpush_async()` function)

Earlier versions require using aiohttp directly or running sync code in a thread.

---

## Testing Strategy

### Unit Tests

| Test | Description |
|------|-------------|
| VAPID key generation | Generate and validate key pairs |
| VAPID claims signing | Verify JWT token generation |
| Subscription validation | Validate endpoint and keys |
| Payload validation | Verify size limits, required fields |
| Expired subscription handling | Mock 410/404 responses |

### Integration Tests

| Test | Description |
|------|-------------|
| End-to-end subscription flow | Client → API → Database |
| End-to-end notification flow | API → Push Service → Client |
| Error handling | Invalid data, auth failures |
| Rate limiting | Verify rate limits enforced |

### Mock Push Service

For testing without real push services:

```python
import pytest
from unittest.mock import AsyncMock, patch

@pytest.mark.asyncio
async def test_send_notification():
    """Test sending notification with mocked push service."""
    
    with patch('pywebpush.webpush_async', new_callable=AsyncMock) as mock_push:
        mock_push.return_value.status_code = 201
        
        # Call notification sender
        result = await send_notification(
            subscription={
                "endpoint": "https://example.com/push/123",
                "keys": {"p256dh": "...", "auth": "..."}
            },
            payload={"title": "Test", "body": "Message"},
            vapid_key={
                "private_key": "...",
                "subject": "mailto:test@example.com"
            }
        )
        
        assert result is True
        mock_push.assert_called_once()
```

---

## OpenAPI Specification (Partial)

```yaml
openapi: 3.1.0
info:
  title: Baseweb Push Notification API
  version: 1.0.0
  description: Push notification backend API for PWA applications

servers:
  - url: https://api.example.com/api
    description: Production

paths:
  /vapid-public-key:
    get:
      tags: [VAPID]
      summary: Get public VAPID key
      operationId: getVAPIDPublicKey
      responses:
        '200':
          description: Public VAPID key
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/VAPIDPublicKey'
        '404':
          description: VAPID not configured
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Error'

  /push-subscriptions:
    post:
      tags: [Subscriptions]
      summary: Register push subscription
      operationId: createPushSubscription
      security:
        - bearerAuth: []
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/PushSubscriptionCreate'
      responses:
        '201':
          description: Subscription created
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/PushSubscription'
        '400':
          description: Invalid subscription
        '401':
          description: Unauthorized
        '409':
          description: Subscription already exists
    
    get:
      tags: [Subscriptions]
      summary: List user subscriptions
      operationId: listPushSubscriptions
      security:
        - bearerAuth: []
      parameters:
        - name: limit
          in: query
          schema:
            type: integer
            minimum: 1
            maximum: 100
            default: 20
        - name: cursor
          in: query
          schema:
            type: string
        - name: is_active
          in: query
          schema:
            type: boolean
      responses:
        '200':
          description: List of subscriptions
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/PushSubscriptionList'
        '401':
          description: Unauthorized

  /push-subscriptions/{id}:
    delete:
      tags: [Subscriptions]
      summary: Delete subscription
      operationId: deletePushSubscription
      security:
        - bearerAuth: []
      parameters:
        - name: id
          in: path
          required: true
          schema:
            type: string
      responses:
        '204':
          description: Subscription deleted
        '401':
          description: Unauthorized
        '404':
          description: Subscription not found

  /push-notifications:
    post:
      tags: [Notifications]
      summary: Send push notification
      operationId: sendPushNotification
      security:
        - bearerAuth: []
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/PushNotificationCreate'
      responses:
        '202':
          description: Notification queued
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/PushNotificationResponse'
        '400':
          description: Invalid notification
        '401':
          description: Unauthorized
        '403':
          description: Forbidden

components:
  schemas:
    VAPIDPublicKey:
      type: object
      required: [public_key]
      properties:
        public_key:
          type: string
          description: Base64url-encoded public VAPID key
        subject:
          type: string
          format: uri
          description: Contact email or URL

    PushSubscriptionCreate:
      type: object
      required: [endpoint, keys]
      properties:
        endpoint:
          type: string
          format: uri
          description: Push service endpoint URL
        keys:
          type: object
          required: [p256dh, auth]
          properties:
            p256dh:
              type: string
              description: Client's ECDH public key (base64url)
            auth:
              type: string
              description: Auth secret (base64url)
        device_name:
          type: string
          maxLength: 100
          description: User-friendly device name
        user_agent:
          type: string
          description: Browser user agent

    PushSubscription:
      type: object
      properties:
        id:
          type: string
        endpoint:
          type: string
        device_name:
          type: string
        user_agent:
          type: string
        created_at:
          type: string
          format: date-time
        last_successful_push:
          type: string
          format: date-time
        is_active:
          type: boolean

    PushSubscriptionList:
      type: object
      properties:
        data:
          type: array
          items:
            $ref: '#/components/schemas/PushSubscription'
        pagination:
          type: object
          properties:
            next_cursor:
              type: string
            has_more:
              type: boolean

    PushNotificationCreate:
      type: object
      required: [subscription_ids, title, body]
      properties:
        subscription_ids:
          type: array
          items:
            type: string
          description: List of subscription IDs
        title:
          type: string
          maxLength: 50
        body:
          type: string
          maxLength: 200
        icon:
          type: string
          format: uri
        badge:
          type: string
          format: uri
        url:
          type: string
        actions:
          type: array
          items:
            type: object
            properties:
              action:
                type: string
              title:
                type: string
              icon:
                type: string
        tag:
          type: string
        require_interaction:
          type: boolean
          default: false
        ttl:
          type: integer
          minimum: 0
          maximum: 2592000
          default: 86400
        urgency:
          type: string
          enum: [very-low, low, normal, high]
          default: normal

    PushNotificationResponse:
      type: object
      properties:
        notification_id:
          type: string
        status:
          type: string
          enum: [processing, sent, failed]
        subscription_count:
          type: integer
        created_at:
          type: string
          format: date-time

    Error:
      type: object
      required: [type, title, status]
      properties:
        type:
          type: string
          format: uri
          description: Error type identifier
        title:
          type: string
          description: Human-readable error title
        status:
          type: integer
          description: HTTP status code
        detail:
          type: string
          description: Detailed error message
        field:
          type: string
          description: Field that caused the error

  securitySchemes:
    bearerAuth:
      type: http
      scheme: bearer
      bearerFormat: JWT
```

---

## Implementation Roadmap

### Phase 1: Core Infrastructure (Estimated: 2-3 days)

| Task | Effort |
|------|--------|
| Add py-vapid and pywebpush dependencies | 0.5 day |
| Create VAPIDKeyManager with environment storage | 1 day |
| Implement VAPIDPublicKeyResource | 0.5 day |
| Unit tests for VAPID management | 0.5 day |

### Phase 2: Subscription Management (Estimated: 2-3 days)

| Task | Effort |
|------|--------|
| Create PushSubscription data model | 0.5 day |
| Implement PushSubscriptionResource (POST) | 1 day |
| Implement PushSubscriptionListResource (GET) | 0.5 day |
| Implement PushSubscriptionDetailResource (DELETE) | 0.5 day |
| Integration tests for subscription flow | 1 day |

### Phase 3: Notification Sending (Estimated: 2-3 days)

| Task | Effort |
|------|--------|
| Implement PushNotificationResource (POST) | 1 day |
| Create PushNotificationSender background worker | 1 day |
| Handle expired subscriptions (410/404) | 0.5 day |
| Integration tests for notification flow | 1 day |

### Phase 4: Documentation & Examples (Estimated: 1 day)

| Task | Effort |
|------|--------|
| Create hello-world example with push | 0.5 day |
| Document API endpoints | 0.5 day |

---

## Action Items

1. **Add dependencies to pyproject.toml**
   - py-vapid >= 1.9.0
   - pywebpush >= 2.1.0

2. **Create baseweb.push module**
   - `vapid.py` - VAPID key management
   - `subscriptions.py` - Subscription storage interface
   - `notifications.py` - Notification sending
   - `resources.py` - Quart Resource classes

3. **Implement database abstraction**
   - Define interface for subscription storage
   - Provide in-memory implementation for testing
   - Document integration with user database

4. **Create example integration**
   - Add push notification example to hello-world app
   - Document client-side integration (Service Worker)
   - Document iOS PWA setup requirements

5. **Add tests**
   - Unit tests for VAPID key management
   - Unit tests for payload validation
   - Integration tests for subscription flow
   - Mock push service tests

---

## Sources

- [Implementing Push Notifications with the Web Push API](https://blog.openreplay.com/implementing-push-notifications-web-push-api/)
- [Sending web push notifications in web apps and browsers - Apple Developer Documentation](https://developer.apple.com/documentation/usernotifications/sending-web-push-notifications-in-web-apps-and-browsers)
- [web-push-libs/pywebpush - GitHub](https://github.com/web-push-libs/pywebpush)
- [Add async_webpush one call func - PR #177](https://github.com/web-push-libs/pywebpush/pull/177)
- [py-vapid on PyPI](https://pypi.org/project/py-vapid/)
- [web-push-libs/vapid - GitHub](https://github.com/web-push-libs/vapid/tree/main/python)