# Web Push Notifications Troubleshooting Guide

## Overview

This document covers common issues and solutions for Web Push notifications, with a focus on iOS Safari PWAs.

## iOS-Specific Requirements

### Critical Limitations

1. **iOS Simulator does NOT support Web Push**
   - You must test on a real iPhone or iPad
   - iOS 16.4 or later is required
   - The Simulator shows empty subscription endpoints

2. **Standalone Mode Required**
   - Push notifications only work when launched from Home Screen
   - Standard Safari tabs cannot receive push notifications
   - Third-party browsers (Chrome, Firefox on iOS) use WebKit but cannot receive push

3. **User Gesture Required**
   - `Notification.requestPermission()` must be called from a user gesture (click/tap)
   - Safari requires `subscribe()` to be called immediately after the permission prompt
   - Pre-fetch the VAPID key before the user clicks to ensure immediate subscription

4. **HTTPS Required**
   - Push API requires HTTPS (or localhost)
   - For mobile testing, use ngrok or similar HTTPS tunnel

### Testing Setup

```bash
# 1. Start development server
cd examples/hello-world && make run

# 2. Start ngrok tunnel (separate terminal)
ngrok http 8000

# 3. On iPhone Safari, navigate to ngrok URL
# 4. Add to Home Screen
# 5. Launch from Home Screen
# 6. Navigate to Notifications page and Enable
```

## VAPID Key Issues

### VAPID Key Format

The VAPID public key must be a 65-byte uncompressed P-256 point, base64url-encoded:

```python
# Correct: Extract raw bytes from cryptography object
from cryptography.hazmat.primitives import serialization

pub_bytes = vapid.public_key.public_bytes(
    encoding=serialization.Encoding.X962,
    format=serialization.PublicFormat.UncompressedPoint
)
public_key = base64.urlsafe_b64encode(pub_bytes).decode().rstrip('=')
```

**Common Mistakes:**
- Returning PEM format instead of raw bytes
- Using compressed point format
- Including padding in base64url

### VAPID Key Loading

VAPID keys must be loaded at server startup, not lazy-loaded:

```python
# Correct: Load at module import
_vapid_instance = None

def _init_vapid():
    global _vapid_instance
    key_pem = os.environ.get("VAPID_PRIVATE_KEY")
    if key_pem:
        key_content = key_pem.strip().strip('"').strip("'")
        _vapid_instance = Vapid01.from_pem(key_content.encode())
    else:
        _vapid_instance = Vapid01()
        _vapid_instance.generate_keys()

_init_vapid()  # Called at module import
```

### VAPID Key Consistency

**Critical:** The VAPID key used for subscription must match the key used for sending:

1. **Store VAPID key hash in localStorage** - Detect when server's key changes
2. **Auto-clear old subscription on key change** - Force re-subscription
3. **Use persistent keys** - Set VAPID_PRIVATE_KEY in environment, don't generate temporary keys

```javascript
// Detect VAPID key change
const storedKey = localStorage.getItem('vapidKey');
const currentKey = await fetchVapidKey();

if (storedKey && storedKey !== currentKey) {
    // VAPID key changed - clear old subscription
    await subscription.unsubscribe();
    localStorage.removeItem('vapidKey');
}
```

## Common Errors

### `BadJwtToken`

**Symptom:** Apple's push service returns 403 with `{"reason":"BadJwtToken"}`

**Causes:**
1. VAPID JWT signature is invalid
2. VAPID claims are malformed
3. VAPID private key doesn't match public key used for subscription

**Solutions:**
```python
# Use Vapid01 instance directly for signing (not PEM string)
from pywebpush import webpush_async

response = await webpush_async(
    subscription_info=subscription,
    data=json.dumps(payload),
    vapid_private_key=vapid_instance,  # Vapid01 instance, not PEM string
    vapid_claims={
        'sub': 'mailto:admin@example.com',  # Valid email or URL
        'aud': 'https://web.push.apple.com',  # Push service origin
        'exp': int(time.time()) + 43200  # Max 24 hours
    }
)
```

### `VapidPkHashMismatch`

**Symptom:** Apple returns 400 with `{"reason":"VapidPkHashMismatch"}`

**Cause:** The VAPID public key used during subscription doesn't match the key used for sending

**Solutions:**
1. Ensure VAPID keys are consistent (not regenerated on restart)
2. Re-subscribe after changing VAPID keys
3. Store VAPID key hash and compare before sending

### Empty Subscription Endpoint

**Symptom:** `subscription.endpoint` is empty or undefined

**Causes:**
1. Testing on iOS Simulator (not supported)
2. VAPID key was rejected by Apple
3. Not in standalone mode (PWA not installed)

**Solutions:**
1. Test on real iPhone/iPad with iOS 16.4+
2. Verify VAPID key format (65-byte uncompressed P-256)
3. Launch from Home Screen (standalone mode)

### `Could not deserialize key data`

**Symptom:** `pywebpush` throws ASN.1 parsing error

**Cause:** Passing PEM string to `webpush_async()` instead of Vapid01 instance

**Solution:**
```python
# Wrong: PEM string
response = await webpush_async(
    vapid_private_key=vapid_instance.private_pem()  # Wrong!
)

# Correct: Vapid01 instance
response = await webpush_async(
    vapid_private_key=vapid_instance  # Correct
)
```

## Subscription Management

### Preventing Redundant API Calls

Store subscription state in Vuex to avoid re-fetching on every page visit:

```javascript
// Vuex store module for push notifications
const pushModule = {
  state: {
    vapidKey: null,          // Cached VAPID key
    subscription: null,      // Browser subscription
    subscriptionStatus: null // 'unsubscribed' | 'subscribed' | 'error'
  },
  actions: {
    async fetchVapidKey(context) {
      if (context.state.vapidKey) return context.state.vapidKey; // Cached
      const response = await fetch('/api/vapid-public-key');
      const data = await response.json();
      context.commit('SET_VAPID_KEY', data.public_key);
      return data.public_key;
    }
  }
}
```

### Handling Server Restarts

Server restarts clear in-memory subscription storage. Auto-sync on page load:

```javascript
async checkSubscription(context) {
  const registration = await navigator.serviceWorker.ready;
  const subscription = await registration.pushManager.getSubscription();
  
  if (subscription) {
    // Re-sync with server (may have restarted)
    await context.dispatch('syncSubscriptionWithServer', subscription);
  }
}
```

### Detecting VAPID Key Changes

```javascript
// On page load, check if VAPID key changed
const storedKey = localStorage.getItem('vapidKey');
const currentKey = context.state.vapidKey;

if (storedKey && storedKey !== currentKey) {
  // Key changed - clear old subscription
  await subscription.unsubscribe();
  localStorage.removeItem('vapidKey');
}
```

## Service Worker

### Push Event Handler

```javascript
// sw.js
self.addEventListener('push', (event) => {
  const payload = event.data.json();
  const title = payload.title || 'New Notification';
  
  const options = {
    body: payload.body,
    icon: payload.icon,
    badge: payload.badge,
    data: { url: payload.url },
    tag: payload.tag
  };

  event.waitUntil(
    self.registration.showNotification(title, options)
  );
});
```

### Notification Click Handler

```javascript
self.addEventListener('notificationclick', (event) => {
  event.waitUntil(
    clients.matchAll({ type: 'window' }).then((clientList) => {
      const url = event.notification.data?.url;
      if (url?.startsWith('https://')) {
        return clients.openWindow(url);
      }
      return clients.openWindow('/');
    })
  );
});
```

### Badge Management

```javascript
// Increment badge on push
self.addEventListener('push', async (event) => {
  // Show notification
  await self.registration.showNotification(title, options);
  
  // Update badge
  if ('setAppBadge' in navigator) {
    const notifications = await self.registration.getNotifications();
    await navigator.setAppBadge(notifications.length);
  }
});
```

## Testing Checklist

- [ ] VAPID keys generated and stored in environment
- [ ] VAPID public key endpoint returns 65-byte base64url string
- [ ] Testing on real iPhone/iPad (not Simulator)
- [ ] App launched from Home Screen (standalone mode)
- [ ] HTTPS/ngrok tunnel for mobile testing
- [ ] User gesture triggers subscription (not automatic on page load)
- [ ] VAPID key hash stored and compared on subsequent visits
- [ ] Subscription synced with server on page load
- [ ] Push notification received on device

## Environment Variables

```env
# Required for push notifications
VAPID_PRIVATE_KEY="-----BEGIN PRIVATE KEY-----
MIGHAgEAMBMGByqGSM49AgEGCCqGSM49AwEHBG0wawIBAQQg...
-----END PRIVATE KEY-----
"

# Contact email (shown to push service)
VAPID_SUBJECT="mailto:admin@example.com"
```

## Architecture Notes

### Why Vapid01 Instance Instead of PEM

`pywebpush` accepts either:
1. A Vapid01/Vapid instance (recommended)
2. A file path to a PEM file
3. A base64url-encoded raw private key (not PEM)

Passing a PEM string causes ASN.1 parsing errors because `from_string()` expects base64url-encoded raw bytes, not PEM format.

### Why Service Worker for Push

The Service Worker is the only component that can receive push events when:
- The app is not running
- The browser is closed
- The device is locked

The main app thread cannot receive push events directly.

### Why Vuex Store for State

Without centralized state:
- Every page visit fetches VAPID key (redundant)
- Every page visit syncs subscription (causes 409 conflicts)
- State is lost when navigating between pages

With Vuex store:
- VAPID key cached for session
- Subscription status cached centrally
- API calls happen only once per session

## References

- [Web Push Protocol (RFC 8030)](https://tools.ietf.org/html/rfc8030)
- [VAPID Protocol (RFC 8292)](https://tools.ietf.org/html/rfc8292)
- [Apple Push Notification Service](https://developer.apple.com/documentation/usernotifications/sending_web_push_notifications)
- [MDN: Push API](https://developer.mozilla.org/en-US/docs/Web/API/Push_API)
- [MDN: Service Worker API](https://developer.mozilla.org/en-US/docs/Web/API/Service_Worker_API)