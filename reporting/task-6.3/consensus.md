# Consensus Report: task-6.3 Push Notification Frontend Integration

## Overview
This document summarizes the agreed-upon implementation strategy for integrating push notifications into the Baseweb frontend, ensuring compatibility with the existing backend infrastructure (task-6.2) and meeting strict iOS Safari PWA requirements.

## Agreed Implementation Flow

### 1. Core Subscription Sequence
The frontend will follow this precise sequence to ensure browser compatibility:
1. **Compatibility Check**: Verify `PushManager` support and iOS PWA status (`window.navigator.standalone`).
2. **VAPID Retrieval**: Fetch the public key from `GET /api/vapid-public-key`.
3. **User Interaction**: Present a "Subscribe" button. The actual permission request MUST happen inside this button's click handler.
4. **Permission Request**: Call `Notification.requestPermission()`.
5. **Browser Subscription**: Convert VAPID key to `Uint8Array` and call `registration.pushManager.subscribe()`.
6. **Backend Sync**: Convert subscription keys (`p256dh`, `auth`) to `base64url` strings and send to `POST /api/push-subscriptions`.

### 2. Domain-Specific Requirements

#### UX & UI (ux-push-notifications.md)
- **Conditional UI**: 
    - If in standalone mode: Show "Enable Notifications" button.
    - If NOT in standalone mode (iOS): Show instruction to "Add to Home Screen" to enable notifications.
    - If browser unsupported: Hide notification UI.
- **Button States**: Implement "Subscribing...", "Subscribed", and "Error" states.

#### API Integration (api-push-frontend.md)
- **Data Transformations**: 
    - `base64url string` $\rightarrow$ `Uint8Array` for VAPID public key.
    - `ArrayBuffer` $\rightarrow$ `base64url string` for subscription keys.
- **Error Handling**: Treat HTTP 409 (Conflict/Duplicate) as success during registration.

#### Security (Security Review)
- **Payload Safety**: In `sw.js`, the `push` event listener must treat the payload as untrusted.
- **URL Validation**: Validate that any URL in the push payload starts with `https://` before calling `clients.openWindow()`.
- **Transport**: All API calls must be over HTTPS (already enforced by backend).

## Acceptance Criteria
- [ ] User clicks "Subscribe" in standalone PWA $\rightarrow$ Permission prompt appears.
- [ ] User grants permission $\rightarrow$ Subscription is created and synced to backend.
- [ ] Push notification received $\rightarrow$ Displays as system notification and opens correct URL on click.
- [ ] Non-standalone mode on iOS does NOT show the permission prompt but shows installation instructions.
- [ ] Service worker handles push events without introducing XSS (no `innerHTML` used for payload data).

## Approval
- API Architect: Approved
- UI/UX Designer: Approved
- Security Engineer: Approved
