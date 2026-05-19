# Push Notifications Guide for Baseweb PWAs

This guide explains the complete setup for push notifications in a Baseweb Progressive Web App (PWA). We'll use a chat application as the example use case.

## Overview

**Use Case:** A chat application PWA that:
1. Gets installed on the user's home screen
2. Requests permission for push notifications
3. Receives push notifications when new messages arrive
4. Updates the app badge with unread message count

### Architecture Overview

The push notification system involves multiple components working together:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              PUSH NOTIFICATION FLOW                         │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌──────────────┐     ┌──────────────┐     ┌──────────────┐              │
│  │   PWA App    │     │   Service    │     │   Browser    │              │
│  │   (Vue.js)   │────▶│   Worker     │────▶│   Push API   │              │
│  │              │     │   (sw.js)    │     │              │              │
│  └──────────────┘     └──────────────┘     └──────┬───────┘              │
│         │                                          │                       │
│         │                                          │                       │
│         ▼                                          ▼                       │
│  ┌──────────────┐                        ┌──────────────────┐             │
│  │   Subscribe │                        │   Push Service   │             │
│  │   Button    │                        │   (FCM/APNs/     │             │
│  │              │                        │    Mozilla)      │             │
│  └──────────────┘                        └────────┬─────────┘             │
│                                                   │                        │
│                                                   │                        │
│  ┌───────────────────────────────────────────────┼────────────────────┐  │
│  │                      BACKEND                   │                    │  │
│  │  ┌──────────────┐     ┌──────────────┐       │                    │  │
│  │  │   VAPID      │     │   Push       │◀──────┘                    │  │
│  │  │   Key Mgr    │     │   Endpoints  │                            │  │
│  │  └──────────────┘     └──────────────┘                            │  │
│  │         │                    │                                    │  │
│  │         │                    │                                    │  │
│  │         ▼                    ▼                                    │  │
│  │  ┌──────────────┐     ┌──────────────┐                            │  │
│  │  │   WebPush    │     │ Subscription │                            │  │
│  │  │   Library    │     │   Storage    │                            │  │
│  │  └──────────────┘     └──────────────┘                            │  │
│  └─────────────────────────────────────────────────────────────────────┘  │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Component Responsibilities

| Component | Responsibility |
|-----------|---------------|
| **PWA App (Vue.js)** | User interface, subscribe button, permission handling, notification display in app |
| **Service Worker (sw.js)** | Handles push events, displays notifications, handles notification clicks |
| **Browser Push API** | Browser native API for push subscription and notification display |
| **Push Service (FCM/APNs)** | Delivers push messages to devices (Google FCM for Chrome, Apple APNs for Safari) |
| **VAPID Key Manager** | Generates and manages VAPID keys for server authentication |
| **Push Endpoints** | REST API endpoints for VAPID public key, subscriptions, and sending |
| **WebPush Library** | Python library for sending push notifications with VAPID authentication |
| **Subscription Storage** | Database/storage for user push subscriptions |

### Sequence Diagram: Subscription Flow

```mermaid
sequenceDiagram
    participant User
    participant PWA App
    participant Service Worker
    participant Browser Push API
    participant Backend API
    participant VAPID Key Mgr

    Note over User, VAPID Key Mgr: Phase 1: Initial Setup

    User->>PWA App: Opens PWA from home screen
    PWA App->>Service Worker: navigator.serviceWorker.ready
    Service Worker-->>PWA App: registration

    Note over User, VAPID Key Mgr: Phase 2: Subscription Request

    User->>PWA App: Clicks "Enable notifications"
    PWA App->>PWA App: Check iOS standalone mode
    PWA App->>Browser Push API: Notification.requestPermission()
    Browser Push API-->>User: Show permission dialog
    User->>Browser Push API: Grant permission
    Browser Push API-->>PWA App: "granted"

    PWA App->>Backend API: GET /api/vapid-public-key
    Backend API->>VAPID Key Mgr: get_public_key()
    VAPID Key Mgr-->>Backend API: public_key (PEM)
    Backend API-->>PWA App: {"public_key": "..."}

    PWA App->>Browser Push API: pushManager.subscribe(vapid_key)
    Browser Push API->>Browser Push API: Generate keys (p256dh, auth)
    Browser Push API->>Push Service: Register subscription
    Push Service-->>Browser Push API: endpoint URL
    Browser Push API-->>PWA App: PushSubscription

    PWA App->>Backend API: POST /api/push-subscriptions
    Note right of PWA App: {endpoint, keys, device_name}
    Backend API->>Backend API: Validate subscription
    Backend API->>Backend API: Store subscription (user_id)
    Backend API-->>PWA App: {subscription_id, created}

    Note over User, VAPID Key Mgr: Subscription complete!
```

### Sequence Diagram: Notification Flow

```mermaid
sequenceDiagram
    participant Sender as Message Sender
    participant Backend as Backend API
    participant VAPID as VAPID Key Mgr
    participant WebPush as WebPush Library
    participant PushService as Push Service
    participant ServiceWorker as Service Worker
    participant User as Notification Recipient

    Note over Sender, User: Phase 1: Event Trigger

    Sender->>Backend: Send message to chat
    Backend->>Backend: Store message
    Backend->>Backend: Get recipients (excluding sender)

    loop For each recipient
        Backend->>Backend: Get user's subscriptions
        
        Backend->>VAPID: get_vapid_claims(push_service_url)
        VAPID-->>Backend: {sub, aud, exp}
        
        Backend->>WebPush: webpush_async(subscription, payload, vapid_key)
        WebPush->>WebPush: Sign JWT with VAPID private key
        WebPush->>PushService: POST /push (encrypted payload)
        PushService-->>WebPush: 201 Created
        WebPush-->>Backend: Success
    end

    Note over Sender, User: Phase 2: Delivery

    PushService->>PushService: Route to device
    PushService->>ServiceWorker: Push event (encrypted)
    
    ServiceWorker->>ServiceWorker: Decrypt payload
    ServiceWorker->>ServiceWorker: Parse notification data
    
    ServiceWorker->>User: showNotification(title, options)
    User->>User: See notification on lock screen/notification center
    
    User->>ServiceWorker: Click notification
    ServiceWorker->>ServiceWorker: notificationclick event
    ServiceWorker->>PWA App: postMessage({type: 'NOTIFICATION_CLICKED'})
    PWA App->>PWA App: Navigate to chat/{chatId}
    PWA App->>User: Show chat conversation
```

### Data Flow: Subscription Storage

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    SUBSCRIPTION DATA FLOW                               │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  BROWSER                            BACKEND                             │
│  ──────                             ───────                             │
│                                                                         │
│  PushSubscription                   PushSubscription (dataclass)        │
│  {                                  {                                   │
│    endpoint: "...",                   id: "uuid",                       │
│    keys: {                            user_id: "user123",               │
│      p256dh: "...",                   endpoint: "...",                  │
│      auth: "..."                      keys: {                           │
│    },                                   p256dh: "...",                   │
│    expirationTime: null                 auth: "..."                      │
│  }                                    },                                │
│                                       is_active: true,                  │
│                                       device_name: "iPhone",            │
│                                       created_at: "2026-05-19...",       │
│                                       updated_at: "2026-05-19..."       │
│                                     }                                   │
│                                                                         │
│         POST /api/push-subscriptions                                    │
│         ────────────────────────────▶                                   │
│                                          ┌──────────────────────┐       │
│                                          │ SubscriptionStorage   │       │
│                                          │ (in-memory or DB)     │       │
│                                          │                       │       │
│                                          │ subscriptions: {      │       │
│                                          │   user_id: [sub1, ...]│       │
│                                          │ }                     │       │
│                                          └──────────────────────┘       │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### Security Model

```
┌─────────────────────────────────────────────────────────────────────────┐
│                       SECURITY ARCHITECTURE                             │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  VAPID Authentication                                                   │
│  ───────────────────                                                    │
│                                                                         │
│  Server                          Push Service                           │
│  ──────                          ────────────                           │
│                                                                         │
│  ┌─────────────────┐            ┌─────────────────┐                    │
│  │ VAPID Private   │            │ VAPID Public    │                    │
│  │ Key (secret)    │            │ Key (shared)    │                    │
│  │                 │            │                 │                    │
│  │ Never exposed!  │            │ Sent to browser │                    │
│  │ env: VAPID_     │            │ via /api/vapid- │                    │
│  │ PRIVATE_KEY     │            │ public-key      │                    │
│  └────────┬────────┘            └─────────────────┘                    │
│           │                                                             │
│           │ Signs JWT                                                   │
│           ▼                                                             │
│  ┌─────────────────┐            ┌─────────────────┐                    │
│  │ JWT Token       │            │ Verify JWT      │                    │
│  │ {               │    ──────▶ │ with Public Key │                    │
│  │   sub: "...",   │            │                 │                    │
│  │   aud: "...",   │            │ Confirms:       │                    │
│  │   exp: "..."    │            │ - Server identity│                    │
│  │ }               │            │ - Not expired    │                    │
│  └─────────────────┘            └─────────────────┘                    │
│                                                                         │
│  Endpoint Security                                                      │
│  ─────────────────                                                      │
│                                                                         │
│  GET  /api/vapid-public-key      → Public (no auth)                     │
│  POST /api/push-subscriptions    → Requires authentication              │
│  GET  /api/push-subscriptions    → Requires authentication              │
│  DEL  /api/push-subscriptions/:id → Requires authentication            │
│  POST /api/push-notifications   → Requires admin role                 │
│                                                                         │
│  Rate Limiting                                                          │
│  ────────────                                                           │
│  - 10 notifications per user per hour                                   │
│  - 50 notifications per user per day                                    │
│  - 100 notifications per minute globally                                │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### Architecture: Dual-Channel Messaging

Push notifications are NOT a replacement for WebSocket messaging—they're a **complement**. Understanding when to use each channel is critical for proper implementation.

#### Channel Comparison

| Aspect | WebSocket | Push Notification |
|--------|-----------|-------------------|
| **Delivery** | Real-time, reliable | Best-effort, not guaranteed |
| **Payload** | Unlimited | ~4KB limit |
| **Frequency** | Unlimited | Rate-limited (10/hour, 50/day per user) |
| **Connection** | Requires active connection | Works when app is closed |
| **Use case** | Real-time chat, typing indicators | Alert user to check app |

#### When Messages Are Missed (Without Push)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                     REAL-TIME MESSAGING (WebSocket Only)                   │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   Client1 sends message via WebSocket                                       │
│         │                                                                   │
│         ▼                                                                   │
│   ┌─────────────┐                                                           │
│   │   Server    │                                                           │
│   │             │──▶ WebSocket ──▶ Client2 (online) ✓                     │
│   │             │                                                           │
│   │             │──▶ WebSocket ──▶ Client3 (offline) ✗                    │
│   │             │                      │                                    │
│   │             │                      │ WebSocket connection CLOSED       │
│   │             │                      │ No message delivery               │
│   └─────────────┘                                                           │
│                                                                             │
│   Client3 is "offline" when:                                               │
│   - PWA not running (browser closed, app not launched)                     │
│   - PWA in background (iOS/Android suspended the app)                     │
│   - Device in sleep mode                                                    │
│   - Network disconnected                                                   │
│                                                                             │
│   Result: Client3 MISSES the message entirely                               │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

#### Delivery by Client State

| Client State | WebSocket | Message Received? |
|--------------|-----------|-------------------|
| PWA open in foreground | Connected | ✓ Yes (real-time) |
| PWA in background (desktop tab) | Usually connected | ✓ Usually |
| PWA in background (mobile) | Often disconnected | ✗ Often missed |
| PWA closed / browser closed | Disconnected | ✗ Missed |
| PWA not launched | Disconnected | ✗ Missed |

#### The Dual-Channel Solution

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                     DUAL-CHANNEL ARCHITECTURE                               │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   MESSAGE FLOW (Backend Decision Logic)                                    │
│                                                                             │
│   Client1 sends message to room                                            │
│         │                                                                   │
│         ▼                                                                   │
│   ┌─────────────────────────────────────────────────────────────────┐      │
│   │                        SERVER                                    │      │
│   │                                                                  │      │
│   │   1. Store message in database                                   │      │
│   │   2. Check recipient status:                                     │      │
│   │      ┌─────────────┐                    ┌─────────────┐         │      │
│   │      │  Client2    │                    │  Client3    │         │      │
│   │      │  WebSocket: │                    │  WebSocket: │         │      │
│   │      │  CONNECTED  │                    │  DISCONNECTED│         │      │
│   │      └──────┬──────┘                    └──────┬──────┘         │      │
│   │             │                                  │                 │      │
│   │             ▼                                  ▼                 │      │
│   │   ┌─────────────────┐                ┌─────────────────┐        │      │
│   │   │ Send via        │                │ Send via         │        │      │
│   │   │ WebSocket       │                │ Push Notification│        │      │
│   │   │ (real-time)     │                │ (alert only)     │        │      │
│   │   └─────────────────┘                └─────────────────┘        │      │
│   │                                                                  │      │
│   └─────────────────────────────────────────────────────────────────┘      │
│                                                                             │
│   Client2 receives message immediately via WebSocket                       │
│   Client3 receives push notification → taps it → opens PWA → fetches      │
│          messages from database via API                                     │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

#### Backend Implementation Pattern

```python
# app/chat.py - Message broadcast with dual-channel delivery

async def broadcast_message(room_id: str, message: dict):
    """
    Broadcast message to all room participants using dual-channel approach.
    
    Connected users receive via WebSocket (real-time).
    Offline users receive push notification (alert).
    """
    # 1. ALWAYS store message in database first
    await store_message(room_id, message)
    
    # 2. Get connected users (via WebSocket presence tracking)
    connected_users = await get_connected_users(room_id)
    
    # 3. Send via WebSocket to connected users (real-time)
    for user_id in connected_users:
        await send_via_websocket(user_id, message)
    
    # 4. Send push notification to OFFLINE users (alert only)
    offline_users = await get_room_participants(room_id, exclude=connected_users)
    for user_id in offline_users:
        # Push notification with SHORT preview, NOT full message
        await send_push_notification(
            user_id,
            title=f"New message in {room_name}",
            body=message["text"][:100],  # Short preview only
            data={
                "room_id": room_id,
                "message_id": message["id"]
            }
        )
```

#### Client Reconnection Flow

When an offline user opens the PWA:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                     CLIENT RECONNECTION FLOW                                │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   User taps push notification                                               │
│         │                                                                   │
│         ▼                                                                   │
│   PWA launches                                                              │
│         │                                                                   │
│         ▼                                                                   │
│   WebSocket connects                                                        │
│         │                                                                   │
│         ▼                                                                   │
│   API call: GET /api/messages?since={last_seen_timestamp}                  │
│         │                                                                   │
│         ▼                                                                   │
│   Server returns all missed messages from database                         │
│         │                                                                   │
│         ▼                                                                   │
│   Client displays messages in chat UI                                       │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

**Key Insight:** Push notifications don't deliver the full message—they **alert the user** and provide metadata (room_id, message_id) so the client can fetch the actual content when they open the app.

#### WebSocket Presence Tracking

To implement the dual-channel approach, the server must track WebSocket connections:

```python
# app/presence.py - Track connected users

from collections import defaultdict
from typing import Set

# In-memory tracking (use Redis for production)
room_connections: dict[str, Set[str]] = defaultdict(set)
user_connections: dict[str, Set[str]] = defaultdict(set)  # user_id -> socket_ids

async def user_connected(user_id: str, socket_id: str, room_id: str):
    """Called when user opens WebSocket connection."""
    user_connections[user_id].add(socket_id)
    room_connections[room_id].add(user_id)

async def user_disconnected(user_id: str, socket_id: str, room_id: str):
    """Called when user closes WebSocket connection."""
    user_connections[user_id].discard(socket_id)
    room_connections[room_id].discard(user_id)
    
    # Clean up empty sets
    if not user_connections[user_id]:
        del user_connections[user_id]

async def get_connected_users(room_id: str) -> list[str]:
    """Get list of users currently connected to room via WebSocket."""
    return list(room_connections.get(room_id, set()))

async def is_user_online(user_id: str) -> bool:
    """Check if user has any active WebSocket connections."""
    return len(user_connections.get(user_id, set())) > 0
```

#### Summary: When to Use Each Channel

| Scenario | Channel | Why |
|----------|---------|-----|
| User is actively chatting | WebSocket | Real-time, unlimited messages |
| Typing indicator | WebSocket | High frequency, low latency needed |
| User is offline | Push + API | Must reach user outside app |
| User returns to app | API fetch | Fetch missed history from database |
| Badge update count | Push | Include in notification payload |

---

## Table of Contents

1. [Prerequisites](#1-prerequisites)
2. [Server Setup (VAPID Keys)](#2-server-setup-vapid-keys)
3. [PWA Installation](#3-pwa-installation)
4. [Frontend Integration](#4-frontend-integration)
5. [Backend Integration](#5-backend-integration)
6. [Sending Notifications](#6-sending-notifications)
7. [Handling Notifications](#7-handling-notifications)
8. [Badge Updates](#8-badge-updates)
9. [Testing](#9-testing)
10. [Troubleshooting](#10-troubleshooting)

---

## 1. Prerequisites

### Platform Requirements

| Platform | Requirement | Notes |
|----------|-------------|-------|
| iOS Safari | iOS 16.4+ | Required for Web Push API |
| Android Chrome | Android 5+ | Works in browser or PWA |
| Desktop Chrome/Firefox | Any modern version | Works in browser or PWA |
| macOS Safari | Safari 16+ | Works in browser or PWA |

### Key Requirements

1. **HTTPS Required** - Push notifications only work on secure origins
2. **PWA Manifest** - Must have a valid web app manifest
3. **Service Worker** - Must have an active service worker
4. **VAPID Keys** - Server must have VAPID authentication keys
5. **User Gesture** - Permission prompt must be triggered by user action (not page load)

### Dependencies

```toml
# pyproject.toml
dependencies = [
  "baseweb>=0.6.0",
  "py-vapid>=1.9.0",
  "pywebpush>=2.1.0",
]
```

---

## 2. Server Setup (VAPID Keys)

### 2.1 Generate VAPID Keys

```bash
# Install py-vapid if not already installed
pip install py-vapid

# Generate keys (one-time setup)
python -c "
from py_vapid import Vapid01
v = Vapid01()
v.generate_keys()
print('Private Key:')
print(v.private_pem().decode())
print()
print('Public Key:')
print(v.public_pem().decode())
"
```

### 2.2 Store VAPID Keys Securely

**Option 1: Environment Variables (Development)**

```bash
# .env (DO NOT commit to version control)
VAPID_SUBJECT=mailto:admin@yourdomain.com
VAPID_PRIVATE_KEY="-----BEGIN PRIVATE KEY-----
MIGHAgEAMBMGByqGSM49AgEGCCqGSM49AwEHBG0wawIBAQQg...
-----END PRIVATE KEY-----"
```

**Option 2: Secrets Manager (Production)**

For production, use a secrets manager:
- AWS Secrets Manager
- HashiCorp Vault
- Google Secret Manager
- Azure Key Vault

### 2.3 Configure Baseweb Application

```python
# app/__init__.py
from dotenv import load_dotenv
load_dotenv()  # Load .env file

from baseweb import Baseweb
from baseweb.push import register_push_resources

# Create baseweb app
server = Baseweb("my-chat-app")

# Register push notification endpoints
register_push_resources(server, prefix="/api")

# ASGI entry point
asgi_app = server._asgi_app
```

### 2.4 Verify VAPID Configuration

```python
# Test script to verify VAPID setup
import asyncio
from baseweb.vapid import get_vapid_manager

async def test_vapid():
    manager = await get_vapid_manager()
    
    if manager.is_configured():
        print("✓ VAPID keys configured")
        print(f"  Public key: {manager.get_public_key()[:50]}...")
        print(f"  Subject: {manager.get_subject()}")
    else:
        print("✗ VAPID keys not configured")

asyncio.run(test_vapid())
```

---

## 3. PWA Installation

### 3.1 Enable PWA Mode

Set `APP_STYLE=pwa` in your environment:

```bash
# .env
APP_STYLE=pwa
```

### 3.2 Verify PWA Manifest

```bash
curl http://localhost:8000/manifest.json | jq
```

Expected output:
```json
{
  "name": "My Chat App",
  "short_name": "Chat",
  "display": "standalone",
  "icons": [
    { "src": "/static/images/icons/icon-192x192.png", "sizes": "192x192" },
    { "src": "/static/images/icons/icon-512x512.png", "sizes": "512x512" }
  ]
}
```

### 3.3 iOS Safari Installation

1. Open Safari on iOS 16.4+
2. Navigate to your PWA URL
3. Tap the Share button (square with up arrow)
4. Tap "Add to Home Screen"
5. Tap "Add" in the top-right corner
6. The app icon appears on your home screen

**Important:** Push notifications ONLY work when the PWA is launched from the home screen, not from Safari tabs.

---

## 4. Frontend Integration

### 4.1 Service Worker Push Handler

Add to your Service Worker (`static/js/sw.js`):

```javascript
// Push event handler - show notification
self.addEventListener('push', (event) => {
  console.log('[Service Worker] Push received');
  
  let notificationData = {
    title: 'New Message',
    body: 'You have a new message',
    icon: '/static/images/icons/icon-192x192.png',
    badge: '/static/images/icons/badge-72x72.png',
    tag: 'chat-message',
    data: {
      url: '/chat',
      messageId: null
    }
  };
  
  // Parse push data if available
  if (event.data) {
    try {
      const data = event.data.json();
      notificationData = {
        title: data.title || notificationData.title,
        body: data.body || notificationData.body,
        icon: data.icon || notificationData.icon,
        badge: data.badge || notificationData.badge,
        tag: data.tag || notificationData.tag,
        data: {
          url: data.url || '/chat',
          messageId: data.messageId,
          chatId: data.chatId
        },
        actions: data.actions || []
      };
    } catch (e) {
      console.error('[Service Worker] Error parsing push data:', e);
    }
  }
  
  event.waitUntil(
    self.registration.showNotification(notificationData.title, {
      body: notificationData.body,
      icon: notificationData.icon,
      badge: notificationData.badge,
      tag: notificationData.tag,
      data: notificationData.data,
      actions: notificationData.actions,
      requireInteraction: true,
      renotify: true
    })
  );
});

// Notification click handler
self.addEventListener('notificationclick', (event) => {
  console.log('[Service Worker] Notification clicked');
  
  event.notification.close();
  
  const urlToOpen = event.notification.data?.url || '/';
  
  event.waitUntil(
    clients.matchAll({ type: 'window', includeUncontrolled: true })
      .then((clientList) => {
        // Check if app is already open
        for (const client of clientList) {
          if (client.url.includes(self.location.origin) && 'focus' in client) {
            client.postMessage({
              type: 'NOTIFICATION_CLICKED',
              data: event.notification.data
            });
            return client.focus();
          }
        }
        // Open new window if not already open
        if (clients.openWindow) {
          return clients.openWindow(urlToOpen);
        }
      })
  );
});
```

### 4.2 Push Subscription Manager (JavaScript)

Create `static/js/push-notifications.js`:

```javascript
/**
 * Push Notification Manager for Baseweb PWAs
 */

class PushNotificationManager {
  constructor() {
    this.vapidPublicKey = null;
    this.subscription = null;
    this.isSupported = 'serviceWorker' in navigator && 'PushManager' in window;
    this.isIOS = /iPad|iPhone|iPod/.test(navigator.userAgent);
    this.isStandalone = window.matchMedia('(display-mode: standalone)').matches 
      || window.navigator.standalone === true;
  }

  /**
   * Check if push notifications are available
   */
  async checkAvailability() {
    if (!this.isSupported) {
      return { available: false, reason: 'Push notifications not supported' };
    }

    // iOS requires standalone mode
    if (this.isIOS && !this.isStandalone) {
      return {
        available: false,
        reason: 'iOS requires PWA to be installed on home screen'
      };
    }

    // Check service worker
    const registration = await navigator.serviceWorker.ready;
    if (!registration) {
      return { available: false, reason: 'Service worker not registered' };
    }

    return { available: true };
  }

  /**
   * Get VAPID public key from server
   */
  async getVapidPublicKey() {
    const response = await fetch('/api/vapid-public-key');
    if (!response.ok) {
      throw new Error('Failed to get VAPID public key');
    }
    const data = await response.json();
    this.vapidPublicKey = data.public_key;
    return this.vapidPublicKey;
  }

  /**
   * Request permission and subscribe to push notifications
   * MUST be called from a user gesture (button click)
   */
  async subscribe(options = {}) {
    // Check availability
    const availability = await this.checkAvailability();
    if (!availability.available) {
      throw new Error(availability.reason);
    }

    // Get VAPID key if not cached
    if (!this.vapidPublicKey) {
      await this.getVapidPublicKey();
    }

    // Request permission (MUST be from user gesture)
    const permission = await Notification.requestPermission();
    if (permission !== 'granted') {
      throw new Error('Notification permission denied');
    }

    // Get service worker registration
    const registration = await navigator.serviceWorker.ready;

    // Subscribe to push
    try {
      this.subscription = await registration.pushManager.subscribe({
        userVisibleOnly: true,
        applicationServerKey: this.urlBase64ToUint8Array(this.vapidPublicKey)
      });
    } catch (error) {
      console.error('[Push] Subscribe error:', error);
      throw new Error('Failed to subscribe to push notifications');
    }

    // Send subscription to server
    await this.sendSubscriptionToServer(this.subscription, options);

    return this.subscription;
  }

  /**
   * Send subscription to server
   */
  async sendSubscriptionToServer(subscription, options = {}) {
    const response = await fetch('/api/push-subscriptions', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        endpoint: subscription.endpoint,
        keys: {
          p256dh: btoa(String.fromCharCode.apply(null, subscription.getKey('p256dh'))),
          auth: btoa(String.fromCharCode.apply(null, subscription.getKey('auth')))
        },
        device_name: options.deviceName || navigator.userAgent,
        user_agent: navigator.userAgent
      })
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to register subscription');
    }

    return response.json();
  }

  /**
   * Unsubscribe from push notifications
   */
  async unsubscribe() {
    if (!this.subscription) {
      const registration = await navigator.serviceWorker.ready;
      this.subscription = await registration.pushManager.getSubscription();
    }

    if (this.subscription) {
      // Unsubscribe from push service
      await this.subscription.unsubscribe();

      // Remove from server
      // Note: You need to store the subscription ID to delete it
      // This is typically done by calling DELETE /api/push-subscriptions/{id}
    }

    this.subscription = null;
  }

  /**
   * Get current subscription status
   */
  async getSubscriptionStatus() {
    const availability = await this.checkAvailability();
    if (!availability.available) {
      return {
        subscribed: false,
        permission: Notification.permission,
        ...availability
      };
    }

    const registration = await navigator.serviceWorker.ready;
    const subscription = await registration.pushManager.getSubscription();

    return {
      subscribed: !!subscription,
      permission: Notification.permission,
      endpoint: subscription?.endpoint
    };
  }

  /**
   * Convert VAPID key from base64 to Uint8Array
   */
  urlBase64ToUint8Array(base64String) {
    const padding = '='.repeat((4 - base64String.length % 4) % 4);
    const base64 = (base64String + padding)
      .replace(/\-/g, '+')
      .replace(/_/g, '/');

    const rawData = window.atob(base64);
    const outputArray = new Uint8Array(rawData.length);

    for (let i = 0; i < rawData.length; ++i) {
      outputArray[i] = rawData.charCodeAt(i);
    }
    return outputArray;
  }
}

// Export as global
window.PushNotificationManager = PushNotificationManager;
```

### 4.3 UI Integration (Vue Component)

Create a Vue component for the subscribe button:

```javascript
// static/js/components/PushSubscribeButton.js

const PushSubscribeButton = {
  name: 'PushSubscribeButton',
  template: `
    <div>
      <!-- iOS not in standalone mode -->
      <v-alert v-if="showIOSWarning" type="info" class="mb-4">
        <strong>Install the App</strong><br>
        To receive push notifications on iOS, install this app on your home screen:
        <ol class="mt-2">
          <li>Tap the Share button (square with up arrow)</li>
          <li>Scroll down and tap "Add to Home Screen"</li>
          <li>Tap "Add" in the top-right corner</li>
          <li>Open the app from your home screen</li>
        </ol>
      </v-alert>

      <!-- Subscribe button -->
      <v-btn
        v-if="!subscribed && !showIOSWarning"
        :color="buttonColor"
        :loading="loading"
        :disabled="!supported"
        @click="requestPermission"
      >
        <v-icon start>mdi-bell</v-icon>
        {{ buttonText }}
      </v-btn>

      <!-- Subscribed indicator -->
      <v-chip v-if="subscribed" color="success">
        <v-icon start>mdi-bell-check</v-icon>
        Notifications enabled
      </v-chip>

      <!-- Permission denied warning -->
      <v-alert v-if="permissionDenied" type="warning" class="mt-4">
        Notifications are blocked. Enable them in your browser settings.
      </v-alert>
    </div>
  `,
  data() {
    return {
      pushManager: null,
      supported: false,
      subscribed: false,
      loading: false,
      permissionDenied: false,
      isIOS: false,
      isStandalone: false
    };
  },
  computed: {
    showIOSWarning() {
      return this.isIOS && !this.isStandalone;
    },
    buttonColor() {
      return this.permissionDenied ? 'warning' : 'primary';
    },
    buttonText() {
      if (this.permissionDenied) return 'Notifications blocked';
      if (this.loading) return 'Subscribing...';
      return 'Enable notifications';
    }
  },
  async mounted() {
    this.pushManager = new PushNotificationManager();
    
    // Check platform
    this.isIOS = this.pushManager.isIOS;
    this.isStandalone = this.pushManager.isStandalone;
    this.supported = this.pushManager.isSupported;

    // Check current status
    if (this.supported && !this.showIOSWarning) {
      const status = await this.pushManager.getSubscriptionStatus();
      this.subscribed = status.subscribed;
      this.permissionDenied = status.permission === 'denied';
    }
  },
  methods: {
    async requestPermission() {
      this.loading = true;
      try {
        await this.pushManager.subscribe({
          deviceName: this.getDeviceName()
        });
        this.subscribed = true;
        this.permissionDenied = false;
        
        // Notify parent component
        this.$emit('subscribed');
        
        // Show success toast
        this.$store.commit('notify/success', 'Push notifications enabled!');
      } catch (error) {
        console.error('[Push] Subscribe error:', error);
        if (error.message.includes('denied')) {
          this.permissionDenied = true;
        }
        this.$store.commit('notify/error', error.message);
      } finally {
        this.loading = false;
      }
    },
    getDeviceName() {
      const ua = navigator.userAgent;
      if (ua.includes('iPhone')) return 'iPhone';
      if (ua.includes('iPad')) return 'iPad';
      if (ua.includes('Android')) return 'Android';
      if (ua.includes('Mac')) return 'Mac';
      if (ua.includes('Windows')) return 'Windows';
      return 'Unknown Device';
    }
  }
};

// Register component
app.component('PushSubscribeButton', PushSubscribeButton);
```

---

## 5. Backend Integration

### 5.1 Authentication Setup

Push notification endpoints require user authentication. Set up your authenticator:

```python
# app/auth.py
from baseweb import Baseweb

def get_current_user():
    """Get the current authenticated user ID."""
    # This depends on your authentication system
    # Example: JWT, session, basic auth, etc.
    from quart import request
    return getattr(request, 'user_id', None)

# Register with baseweb
server.authenticator = get_current_user
```

### 5.2 Admin Authorization

For sending notifications, you need admin/sender authorization:

```python
# app/auth.py

def is_admin():
    """Check if current user has admin/sender role."""
    from quart import request
    user_id = getattr(request, 'user_id', None)
    # Check your user database for admin role
    return user_id in ADMIN_USER_IDS  # Replace with your logic

# Configure push resources with authorization
from baseweb.push import register_push_resources

register_push_resources(
    server,
    prefix="/api",
    # Note: You may need to customize the authorization
    # The default requires authentication for subscription endpoints
    # and admin role for sending notifications
)
```

---

## 6. Sending Notifications

### 6.1 Backend Notification Sender

Create a helper function to send notifications:

```python
# app/notifications.py

import asyncio
from baseweb.push import (
    SubscriptionStorage,
    PushNotificationPayload,
    RateLimiter,
)
from baseweb.vapid import get_vapid_manager

async def send_push_notification(
    user_id: str,
    title: str,
    body: str,
    data: dict = None,
    actions: list = None,
    url: str = None
) -> dict:
    """
    Send a push notification to a user.
    
    Args:
        user_id: The user to notify
        title: Notification title
        body: Notification body
        data: Additional data (chatId, messageId, etc.)
        actions: Notification actions (optional)
        url: URL to open when clicked (optional)
    
    Returns:
        Dictionary with results for each subscription
    """
    storage = SubscriptionStorage()
    rate_limiter = RateLimiter()
    
    # Check rate limit
    can_send, reason = rate_limiter.can_send(user_id)
    if not can_send:
        return {"success": False, "reason": reason}
    
    # Create payload
    payload = PushNotificationPayload(
        title=title,
        body=body,
        data=data,
        actions=actions,
        url=url
    )
    
    # Get user's subscriptions
    subscriptions = storage.get_by_user(user_id)
    if not subscriptions:
        return {"success": False, "reason": "No subscriptions"}
    
    # Get VAPID manager
    manager = await get_vapid_manager()
    if not manager.is_configured():
        return {"success": False, "reason": "VAPID not configured"}
    
    # Send to each subscription
    results = []
    for subscription in subscriptions:
        if not subscription.is_active:
            continue
            
        try:
            # Import pywebpush
            from pywebpush import webpush_async
            
            # Get VAPID claims
            claims = manager.get_vapid_claims(subscription.endpoint)
            
            # Send notification
            result = await webpush_async(
                subscription_info=subscription.to_webpush_format(),
                data=payload.to_json(),
                vapid_private_key=manager.get_private_key_pem(),
                vapid_claims=claims
            )
            
            # Update rate limiter
            rate_limiter.record_send(user_id)
            
            results.append({
                "subscription_id": subscription.id,
                "success": True,
                "status": result.status_code if result else 200
            })
            
        except Exception as e:
            # Handle expired/invalid subscriptions
            error_str = str(e)
            if "410" in error_str or "404" in error_str:
                # Subscription expired - mark as inactive
                storage.deactivate(subscription.id)
                results.append({
                    "subscription_id": subscription.id,
                    "success": False,
                    "reason": "Subscription expired"
                })
            else:
                results.append({
                    "subscription_id": subscription.id,
                    "success": False,
                    "reason": str(e)
                })
    
    return {
        "success": any(r["success"] for r in results),
        "results": results
    }
```

### 6.2 Chat Message Notification Example

```python
# app/chat.py

from app.notifications import send_push_notification

async def on_new_message(chat_id: str, message: dict):
    """Called when a new chat message is received."""
    
    # Get chat participants
    participants = await get_chat_participants(chat_id)
    
    # Get sender info
    sender_name = message.get('sender_name', 'Someone')
    message_preview = message['text'][:100] + ('...' if len(message['text']) > 100 else '')
    
    # Send notification to other participants
    for user_id in participants:
        if user_id == message['sender_id']:
            continue  # Don't notify sender
        
        await send_push_notification(
            user_id=user_id,
            title=f"{sender_name}",
            body=message_preview,
            data={
                'chatId': chat_id,
                'messageId': message['id']
            },
            actions=[
                {'action': 'reply', 'title': 'Reply'},
                {'action': 'dismiss', 'title': 'Dismiss'}
            ],
            url=f'/chat/{chat_id}'
        )
    
    # Update badge counts
    await update_badge_counts(participants)
```

---

## 7. Handling Notifications

### 7.1 Notification Click Handler in App

Add this to your Vue app:

```javascript
// static/js/app.js

// Listen for messages from service worker
navigator.serviceWorker.addEventListener('message', (event) => {
  if (event.data && event.data.type === 'NOTIFICATION_CLICKED') {
    console.log('[App] Notification clicked:', event.data.data);
    
    // Navigate to the chat
    if (event.data.data.chatId) {
      app.$router.push(`/chat/${event.data.data.chatId}`);
    } else if (event.data.data.url) {
      app.$router.push(event.data.data.url);
    }
    
    // Clear badge if needed
    updateBadgeCount();
  }
});

// Listen for service worker controller change (new version)
navigator.serviceWorker.addEventListener('controllerchange', () => {
  console.log('[App] Service worker updated');
});
```

### 7.2 Service Worker Update Handling

```javascript
// static/js/sw.js

// Handle notification close
self.addEventListener('notificationclose', (event) => {
  console.log('[Service Worker] Notification closed');
  
  // Optional: Track dismissals
  fetch('/api/push-notifications/dismissed', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      notificationId: event.notification.data?.messageId,
      timestamp: Date.now()
    })
  }).catch(err => console.error('[SW] Error tracking dismissal:', err));
});
```

---

## 8. Badge Updates

### 8.1 Server-Side Badge Count

```python
# app/badges.py

from app.notifications import send_push_notification

async def update_badge_counts(user_ids: list[str]):
    """
    Update app badge counts for users.
    This is typically called after receiving new messages.
    """
    for user_id in user_ids:
        unread_count = await get_unread_message_count(user_id)
        
        # Store badge count in database for reference
        await set_user_badge(user_id, unread_count)
        
        # Note: iOS doesn't support programmatic badge updates via push
        # Badge is set when notification arrives
        # You can include badge count in the notification payload
        
async def get_unread_message_count(user_id: str) -> int:
    """Get unread message count for badge."""
    # Query your database
    # Example: SELECT COUNT(*) FROM messages WHERE user_id = ? AND read = 0
    pass

async def set_user_badge(user_id: str, count: int):
    """Store badge count for reference."""
    # Store in Redis or database
    pass
```

### 8.2 Include Badge in Push Payload

```python
# app/notifications.py - Update send_push_notification

async def send_push_notification(
    user_id: str,
    title: str,
    body: str,
    badge_count: int = None,
    **kwargs
) -> dict:
    """Send push with badge count."""
    
    # Get badge count if not provided
    if badge_count is None:
        badge_count = await get_unread_message_count(user_id)
    
    payload = PushNotificationPayload(
        title=title,
        body=body,
        badge=badge_count,  # iOS uses this
        **kwargs
    )
    
    # ... rest of implementation
```

---

## 9. Testing

### 9.1 Test VAPID Setup

```python
# tests/test_push_notifications.py

import asyncio
import pytest
from baseweb.vapid import VAPIDKeyManager, get_vapid_manager

@pytest.mark.asyncio
async def test_vapid_keys_generated():
    """Test VAPID key generation."""
    manager = VAPIDKeyManager()
    await manager.initialize()
    
    assert manager.is_configured()
    public_key = manager.get_public_key()
    assert public_key is not None
    assert "BEGIN PUBLIC KEY" in public_key

@pytest.mark.asyncio
async def test_vapid_claims_for_safari():
    """Test VAPID claims include Safari-required fields."""
    manager = VAPIDKeyManager()
    await manager.initialize()
    
    claims = manager.get_vapid_claims("https://web.push.apple.com/token")
    
    assert "sub" in claims
    assert "aud" in claims
    assert "exp" in claims
    assert claims["aud"] == "https://web.push.apple.com"
```

### 9.2 Test Subscription Flow

```python
@pytest.mark.asyncio
async def test_subscribe_to_push():
    """Test push subscription."""
    app = create_test_app()
    client = app.test_client()
    
    # Get VAPID public key
    response = await client.get('/api/vapid-public-key')
    assert response.status_code == 200
    data = await response.get_json()
    assert 'public_key' in data
    
    # Subscribe (simulated - requires browser)
    # In real tests, use Playwright or similar
```

### 9.3 Test Notification Sending

```python
@pytest.mark.asyncio
async def test_send_notification():
    """Test sending push notification."""
    from app.notifications import send_push_notification
    
    # Create test subscription
    # ...
    
    result = await send_push_notification(
        user_id="test-user",
        title="Test",
        body="Test notification",
        data={"chatId": "123"}
    )
    
    assert result["success"] == True
```

---

## 10. Troubleshooting

### Common Issues

| Issue | Cause | Solution |
|-------|-------|----------|
| "VAPID not configured" | Missing VAPID_PRIVATE_KEY env var | Set environment variable |
| Permission denied | Browser blocked notifications | User must enable in browser settings |
| iOS notifications not working | App not in standalone mode | Install PWA on home screen |
| "Subscription expired" | Browser unsubscribed | Re-subscribe user |
| Notifications not showing | Wrong VAPID key | Verify public key matches server |

### Debug Checklist

1. **Verify VAPID keys match**
   ```bash
   curl http://localhost:8000/api/vapid-public-key
   # Compare with your stored public key
   ```

2. **Check service worker registration**
   ```javascript
   navigator.serviceWorker.ready.then(reg => {
     console.log('SW registered:', reg);
     console.log('Push manager:', reg.pushManager);
   });
   ```

3. **Test notification permission**
   ```javascript
   Notification.requestPermission().then(p => console.log('Permission:', p));
   ```

4. **Check subscription**
   ```javascript
   navigator.serviceWorker.ready
     .then(reg => reg.pushManager.getSubscription())
     .then(sub => console.log('Subscription:', sub));
   ```

### iOS-Specific Troubleshooting

1. **Notifications not received on iOS:**
   - Verify app is installed on home screen (not Safari tab)
   - Check iOS version is 16.4 or later
   - Verify using Safari (not Chrome/Firefox on iOS)
   - Check VAPID claims include `sub` and `aud`

2. **Permission prompt not showing:**
   - Must be triggered from user gesture (button click)
   - Cannot be triggered on page load

3. **Notification sound:**
   - iOS plays default sound; custom sounds require app bundle

---

## Summary

The complete push notification flow:

1. **Server Setup:** Generate VAPID keys, configure environment
2. **PWA Install:** User installs PWA on home screen (iOS requirement)
3. **Permission:** User clicks "Enable notifications" button
4. **Subscribe:** Browser creates push subscription, sends to server
5. **Store:** Server stores subscription with user association
6. **Trigger:** Backend sends notification with VAPID authentication
7. **Receive:** Service Worker receives push event
8. **Display:** Service Worker shows notification
9. **Click:** User clicks notification, app opens to relevant page
10. **Badge:** Notification updates app badge count

---

*Document version: 1.0.0*
*Last updated: 2026-05-19*