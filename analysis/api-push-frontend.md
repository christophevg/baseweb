# API Analysis: Push Notification Frontend Integration

**Date:** 2026-05-20
**Task:** task-6.3 - Push notification frontend integration
**Related Documents:** [analysis/api-push-notifications.md](/Users/xtof/Workspace/agentic/baseweb/analysis/api-push-notifications.md)

## Summary

This document defines the frontend integration requirements and sequence for implementing push notifications in the baseweb PWA. It bridges the gap between the browser's Push API and the baseweb backend infrastructure.

---

## Subscription Sequence

The frontend must follow this precise sequence to ensure successful registration, especially for iOS Safari PWA compatibility.

### 1. Compatibility Check
Before attempting subscription, the frontend must verify:
- **Browser Support**: `PushManager` exists in `window`.
- **Service Worker**: `serviceWorker` exists in `navigator`.
- **Platform Constraints (iOS)**:
    - Must be iOS 16.4+
    - Must be running in `standalone` mode (installed as PWA)
    - Must be launched from the Home Screen

### 2. Retrieve VAPID Public Key
The frontend needs the server's public key to initiate the subscription with the push service.
- **Endpoint**: `GET /api/vapid-public-key`
- **Action**: Fetch the `public_key` and cache it for the session.
- **Error Handling**: If 404 is returned, notifications are not configured on the server; disable the "Enable Notifications" UI.

### 3. User Gesture & Permission
Push notifications require an explicit user gesture (e.g., button click) to trigger the permission prompt.
- **Action**: Call `Notification.requestPermission()`.
- **Condition**: Must be called within a user-initiated event handler.
- **Handling**:
    - `granted`: Proceed to subscription.
    - `denied`/`ignored`: Update UI to show notifications are disabled.

### 4. Browser Subscription
Once permission is granted, the frontend interacts with the browser's Push Manager.
- **Prerequisite**: Wait for the Service Worker to be ready (`navigator.serviceWorker.ready`).
- **Action**: 
  ```javascript
  const subscription = await registration.pushManager.subscribe({
    userVisibleOnly: true,
    applicationServerKey: urlBase64ToUint8Array(vapidPublicKey)
  });
  ```
- **Key Detail**: The `vapidPublicKey` from the API must be converted from a base64url string to a `Uint8Array`.

### 5. Backend Registration
The resulting subscription object must be sent to the backend to enable targeted notifications.
- **Endpoint**: `POST /api/push-subscriptions`
- **Headers**: `Authorization: Bearer <token>`, `Content-Type: application/json`
- **Payload Transformation**:
  The `subscription` object returned by the browser contains `ArrayBuffer` keys. These **must** be encoded to base64url strings before sending.
  
| Browser Field | Backend Field | Transformation |
|---------------|---------------|-----------------|
| `subscription.endpoint` | `endpoint` | None (String) |
| `subscription.getKey('p256dh')` | `keys.p256dh` | ArrayBuffer $\rightarrow$ base64url |
| `subscription.getKey('auth')` | `keys.auth` | ArrayBuffer $\rightarrow$ base64url |

---

## Data Handling & Transformation

### VAPID Key Conversion
The backend provides the VAPID key as a base64url string. The browser requires a `Uint8Array`.

**Required Helper:**
```javascript
function urlBase64ToUint8Array(base64String) {
  const padding = '='.repeat((4 - base64String.length % 4) % 4);
  const base64 = (base64String + padding).replace(/-/g, '+').replace(/_/g, '/');
  const rawData = window.atob(base64);
  const outputArray = new Uint8Array(rawData.length);
  for (let i = 0; i < rawData.length; ++i) {
    outputArray[i] = rawData.charCodeAt(i);
  }
  return outputArray;
}
```

### Subscription Key Encoding
The `p256dh` and `auth` keys must be sent as strings.

**Required Helper:**
```javascript
function arrayBufferToBase64Url(buffer) {
  const bytes = new Uint8Array(buffer);
  let binary = '';
  for (const byte of bytes) binary += String.fromCharCode(byte);
  return window.btoa(binary)
    .replace(/\+/g, '-')
    .replace(/\//g, '_')
    .replace(/=+$/, '');
}
```

---

## Error Handling Matrix

| Scenario | API/Browser Response | Frontend Action | User Message |
|-----------|---------------------|-------------------|---------------|
| **VAPID missing** | `GET ...` $\rightarrow$ 404 | Hide "Enable Notifications" button | N/A |
| **Permission Denied** | `denied` | Mark as "Blocked" in settings | "Please enable notifications in browser settings" |
| **Not a PWA (iOS)** | Detection logic | Show installation guide | "Add baseweb to your home screen to enable notifications" |
| **Auth Failure** | `POST ...` $\rightarrow$ 401 | Redirect to login | "Please log in to enable notifications" |
| **Duplicate Sub** | `POST ...` $\rightarrow$ 409 | Treat as success (already registered) | "Notifications enabled" |
| **Invalid Data** | `POST ...` $\rightarrow$ 400 | Log error, alert user | "There was a problem registering your device" |
| **Network Error** | Fetch failure | Retry with exponential backoff | "Connection lost. Retrying..." |

---

## Action Items for Frontend Implementation

- [ ] Implement `canUsePushNotifications()` check including iOS PWA detection.
- [ ] Create "Notification Settings" UI component with toggle and status indicators.
- [ ] Implement VAPID key retrieval and transformation logic.
- [ ] Implement the `subscribeToPush` flow within a user gesture handler.
- [ ] Implement `ArrayBuffer` to base64url encoding for subscription keys.
- [ ] Integrate with existing authentication token management for `POST` requests.
- [ ] Add telemetry/logging for subscription success and failure rates.
