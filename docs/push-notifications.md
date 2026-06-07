# Push Notifications Documentation

Complete guide for implementing and using push notifications in Baseweb Progressive Web Apps (PWAs).

## Table of Contents

1. [Overview](#overview)
2. [Compatibility Matrix](#compatibility-matrix)
3. [User Guide: iOS Safari PWA Installation](#user-guide-ios-safari-pwa-installation)
4. [Developer Guide: Push Notification Setup](#developer-guide-push-notification-setup)
5. [API Reference](#api-reference)
6. [Troubleshooting Guide](#troubleshooting-guide)

---

## Overview

Push notifications allow your PWA to send alerts to users even when the app is not actively running. This is essential for real-time applications like chat, alerts, and updates.

### Key Requirements

- **HTTPS Required** - Push notifications only work on secure origins
- **Service Worker** - Must have an active service worker
- **VAPID Keys** - Server must have VAPID authentication keys
- **User Gesture** - Permission prompt must be triggered by user action

### Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              PUSH NOTIFICATION FLOW                         │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  Browser                           Backend                                   │
│  ───────                           ──────                                   │
│                                                                             │
│  PWA App                          VAPID Key Manager                         │
│  └── Subscribe Button     ──▶     └── Generate/Load Keys                   │
│      └── Request Permission          └── GET /api/vapid-public-key          │
│      └── Subscribe to Push                                              │
│      └── POST /api/push-subscriptions                                    │
│                                  Subscription Storage                      │
│                                  └── Store user subscriptions              │
│                                                                             │
│  Push Service (FCM/APNs)                                                    │
│  └── Receive notification from backend                                     │
│  └── Deliver to device                                                     │
│                                                                             │
│  Service Worker                                                            │
│  └── Receive push event                                                    │
│  └── Show notification                                                    │
│  └── Handle click → Navigate to app                                       │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Compatibility Matrix

### Platform Support

| Platform | Browser | Minimum Version | PWA Mode Required | Notes |
|----------|---------|-----------------|-------------------|-------|
| **iOS/iPadOS** | Safari | 16.4+ | **Yes (standalone)** | **Chrome/Firefox on iOS do NOT support push** |
| Android | Chrome | 50+ | No | Works in browser and PWA |
| Android | Firefox | 44+ | No | Works in browser and PWA |
| Desktop | Chrome | 50+ | No | Works in browser and PWA |
| Desktop | Firefox | 44+ | No | Works in browser and PWA |
| Desktop | Safari | 16+ | No | Works in browser and PWA |
| Desktop | Edge | 79+ | No | Works in browser and PWA |

### Key Limitations

#### iOS Safari (Critical)

- **iOS Simulator does NOT support Web Push** - Must test on real device
- **iOS 16.4 or later required** - Older versions do not support push
- **Standalone mode required** - Must be installed on Home Screen
- **Safari only** - Third-party browsers (Chrome, Firefox) on iOS use WebKit but do NOT support push
- **User gesture required** - Permission prompt must be triggered by user tap/click

#### General

- **HTTPS required** - Push API only works on secure origins
- **Service worker required** - Must have active service worker registration
- **VAPID key consistency** - Keys must not change between server restarts

---

## User Guide: iOS Safari PWA Installation

### Step-by-Step Installation

Follow these steps to install a Baseweb PWA on iOS and enable push notifications.

#### Step 1: Check iOS Version

1. Open **Settings** on your iPhone or iPad
2. Tap **General** → **About**
3. Scroll to **Software Version**
4. Verify it shows **16.4** or higher
5. If lower than 16.4, update your iOS before continuing

#### Step 2: Open Safari

1. Open the **Safari** app (not Chrome, Firefox, or other browsers)
2. Navigate to your Baseweb app URL (e.g., `https://myapp.example.com`)

**Important:** You MUST use Safari. Other browsers on iOS do not support Web Push notifications.

#### Step 3: Install PWA on Home Screen

1. Tap the **Share button** (square with up arrow) at the bottom of Safari
2. Scroll down and tap **"Add to Home Screen"**
3. (Optional) Edit the app name if desired
4. Tap **"Add"** in the top-right corner
5. The app icon appears on your Home Screen

#### Step 4: Launch PWA

1. Close Safari
2. Find the new app icon on your Home Screen
3. **Tap the icon to launch the PWA**

**Critical:** Push notifications ONLY work when the app is launched from the Home Screen icon (standalone mode). Running in a Safari tab does NOT support push notifications.

#### Step 5: Enable Notifications

1. In the PWA, navigate to the **Notifications** or **Settings** page
2. Tap the **"Enable"** or **"Subscribe"** button
3. iOS will show a permission dialog: `"App Name" Would Like to Send You Notifications`
4. Tap **"Allow"** to grant permission
5. The app should show **"Notifications Enabled"** or similar confirmation

#### Step 6: Test Notifications

1. Use the app's **"Send Test Notification"** button (if available)
2. Or have another user send you a notification
3. Put the app in the background or lock your device
4. Wait for the notification to appear

### Troubleshooting iOS Installation

| Issue | Cause | Solution |
|-------|-------|----------|
| "Add to Home Screen" not showing | Already installed | Check Home Screen for existing icon |
| No notifications received | Not in standalone mode | Launch from Home Screen, not Safari |
| Permission prompt doesn't show | Already denied | Go to Settings → App → Notifications → Enable |
| iOS version too old | iOS < 16.4 | Update iOS to 16.4 or later |
| Wrong browser | Not using Safari | Must use Safari on iOS |
| Notifications stop working | Server restarted with temp keys | Set VAPID_PRIVATE_KEY in environment |

### Screenshot Guide

```
Step 1: Check iOS Version
┌─────────────────────────────┐
│ Settings                     │
│   General                    │
│     About                    │
│       Software Version: 16.4+│  ✓ Required
└─────────────────────────────┘

Step 2-3: Add to Home Screen
┌─────────────────────────────┐
│ Safari                      │
│   [Share button] ──▶        │
│     Add to Home Screen      │
│       [Add]                 │
└─────────────────────────────┘

Step 4: Launch PWA
┌─────────────────────────────┐
│ Home Screen                 │
│   [App Icon] ──▶ Launch     │  ✓ Must launch from here
└─────────────────────────────┘

Step 5: Enable Notifications
┌─────────────────────────────┐
│ App                          │
│   Notifications Page         │
│     [Enable] ──▶             │
│       "Allow" permission     │
└─────────────────────────────┘
```

---

## Developer Guide: Push Notification Setup

### Prerequisites

- Python 3.9+
- Baseweb 0.6.0+
- py-vapid package
- pywebpush package

### Step 1: Install Dependencies

```bash
# Using pip
pip install py-vapid pywebpush

# Or using uv
uv pip install py-vapid pywebpush
```

### Step 2: Generate VAPID Keys

**One-time setup** - Generate keys and store securely:

```bash
# Generate VAPID keys
python -c "
from py_vapid import Vapid01
v = Vapid01()
v.generate_keys()
print('VAPID_PRIVATE_KEY:')
print(v.private_pem().decode())
print()
print('VAPID_PUBLIC_KEY:')
print(v.public_pem().decode())
"
```

**Save the output securely:**

```bash
# Store in .env file (DO NOT commit to version control)
cat >> .env << 'EOF'
VAPID_SUBJECT="mailto:admin@yourdomain.com"
VAPID_PRIVATE_KEY="-----BEGIN PRIVATE KEY-----
MIGHAgEAMBMGByqGSM49AgEGCCqGSM49AwEHBG0wawIBAQQg...
-----END PRIVATE KEY-----
"
EOF
```

**Important:** Never commit VAPID_PRIVATE_KEY to version control. Use environment variables or secrets management in production.

### Step 3: Configure Baseweb Application

```python
# app/__init__.py
from dotenv import load_dotenv
load_dotenv()  # Load .env file

from baseweb import Baseweb
from baseweb.push import register_push_resources

# Create baseweb app
server = Baseweb("my-app")

# Register push notification endpoints
register_push_resources(server, prefix="/api")

# ASGI entry point
asgi_app = server._asgi_app
```

### Step 4: Verify VAPID Configuration

Run this test to verify your setup:

```python
# test_vapid.py
import asyncio
from baseweb.vapid import get_public_key, is_configured

async def test_vapid():
    if not is_configured():
        print("✗ VAPID keys not configured")
        print("  Set VAPID_PRIVATE_KEY in environment")
        return

    try:
        public_key = get_public_key()
        print("✓ VAPID keys configured")
        print(f"  Public key: {public_key[:50]}...")
    except Exception as e:
        print(f"✗ VAPID error: {e}")

asyncio.run(test_vapid())
```

### Step 5: Set Up Authentication

Push notification endpoints require authentication:

```python
# app/auth.py
from quart import request

def get_current_user():
    """Get the current authenticated user ID."""
    # Implement your authentication logic
    # Examples: JWT, session cookie, API key
    return getattr(request, 'user_id', None)

def is_admin_user():
    """Check if current user has admin role."""
    # Implement your authorization logic
    return getattr(request, 'is_admin', False)

# Register authenticator with Baseweb
server.authenticator = get_current_user
```

### Step 6: Frontend Integration

#### 6.1 Register Vuex Store Module

```javascript
// app/store.js
import pushModule from '/static/js/store-push.js';

const store = new Vuex.Store({
  modules: {
    push: pushModule
  }
});
```

#### 6.2 Create Settings Page Component

```javascript
// app/pages/notifications.js
const PushNotificationSettings = {
  navigation: {
    path: '/settings/notifications',
    text: 'Notifications',
    icon: 'mdi-bell'
  },
  template: `
    <page title="Notifications">
      <v-card>
        <v-card-title>Push Notifications</v-card-title>
        <v-card-text>
          <!-- iOS Standalone Warning -->
          <v-alert v-if="isIOS && !isStandalone" type="info">
            To receive notifications on iOS, install this app on your Home Screen.
          </v-alert>

          <!-- Subscribe Button -->
          <v-btn v-if="!subscribed" @click="subscribe">
            Enable Notifications
          </v-btn>

          <!-- Subscribed Status -->
          <v-chip v-else color="success">
            Notifications Enabled
          </v-chip>
        </v-card-text>
      </v-card>
    </page>
  `,
  computed: {
    subscribed() {
      return this.$store.state.push.subscriptionStatus === 'subscribed';
    }
  },
  async mounted() {
    await this.$store.dispatch('push/fetchVapidKey');
    await this.$store.dispatch('push/checkSubscription');
  },
  methods: {
    async subscribe() {
      const result = await this.$store.dispatch('push/subscribe');
      if (result === 'subscribed') {
        this.$store.commit('notify/success', 'Notifications enabled!');
      }
    }
  }
};
```

#### 6.3 Service Worker Push Handler

```javascript
// static/js/sw.js
self.addEventListener('push', (event) => {
  const data = event.data ? event.data.json() : {};
  
  const title = data.title || 'New Notification';
  const options = {
    body: data.body || 'You have a new message',
    icon: data.icon || '/static/images/icons/icon-192x192.png',
    badge: data.badge || '/static/images/icons/badge-72x72.png',
    tag: data.tag,
    data: {
      url: data.url || '/'
    }
  };

  event.waitUntil(
    self.registration.showNotification(title, options)
  );
});

self.addEventListener('notificationclick', (event) => {
  event.notification.close();
  
  const url = event.notification.data?.url || '/';
  
  event.waitUntil(
    clients.matchAll({ type: 'window' }).then((clientList) => {
      for (const client of clientList) {
        if (client.url.includes(self.location.origin) && 'focus' in client) {
          return client.focus();
        }
      }
      return clients.openWindow(url);
    })
  );
});
```

### Step 7: Send Notifications from Backend

```python
# app/notifications.py
import asyncio
from baseweb.push import (
    get_subscription_storage,
    PushNotificationPayload,
    send_push_notification
)
from baseweb.vapid import get_vapid_instance, get_vapid_claims

async def notify_user(user_id: str, title: str, body: str, url: str = None):
    """Send push notification to a user."""
    storage = get_subscription_storage()
    subscriptions = storage.get_by_user(user_id)

    if not subscriptions:
        return {"sent": 0, "message": "No subscriptions"}

    sent = 0
    for subscription in subscriptions:
        if not subscription.is_active:
            continue

        payload = PushNotificationPayload(
            title=title,
            body=body,
            url=url
        )

        try:
            result = await send_push_notification(subscription, payload)
            if result:
                sent += 1
        except Exception as e:
            # Mark inactive subscriptions
            if "410" in str(e) or "404" in str(e):
                storage.mark_inactive(subscription.id)

    return {"sent": sent}
```

### Step 8: Test Push Notifications

```bash
# 1. Start development server
make run

# 2. Start ngrok for HTTPS (required for iOS)
ngrok http 8000

# 3. On iPhone, open Safari to ngrok URL
# 4. Add to Home Screen
# 5. Launch from Home Screen
# 6. Enable notifications in app

# 7. Send test notification via API
curl -X POST https://your-ngrok-url.ngrok.io/api/push-notifications \
  -H "Content-Type: application/json" \
  -H "Cookie: session=your-session-cookie" \
  -d '{
    "title": "Test Notification",
    "body": "Hello from baseweb!",
    "url": "https://your-ngrok-url.ngrok.io"
  }'
```

---

## API Reference

### VAPID Public Key

**GET /api/vapid-public-key**

Returns the VAPID public key needed for browser subscription.

**Response:**
```json
{
  "public_key": "BC_M4u...base64url-encoded-key",
  "subject": "mailto:admin@example.com"
}
```

**Status Codes:**
- `200 OK` - Success
- `503 Service Unavailable` - VAPID not configured

### Create Subscription

**POST /api/push-subscriptions**

Register a new push subscription.

**Request:**
```json
{
  "endpoint": "https://fcm.googleapis.com/fcm/send/...",
  "keys": {
    "p256dh": "base64url-encoded-public-key",
    "auth": "base64url-encoded-auth-secret"
  },
  "device_name": "iPhone 15 Pro",
  "user_agent": "Mozilla/5.0..."
}
```

**Response:**
```json
{
  "id": "uuid",
  "endpoint": "https://...",
  "device_name": "iPhone 15 Pro",
  "created_at": "2026-06-07T12:00:00Z"
}
```

**Status Codes:**
- `201 Created` - Subscription registered
- `400 Bad Request` - Invalid subscription data
- `401 Unauthorized` - Authentication required
- `409 Conflict` - Subscription already exists

### List Subscriptions

**GET /api/push-subscriptions**

List user's push subscriptions.

**Response:**
```json
{
  "subscriptions": [
    {
      "id": "uuid",
      "endpoint": "https://...",
      "device_name": "iPhone 15 Pro",
      "created_at": "2026-06-07T12:00:00Z",
      "is_active": true
    }
  ]
}
```

**Status Codes:**
- `200 OK` - Success
- `401 Unauthorized` - Authentication required

### Delete Subscription

**DELETE /api/push-subscriptions/{id}**

Remove a push subscription.

**Status Codes:**
- `204 No Content` - Deleted
- `401 Unauthorized` - Authentication required
- `404 Not Found` - Subscription not found

### Send Notification

**POST /api/push-notifications**

Send push notifications (admin only).

**Request:**
```json
{
  "title": "New Message",
  "body": "You have a new message from John",
  "url": "/chat/123",
  "user_ids": ["user-1", "user-2"]
}
```

**Response:**
```json
{
  "sent": 2,
  "failed": 0,
  "total": 2
}
```

**Status Codes:**
- `200 OK` - Success
- `400 Bad Request` - Invalid payload
- `401 Unauthorized` - Authentication required
- `403 Forbidden` - Admin role required
- `429 Too Many Requests` - Rate limit exceeded

---

## Troubleshooting Guide

### Common Issues

#### iOS-Specific Issues

##### "No notifications on iOS"

**Symptoms:** Notifications work on desktop/Android but not on iOS.

**Check:**

1. **iOS Version**
   ```javascript
   // Check in Safari console
   navigator.userAgent.includes('iPhone') || navigator.userAgent.includes('iPad')
   ```
   - Must be iOS 16.4 or later
   - Update iOS if needed

2. **Standalone Mode**
   ```javascript
   // Check in Safari console
   window.navigator.standalone === true
   ```
   - Must be `true` for push to work
   - If `false`, app is running in Safari tab (not supported)
   - Install on Home Screen and launch from there

3. **Browser**
   - Must be Safari
   - Chrome/Firefox on iOS do NOT support Web Push
   - They use WebKit but lack full Push API support

4. **HTTPS**
   ```javascript
   // Check in console
   window.location.protocol
   ```
   - Must be `https:`
   - For testing, use ngrok or similar HTTPS tunnel

**Solutions:**
- Update iOS to 16.4+
- Install PWA on Home Screen
- Launch from Home Screen icon
- Use Safari (not Chrome/Firefox)
- Test on real device (not Simulator)

##### "Empty subscription endpoint"

**Symptoms:** `subscription.endpoint` is empty or undefined.

**Causes:**
1. Testing on iOS Simulator (not supported)
2. VAPID key rejected by Apple
3. Not in standalone mode

**Solutions:**
1. Test on real iPhone/iPad
2. Verify VAPID key format (65-byte uncompressed P-256)
3. Launch from Home Screen

##### "Permission prompt not showing"

**Symptoms:** No permission dialog when clicking "Enable".

**Cause:** Permission prompt must be triggered by user gesture.

**Wrong:**
```javascript
// ❌ Don't request on page load
mounted() {
  Notification.requestPermission();  // Blocked by browser
}
```

**Correct:**
```javascript
// ✓ Request on user click
methods: {
  async subscribe() {
    const permission = await Notification.requestPermission();
    // ...
  }
}
```

#### VAPID Key Issues

##### "VAPID not configured"

**Symptoms:** Server returns 503 for `/api/vapid-public-key`.

**Solution:**
```bash
# Check environment variable
echo $VAPID_PRIVATE_KEY

# If empty, add to .env
echo 'VAPID_PRIVATE_KEY="-----BEGIN PRIVATE KEY-----
...
-----END PRIVATE KEY-----
"' >> .env

# Restart server
make run
```

##### "VapidPkHashMismatch"

**Symptoms:** Apple returns 400 with `{"reason":"VapidPkHashMismatch"}`.

**Cause:** VAPID key changed after subscription.

**Solution:**
1. Store VAPID key hash in localStorage
2. Detect changes and re-subscribe

```javascript
// Check on page load
const storedKey = localStorage.getItem('vapidKey');
const currentKey = await fetchVapidKey();

if (storedKey && storedKey !== currentKey) {
  // Key changed - clear old subscription
  await subscription.unsubscribe();
  localStorage.removeItem('vapidKey');
}
```

##### "BadJwtToken"

**Symptoms:** Apple returns 403 with `{"reason":"BadJwtToken"}`.

**Causes:**
1. VAPID JWT signature invalid
2. VAPID claims malformed
3. VAPID private key doesn't match public key

**Solution:**
```python
# Verify VAPID claims
from baseweb.vapid import get_vapid_claims

claims = get_vapid_claims(subscription.endpoint)
# Should include: sub, aud, exp
```

#### Subscription Issues

##### "Subscription already exists"

**Symptoms:** Server returns 409 for POST /api/push-subscriptions.

**Solution:**
```javascript
// Check existing subscription before creating new one
const registration = await navigator.serviceWorker.ready;
const existing = await registration.pushManager.getSubscription();

if (existing) {
  // Use existing subscription
  await syncWithServer(existing);
} else {
  // Create new subscription
  await subscribe();
}
```

##### "Notifications not received"

**Symptoms:** Server returns 200 but no notification on device.

**Check:**

1. **Device Settings**
   - iOS: Settings → App → Notifications → Allow Notifications
   - Android: Settings → Apps → App → Notifications

2. **Do Not Disturb**
   - Disable Focus/Do Not Disturb mode

3. **Background App Refresh**
   - iOS: Settings → General → Background App Refresh

4. **Network Connectivity**
   - Verify device can reach push service
   - Check firewall rules for `web.push.apple.com`

#### Server Issues

##### "Server returns 401 Unauthorized"

**Symptoms:** API requests fail with 401.

**Solution:**
```python
# Implement authenticator
def get_current_user():
    # Your authentication logic
    return user_id

server.authenticator = get_current_user
```

##### "Server returns 403 Forbidden"

**Symptoms:** POST /api/push-notifications returns 403.

**Cause:** User doesn't have admin role.

**Solution:**
```python
# Implement admin check
def is_admin():
    return getattr(request, 'is_admin', False)

# Set on request in authenticator
def get_current_user():
    # ... auth logic ...
    request.is_admin = user.has_role('admin')
    return user.id
```

### Debug Tools

#### Browser Console

```javascript
// Check VAPID key
fetch('/api/vapid-public-key')
  .then(r => r.json())
  .then(d => console.log('VAPID key:', d.public_key));

// Check service worker
navigator.serviceWorker.ready.then(reg => {
  console.log('SW registration:', reg);
  return reg.pushManager.getSubscription();
}).then(sub => {
  console.log('Subscription:', sub);
});

// Check permission
console.log('Permission:', Notification.permission);

// Check iOS standalone mode
console.log('Standalone:', window.navigator.standalone);
console.log('Display mode:', window.matchMedia('(display-mode: standalone)').matches);
```

#### Server Logs

```bash
# Check for VAPID loading
grep "VAPID" logs/server.log

# Check for subscription creation
grep "Created subscription" logs/server.log

# Check for push errors
grep "Error sending push" logs/server.log
```

#### Testing with curl

```bash
# Test VAPID endpoint
curl https://your-domain.com/api/vapid-public-key

# Test subscription creation (with auth)
curl -X POST https://your-domain.com/api/push-subscriptions \
  -H "Content-Type: application/json" \
  -H "Cookie: session=your-session" \
  -d '{
    "endpoint": "https://web.push.apple.com/...",
    "keys": {
      "p256dh": "...",
      "auth": "..."
    }
  }'

# Test notification sending (with admin auth)
curl -X POST https://your-domain.com/api/push-notifications \
  -H "Content-Type: application/json" \
  -H "Cookie: session=admin-session" \
  -d '{
    "title": "Test",
    "body": "Hello",
    "user_ids": ["user-1"]
  }'
```

### Testing Checklist

- [ ] VAPID keys generated and stored in environment
- [ ] VAPID public key endpoint returns 200
- [ ] Testing on real iPhone/iPad (not Simulator)
- [ ] iOS 16.4 or later confirmed
- [ ] App launched from Home Screen (standalone mode)
- [ ] HTTPS/ngrok tunnel for mobile testing
- [ ] User gesture triggers subscription (not page load)
- [ ] VAPID key hash stored and compared on subsequent visits
- [ ] Subscription synced with server on page load
- [ ] Push notification received on device
- [ ] Notification click opens app to correct page
- [ ] Badge updates correctly

### Known Limitations

- **iOS Simulator:** Does not support Web Push notifications
- **Network restrictions:** Some corporate networks may block `web.push.apple.com`
- **Temporary VAPID keys:** If `VAPID_PRIVATE_KEY` is not set, temporary keys are generated on each server restart. This breaks existing subscriptions. Always set a persistent VAPID_PRIVATE_KEY in production.
- **Payload size:** Push notifications have a ~4KB payload limit. Keep messages short.
- **Rate limits:** Default limits are 10/hour and 50/day per user.

---

## Additional Resources

- [Web Push Protocol (RFC 8030)](https://tools.ietf.org/html/rfc8030)
- [VAPID Protocol (RFC 8292)](https://tools.ietf.org/html/rfc8292)
- [Apple Push Notification Service](https://developer.apple.com/documentation/usernotifications/sending_web_push_notifications)
- [MDN: Push API](https://developer.mozilla.org/en-US/docs/Web/API/Push_API)
- [MDN: Service Worker API](https://developer.mozilla.org/en-US/docs/Web/API/Service_Worker_API)

---

*Document version: 2.0.0*
*Last updated: 2026-06-07*
*Satisfies: R88 - Push notification documentation*