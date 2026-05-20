# Push Notifications Testing Guide

## Overview

This document describes how to test push notifications in a development environment using ngrok and a real iOS device.

## Prerequisites

- **iOS 16.4 or later**: Push notifications only work on iOS 16.4+.
- **Real iPhone or iPad**: The iOS Simulator does **not** support Web Push notifications.
- **ngrok**: For HTTPS tunneling to your local development server.

## Test Setup

### 1. Set VAPID Keys

Generate VAPID keys and add them to your `.env` file:

```bash
# Generate keys
python -c "from py_vapid import Vapid01; v = Vapid01(); v.generate_keys(); print('VAPID_PRIVATE_KEY:'); print(v.private_pem().decode()); print('\nVAPID_PUBLIC_KEY:'); print(v.public_pem().decode())"
```

Add to `examples/hello-world/.env`:

```env
VAPID_PRIVATE_KEY="-----BEGIN PRIVATE KEY-----
MIGHAgEAMBMGByqGSM49AgEGCCqGSM49AwEHBG0wawIBAQQg...
-----END PRIVATE KEY-----
"
VAPID_SUBJECT="mailto:your-email@example.com"
```

### 2. Start the Development Server

```bash
cd examples/hello-world
make run
```

Verify the server logs show:
```
✓ VAPID keys loaded successfully from environment
✓ VAPID Public Key: <base64url-string>
```

### 3. Start ngrok

In a separate terminal:

```bash
ngrok http 8000
```

Copy the HTTPS URL (e.g., `https://abc123.ngrok.io`).

### 4. Install as PWA on iPhone

1. Open Safari on your iPhone.
2. Navigate to the ngrok URL.
3. Tap the **Share** button.
4. Select **"Add to Home Screen"**.
5. Tap **"Add"** in the top right.

**Important**: Push notifications only work when the app is launched from the Home Screen icon (standalone mode), not in regular Safari tabs.

### 5. Test Push Notifications

1. Launch the app from the Home Screen.
2. Navigate to **Notifications**.
3. Click **"Enable"**.
4. Accept the permission prompt.
5. The status should change to **"Notifications Enabled"**.

### 6. Send a Test Notification

Use `curl` to send a test notification:

```bash
curl -X POST https://abc123.ngrok.io/api/push-notifications \
  -H "Content-Type: application/json" \
  -H "Cookie: <your-session-cookie>" \
  -d '{
    "title": "Test Notification",
    "body": "Hello from baseweb!",
    "url": "https://abc123.ngrok.io"
  }'
```

**Note**: You need to be authenticated to send notifications. In the hello-world example, a dummy authenticator is used that sets `user_id = "hello-world-user"`.

## Troubleshooting

### Empty Subscription Endpoint

If `subscription.endpoint` is empty:

1. **Check iOS version**: Must be 16.4 or later.
2. **Check PWA mode**: Must be launched from Home Screen, not Safari.
3. **Check HTTPS**: Must use HTTPS (ngrok provides this).
4. **Check VAPID key**: Must be 65 bytes uncompressed P-256 key.
5. **Test on real device**: iOS Simulator does not support Web Push.

### Permission Prompt Not Showing

- The permission prompt must be triggered by a **user gesture** (click/tap).
- We pre-fetch the VAPID key on page load to ensure `subscribe()` is called immediately after `Notification.requestPermission()`.

### Notifications Not Received

1. Check the device is not in **Do Not Disturb** mode.
2. Check the app has notification permission in iOS Settings.
3. Verify the push service endpoint is reachable from the device.

## Known Limitations

- **iOS Simulator**: Does not support Web Push notifications.
- **Network restrictions**: Some networks may block `web.push.apple.com`.
- **Temporary keys**: If `VAPID_PRIVATE_KEY` is not set, temporary keys are generated on each server restart. This breaks existing subscriptions.

## Production Deployment

For production:

1. Use a **persistent VAPID key** (store in environment variables).
2. Use a **stable domain** with SSL certificate.
3. Consider using a **push service provider** for reliability.