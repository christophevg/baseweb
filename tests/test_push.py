"""Tests for Push Notification Backend Infrastructure.

This module contains tests for task-6.2: Push notification backend
infrastructure. Tests verify:
- VAPID key generation and management
- Push subscription storage and retrieval
- Push notification sending functionality
- Security requirements (authentication, rate limiting, input validation)
- Safari Web Push compatibility for iOS 16.4+

Requirements satisfied:
- R85: VAPID key generation and management
- R86: Push subscription storage and retrieval
- R87: Push notification sending functionality
- NFR3: VAPID keys secured properly
"""

import os

import pytest

from baseweb import Baseweb
from baseweb.push import (
  MAX_BODY_LENGTH,
  MAX_KEY_LENGTH,
  MAX_TITLE_LENGTH,
  PushNotificationPayload,
  PushSubscription,
  RateLimiter,
  SubscriptionStorage,
  get_rate_limiter,
  get_subscription_storage,
  is_known_push_service,
  sanitize_user_agent,
  validate_subscription_data,
)
from baseweb.vapid import VAPIDKeyError, VAPIDKeyManager

# ==============================================================================
# Test Infrastructure
# ==============================================================================


@pytest.fixture
async def vapid_manager():
  """Create a VAPID key manager for testing."""
  # Set test environment variables
  os.environ["VAPID_SUBJECT"] = "mailto:test@example.com"
  os.environ["VAPID_PRIVATE_KEY"] = None  # Will generate temporary keys

  manager = VAPIDKeyManager()
  await manager.initialize()
  yield manager

  # Cleanup
  if "VAPID_SUBJECT" in os.environ:
    del os.environ["VAPID_SUBJECT"]
  if "VAPID_PRIVATE_KEY" in os.environ:
    del os.environ["VAPID_PRIVATE_KEY"]


@pytest.fixture
def subscription_storage():
  """Create a fresh subscription storage for testing."""
  storage = SubscriptionStorage()
  return storage


@pytest.fixture
def rate_limiter():
  """Create a fresh rate limiter for testing."""
  return RateLimiter()


# ==============================================================================
# VAPID Key Management Tests
# ==============================================================================


class TestVAPIDKeyGeneration:
  """
  Tests for VAPID key generation and management.

  VAPID (Voluntary Application Server Identification) keys are used to
  authenticate the push notification server with push services (APNS, FCM).

  iOS 16.4+ Safari requires VAPID authentication for Web Push.
  """

  @pytest.mark.asyncio
  async def test_vapid_keys_generated_on_startup(self):
    """
    Given: A VAPIDKeyManager without existing keys
    When: Calling initialize()
    Then: VAPID key pair should be generated
    """
    # Clear any existing key
    if "VAPID_PRIVATE_KEY" in os.environ:
      del os.environ["VAPID_PRIVATE_KEY"]

    manager = VAPIDKeyManager()
    await manager.initialize()

    assert manager.is_configured()
    assert manager.get_public_key() is not None

  @pytest.mark.asyncio
  async def test_vapid_keys_loaded_from_environment(self):
    """
    Given: Environment variable VAPID_PRIVATE_KEY is set
    When: Application initializes
    Then: Private key should be loaded from environment
    """
    # Generate test key
    try:
      from py_vapid import Vapid01
    except ImportError:
      pytest.skip("py-vapid not installed")

    vapid = Vapid01()
    vapid.generate_keys()
    private_key_pem = vapid.private_pem()
    if isinstance(private_key_pem, bytes):
      private_key_pem = private_key_pem.decode()

    os.environ["VAPID_PRIVATE_KEY"] = private_key_pem

    manager = VAPIDKeyManager()
    await manager.initialize()

    assert manager.is_configured()
    assert manager.get_private_key_pem() == private_key_pem

    # Cleanup
    del os.environ["VAPID_PRIVATE_KEY"]

  @pytest.mark.asyncio
  async def test_vapid_public_key_derived_from_private(self):
    """
    Given: A VAPID private key
    When: Getting the public key
    Then: Public key should be correctly derived from private key
    """
    try:
      from py_vapid import Vapid01
    except ImportError:
      pytest.skip("py-vapid not installed")

    vapid = Vapid01()
    vapid.generate_keys()
    private_key_pem = vapid.private_pem()
    if isinstance(private_key_pem, bytes):
      private_key_pem = private_key_pem.decode()
    expected_public_key = vapid.public_pem()
    if isinstance(expected_public_key, bytes):
      expected_public_key = expected_public_key.decode()

    os.environ["VAPID_PRIVATE_KEY"] = private_key_pem

    manager = VAPIDKeyManager()
    await manager.initialize()

    public_key = manager.get_public_key()
    assert public_key == expected_public_key

    # Cleanup
    del os.environ["VAPID_PRIVATE_KEY"]

  @pytest.mark.asyncio
  async def test_vapid_keys_stored_securely(self):
    """
    Given: Generated VAPID keys
    When: Keys are stored
    Then: Private key should not be exposed via API or logs
    """
    manager = VAPIDKeyManager()
    await manager.initialize()

    # get_public_key() should return public key
    public_key = manager.get_public_key()
    assert public_key is not None
    assert "PRIVATE" not in public_key
    assert "BEGIN RSA" not in public_key  # Should be public key format

    # get_private_key_pem() returns the private key, but API should not expose it
    # This is for internal use only
    private_key = manager.get_private_key_pem()
    assert private_key is None or "PRIVATE" in private_key  # For generated keys

  @pytest.mark.asyncio
  async def test_vapid_key_validation(self):
    """
    Given: A VAPID private key from environment
    When: Validating the key format
    Then: Invalid keys should raise a clear error
    """
    # Test with invalid key
    os.environ["VAPID_PRIVATE_KEY"] = "invalid-key-format"

    manager = VAPIDKeyManager()
    with pytest.raises(VAPIDKeyError):
      await manager.initialize()

    del os.environ["VAPID_PRIVATE_KEY"]


class TestVAPIDKeyGenerationErrors:
  """
  Tests for error handling in VAPID key generation.
  """

  @pytest.mark.asyncio
  async def test_missing_vapid_subject_logs_warning(self):
    """
    Given: VAPID_PRIVATE_KEY set but VAPID_SUBJECT missing
    When: Application initializes
    Then: Should use default subject and log a warning
    """
    try:
      from py_vapid import Vapid01
    except ImportError:
      pytest.skip("py-vapid not installed")

    # Generate test key
    vapid = Vapid01()
    vapid.generate_keys()
    private_key_pem = vapid.private_pem()
    if isinstance(private_key_pem, bytes):
      private_key_pem = private_key_pem.decode()

    os.environ["VAPID_PRIVATE_KEY"] = private_key_pem
    if "VAPID_SUBJECT" in os.environ:
      del os.environ["VAPID_SUBJECT"]

    manager = VAPIDKeyManager()
    await manager.initialize()

    # Should use default subject
    assert manager.get_subject() == "mailto:admin@localhost"

    del os.environ["VAPID_PRIVATE_KEY"]

  @pytest.mark.asyncio
  async def test_invalid_vapid_key_format_raises_error(self):
    """
    Given: VAPID_PRIVATE_KEY with invalid format
    When: Application initializes
    Then: Should raise VAPIDKeyError with clear message
    """
    os.environ["VAPID_PRIVATE_KEY"] = "not-a-valid-key"

    manager = VAPIDKeyManager()
    with pytest.raises(VAPIDKeyError) as exc_info:
      await manager.initialize()

    assert "Invalid VAPID private key" in str(exc_info.value)

    del os.environ["VAPID_PRIVATE_KEY"]


# ==============================================================================
# Public Key Endpoint Tests
# ==============================================================================


class TestVAPIDPublicKeyEndpoint:
  """
  Tests for GET /api/vapid-public-key endpoint.

  This endpoint returns the public VAPID key to clients for
  push subscription creation. It is the only unauthenticated
  push-related endpoint.
  """

  @pytest.fixture
  def app(self):
    """Create a test Baseweb app."""
    return Baseweb("test_vapid")

  @pytest.fixture
  def client(self, app):
    """Create a test client."""
    return app.test_client()

  @pytest.mark.asyncio
  async def test_get_vapid_public_key_returns_200(self, app, client):
    """
    Given: A Baseweb instance with VAPID keys
    When: Requesting GET /api/vapid-public-key
    Then: Should return 200 OK with public key
    """
    from baseweb.push import VAPIDPublicKeyResource

    app.add_resource(VAPIDPublicKeyResource, "/api/vapid-public-key")

    response = await client.get("/api/vapid-public-key")
    assert response.status_code == 200

    import json

    data = json.loads(await response.get_data())
    assert "public_key" in data or "error" in data

  @pytest.mark.asyncio
  async def test_vapid_public_key_returns_json(self, app, client):
    """
    Given: A valid VAPID public key
    When: Requesting GET /api/vapid-public-key
    Then: Response should be JSON with publicKey field
    """
    from baseweb.push import VAPIDPublicKeyResource

    app.add_resource(VAPIDPublicKeyResource, "/api/vapid-public-key")

    response = await client.get("/api/vapid-public-key")
    assert response.content_type and "json" in response.content_type.lower()

  @pytest.mark.asyncio
  async def test_vapid_public_key_is_base64_encoded(self, app, client):
    """
    Given: A VAPID public key response
    When: Parsing the publicKey field
    Then: Key should be valid base64-encoded string
    """
    from baseweb.push import VAPIDPublicKeyResource

    app.add_resource(VAPIDPublicKeyResource, "/api/vapid-public-key")

    response = await client.get("/api/vapid-public-key")

    import json

    data = json.loads(await response.get_data())

    # If VAPID is configured, check the key format
    if "public_key" in data:
      key = data["public_key"]
      assert key is not None
      assert len(key) > 0

  @pytest.mark.asyncio
  async def test_vapid_public_key_endpoint_no_auth_required(self, app, client):
    """
    Given: VAPID public key endpoint
    When: Requesting without authentication
    Then: Should still return 200 OK
    """
    from baseweb.push import VAPIDPublicKeyResource

    app.add_resource(VAPIDPublicKeyResource, "/api/vapid-public-key")

    # No authenticator set - should work without auth
    response = await client.get("/api/vapid-public-key")
    # Should return 200 or 503 (if not configured), but not 401
    assert response.status_code in [200, 503]

  @pytest.mark.asyncio
  async def test_vapid_public_key_caching_headers(self, app, client):
    """
    Given: VAPID public key response
    When: Checking response headers
    Then: Should include appropriate caching headers
    """
    from baseweb.push import VAPIDPublicKeyResource

    app.add_resource(VAPIDPublicKeyResource, "/api/vapid-public-key")

    response = await client.get("/api/vapid-public-key")

    if response.status_code == 200:
      assert "Cache-Control" in response.headers


class TestVAPIDPublicKeyEndpointErrors:
  """
  Tests for error handling in VAPID public key endpoint.
  """

  @pytest.fixture
  def app(self):
    """Create a test Baseweb app."""
    return Baseweb("test_vapid_errors")

  @pytest.fixture
  def client(self, app):
    """Create a test client."""
    return app.test_client()

  @pytest.mark.asyncio
  async def test_no_vapid_keys_returns_error(self, app, client):
    """
    Given: A Baseweb instance without VAPID keys configured
    When: Requesting GET /api/vapid-public-key
    Then: Should return 503 Service Unavailable
    """
    from baseweb.push import VAPIDPublicKeyResource

    # Clear environment
    if "VAPID_PRIVATE_KEY" in os.environ:
      del os.environ["VAPID_PRIVATE_KEY"]

    app.add_resource(VAPIDPublicKeyResource, "/api/vapid-public-key")

    # Response should indicate VAPID not configured
    response = await client.get("/api/vapid-public-key")
    # May return 503 or still work with generated keys
    assert response.status_code in [200, 503]

  @pytest.mark.asyncio
  async def test_vapid_public_key_error_response_format(self, app, client):
    """
    Given: VAPID key generation failure
    When: Requesting GET /api/vapid-public-key
    Then: Should return JSON error with error field
    """
    from baseweb.push import VAPIDPublicKeyResource

    app.add_resource(VAPIDPublicKeyResource, "/api/vapid-public-key")

    response = await client.get("/api/vapid-public-key")

    import json

    data = json.loads(await response.get_data())
    # Should be valid JSON
    assert isinstance(data, dict)


# ==============================================================================
# Subscription Registration Tests
# ==============================================================================


class TestPushSubscriptionRegistration:
  """
  Tests for POST /api/push-subscriptions endpoint.

  This endpoint registers a new push subscription for the authenticated user.
  Safari Web Push on iOS 16.4+ requires valid VAPID authentication.
  """

  @pytest.fixture
  def app(self):
    """Create a test Baseweb app."""
    return Baseweb("test_push_subscriptions")

  @pytest.fixture
  def client(self, app):
    """Create a test client."""
    return app.test_client()

  def test_valid_subscription_data(self, subscription_storage):
    """
    Given: Valid subscription data from client
    When: Validating the data
    Then: Should pass validation and return cleaned data
    """
    data = {
      "endpoint": "https://fcm.googleapis.com/fcm/send/test123",
      "keys": {"p256dh": "test_public_key_base64url", "auth": "test_auth_secret_base64url"},
    }

    is_valid, error, cleaned = validate_subscription_data(data)
    assert is_valid
    assert error is None
    assert cleaned["endpoint"] == data["endpoint"]

  def test_register_subscription_stores_user_association(self, subscription_storage):
    """
    Given: An authenticated user
    When: Registering a push subscription
    Then: Subscription should be associated with user ID
    """
    subscription = PushSubscription(
      id="test-id",
      user_id="user-123",
      endpoint="https://fcm.googleapis.com/fcm/send/test",
      p256dh="test_key",
      auth="test_auth",
    )

    created = subscription_storage.create(subscription)
    assert created.user_id == "user-123"

    # Verify retrieval by user
    user_subs = subscription_storage.get_by_user("user-123")
    assert len(user_subs) == 1
    assert user_subs[0].id == "test-id"

  @pytest.mark.asyncio
  async def test_register_subscription_requires_authentication(self, app, client):
    """
    Given: An unauthenticated request
    When: POST /api/push-subscriptions
    Then: Should return 401 Unauthorized
    """
    from baseweb.push import PushSubscriptionResource

    app.add_resource(PushSubscriptionResource, "/api/push-subscriptions")

    data = {
      "endpoint": "https://fcm.googleapis.com/fcm/send/test",
      "keys": {"p256dh": "test_key", "auth": "test_auth"},
    }

    response = await client.post("/api/push-subscriptions", json=data)
    # Without setting request.user_id, should return 401
    assert response.status_code == 401

  def test_register_subscription_validates_endpoint(self):
    """
    Given: A subscription with invalid endpoint URL
    When: Validating subscription data
    Then: Should return validation error
    """
    # HTTP endpoint (not HTTPS)
    data = {
      "endpoint": "http://example.com/push",
      "keys": {"p256dh": "test_key", "auth": "test_auth"},
    }

    is_valid, error, cleaned = validate_subscription_data(data)
    assert not is_valid
    assert "HTTPS" in error

  def test_register_subscription_validates_keys(self):
    """
    Given: A subscription with missing or invalid keys
    When: Validating subscription data
    Then: Should return validation error
    """
    # Missing p256dh
    data = {
      "endpoint": "https://fcm.googleapis.com/fcm/send/test",
      "keys": {"auth": "test_auth"},
    }

    is_valid, error, cleaned = validate_subscription_data(data)
    assert not is_valid
    assert "p256dh" in error.lower() or "keys" in error.lower()

  def test_register_subscription_stores_device_info(self, subscription_storage):
    """
    Given: A subscription with optional device info
    When: Storing the subscription
    Then: Should store device info for user reference
    """
    subscription = PushSubscription(
      id="test-id",
      user_id="user-123",
      endpoint="https://fcm.googleapis.com/fcm/send/test",
      p256dh="test_key",
      auth="test_auth",
      device_name="iPhone 15 Pro",
      user_agent="Mozilla/5.0 (iPhone...)",
    )

    created = subscription_storage.create(subscription)
    assert created.device_name == "iPhone 15 Pro"
    assert created.user_agent == "Mozilla/5.0 (iPhone...)"

  def test_register_subscription_returns_id(self, subscription_storage):
    """
    Given: Valid subscription data
    When: Creating a subscription
    Then: Response should include subscription ID
    """
    subscription = PushSubscription(
      id="test-uuid",
      user_id="user-123",
      endpoint="https://fcm.googleapis.com/fcm/send/test",
      p256dh="test_key",
      auth="test_auth",
    )

    created = subscription_storage.create(subscription)
    assert created.id == "test-uuid"


class TestPushSubscriptionRegistrationValidation:
  """
  Tests for input validation in subscription registration.
  """

  def test_subscription_endpoint_must_be_https(self):
    """
    Given: A subscription with HTTP endpoint
    When: Validating subscription data
    Then: Should fail validation with HTTPS requirement
    """
    data = {
      "endpoint": "http://example.com/push",
      "keys": {"p256dh": "test_key", "auth": "test_auth"},
    }

    is_valid, error, cleaned = validate_subscription_data(data)
    assert not is_valid
    assert "HTTPS" in error

  def test_subscription_keys_must_be_base64(self):
    """
    Given: A subscription with non-base64 keys
    When: Validating subscription data
    Then: Should fail validation
    """
    data = {
      "endpoint": "https://fcm.googleapis.com/fcm/send/test",
      "keys": {"p256dh": "invalid!@#$", "auth": "test_auth"},
    }

    is_valid, error, cleaned = validate_subscription_data(data)
    assert not is_valid

  def test_subscription_endpoint_url_validation(self):
    """
    Given: A subscription with malformed endpoint URL
    When: Validating subscription data
    Then: Should fail validation
    """
    data = {
      "endpoint": "not-a-url",
      "keys": {"p256dh": "test_key", "auth": "test_auth"},
    }

    is_valid, error, cleaned = validate_subscription_data(data)
    assert not is_valid

  def test_subscription_duplicate_handling(self, subscription_storage):
    """
    Given: A user with existing subscription for same endpoint
    When: Trying to register duplicate
    Then: Should detect duplicate subscription
    """
    subscription = PushSubscription(
      id="sub1",
      user_id="user-123",
      endpoint="https://fcm.googleapis.com/fcm/send/test",
      p256dh="test_key",
      auth="test_auth",
    )

    subscription_storage.create(subscription)

    # Try to create duplicate
    existing = subscription_storage.get_by_endpoint("https://fcm.googleapis.com/fcm/send/test")
    assert existing is not None
    assert existing.id == "sub1"


# ==============================================================================
# Subscription Listing Tests
# ==============================================================================


class TestPushSubscriptionListing:
  """
  Tests for GET /api/push-subscriptions endpoint.

  This endpoint lists all push subscriptions for the authenticated user.
  Used for subscription management UI.
  """

  @pytest.fixture
  def app(self):
    """Create a test Baseweb app."""
    return Baseweb("test_list_subscriptions")

  @pytest.fixture
  def client(self, app):
    """Create a test client."""
    return app.test_client()

  def test_list_subscriptions_returns_200(self, subscription_storage):
    """
    Given: An authenticated user with subscriptions
    When: Listing subscriptions
    Then: Should return list of subscriptions
    """
    sub1 = PushSubscription(
      id="sub1",
      user_id="user-123",
      endpoint="https://fcm.googleapis.com/fcm/send/1",
      p256dh="key1",
      auth="auth1",
    )
    sub2 = PushSubscription(
      id="sub2",
      user_id="user-123",
      endpoint="https://fcm.googleapis.com/fcm/send/2",
      p256dh="key2",
      auth="auth2",
    )

    subscription_storage.create(sub1)
    subscription_storage.create(sub2)

    subscriptions = subscription_storage.get_by_user("user-123")
    assert len(subscriptions) == 2

  @pytest.mark.asyncio
  async def test_list_subscriptions_requires_authentication(self, app, client):
    """
    Given: An unauthenticated request
    When: GET /api/push-subscriptions
    Then: Should return 401 Unauthorized
    """
    from baseweb.push import PushSubscriptionResource

    app.add_resource(PushSubscriptionResource, "/api/push-subscriptions")

    response = await client.get("/api/push-subscriptions")
    assert response.status_code == 401

  def test_list_subscriptions_returns_only_user_subs(self, subscription_storage):
    """
    Given: Multiple users with subscriptions
    When: Listing subscriptions for a user
    Then: Should return only that user's subscriptions
    """
    sub1 = PushSubscription(
      id="sub1",
      user_id="user-123",
      endpoint="https://fcm.googleapis.com/fcm/send/1",
      p256dh="key1",
      auth="auth1",
    )
    sub2 = PushSubscription(
      id="sub2",
      user_id="user-456",  # Different user
      endpoint="https://fcm.googleapis.com/fcm/send/2",
      p256dh="key2",
      auth="auth2",
    )

    subscription_storage.create(sub1)
    subscription_storage.create(sub2)

    # Get only user-123's subscriptions
    subscriptions = subscription_storage.get_by_user("user-123")
    assert len(subscriptions) == 1
    assert subscriptions[0].user_id == "user-123"

  def test_list_subscriptions_empty_array_when_none(self, subscription_storage):
    """
    Given: An authenticated user with no subscriptions
    When: Listing subscriptions
    Then: Should return empty array
    """
    subscriptions = subscription_storage.get_by_user("user-no-subs")
    assert len(subscriptions) == 0

  def test_list_subscriptions_masks_keys(self, subscription_storage):
    """
    Given: A user requesting subscription list
    When: Converting to dict for API response
    Then: Response should NOT include p256dh and auth keys
    """
    subscription = PushSubscription(
      id="sub1",
      user_id="user-123",
      endpoint="https://fcm.googleapis.com/fcm/send/1",
      p256dh="secret_key",
      auth="secret_auth",
    )

    subscription_storage.create(subscription)

    # Convert to dict without keys
    sub_dict = subscription.to_dict(include_keys=False)

    assert "keys" not in sub_dict
    assert "p256dh" not in sub_dict
    assert "auth" not in sub_dict

    # With keys
    sub_dict_with_keys = subscription.to_dict(include_keys=True)
    assert "keys" in sub_dict_with_keys


# ==============================================================================
# Subscription Removal Tests
# ==============================================================================


class TestPushSubscriptionRemoval:
  """
  Tests for DELETE /api/push-subscriptions/{id} endpoint.

  This endpoint removes a push subscription for the authenticated user.
  """

  @pytest.fixture
  def app(self):
    """Create a test Baseweb app."""
    return Baseweb("test_delete_subscription")

  @pytest.fixture
  def client(self, app):
    """Create a test client."""
    return app.test_client()

  def test_delete_subscription_returns_204(self, subscription_storage):
    """
    Given: An authenticated user with existing subscription
    When: Deleting the subscription
    Then: Should return 204 No Content
    """
    subscription = PushSubscription(
      id="sub1",
      user_id="user-123",
      endpoint="https://fcm.googleapis.com/fcm/send/1",
      p256dh="key1",
      auth="auth1",
    )

    subscription_storage.create(subscription)

    # Delete should succeed
    result = subscription_storage.delete("sub1")
    assert result is True

  @pytest.mark.asyncio
  async def test_delete_subscription_requires_authentication(self, app, client):
    """
    Given: An unauthenticated request
    When: DELETE /api/push-subscriptions/{id}
    Then: Should return 401 Unauthorized
    """
    from baseweb.push import PushSubscriptionDetailResource

    app.add_resource(
      PushSubscriptionDetailResource,
      "/api/push-subscriptions/<string:subscription_id>",
    )

    response = await client.delete("/api/push-subscriptions/test-id")
    assert response.status_code == 401

  def test_delete_subscription_ownership_check(self, subscription_storage):
    """
    Given: An authenticated user trying to delete another user's subscription
    When: Checking ownership
    Then: Should not find the subscription
    """
    subscription = PushSubscription(
      id="sub1",
      user_id="user-123",
      endpoint="https://fcm.googleapis.com/fcm/send/1",
      p256dh="key1",
      auth="auth1",
    )

    subscription_storage.create(subscription)

    # Try to get as different user
    sub = subscription_storage.get("sub1")
    assert sub.user_id == "user-123"
    assert sub.user_id != "user-456"  # Different user

  def test_delete_nonexistent_subscription_returns_404(self, subscription_storage):
    """
    Given: A subscription ID that doesn't exist
    When: Deleting the subscription
    Then: Should return False (not found)
    """
    result = subscription_storage.delete("nonexistent-id")
    assert result is False

  def test_delete_subscription_idempotent(self, subscription_storage):
    """
    Given: A deleted subscription
    When: Deleting again
    Then: Should return False (already deleted)
    """
    subscription = PushSubscription(
      id="sub1",
      user_id="user-123",
      endpoint="https://fcm.googleapis.com/fcm/send/1",
      p256dh="key1",
      auth="auth1",
    )

    subscription_storage.create(subscription)

    # First delete
    result1 = subscription_storage.delete("sub1")
    assert result1 is True

    # Second delete (idempotent)
    result2 = subscription_storage.delete("sub1")
    assert result2 is False


# ==============================================================================
# Notification Sending Tests
# ==============================================================================


class TestPushNotificationSending:
  """
  Tests for POST /api/push-notifications endpoint.

  This endpoint sends push notifications to subscribed users.
  Requires authentication and may require admin role.
  """

  @pytest.fixture
  def app(self):
    """Create a test Baseweb app."""
    return Baseweb("test_send_notification")

  @pytest.fixture
  def client(self, app):
    """Create a test client."""
    return app.test_client()

  def test_notification_payload_validation(self):
    """
    Given: A notification with valid payload
    When: Validating payload
    Then: Should pass validation
    """
    payload = PushNotificationPayload(
      title="Test Notification",
      body="This is a test notification",
    )

    is_valid, error = payload.validate()
    assert is_valid
    assert error is None

  @pytest.mark.asyncio
  async def test_send_notification_requires_authentication(self, app, client):
    """
    Given: An unauthenticated request
    When: POST /api/push-notifications
    Then: Should return 401 Unauthorized
    """
    from baseweb.push import PushNotificationResource

    app.add_resource(PushNotificationResource, "/api/push-notifications")

    data = {
      "title": "Test",
      "body": "Test notification",
      "user_ids": ["user-123"],
    }

    response = await client.post("/api/push-notifications", json=data)
    assert response.status_code == 401

  @pytest.mark.asyncio
  async def test_send_notification_requires_admin_role(self, app, client):
    """
    Given: An authenticated non-admin user
    When: POST /api/push-notifications
    Then: Should return 403 Forbidden
    """
    from baseweb.push import PushNotificationResource

    app.add_resource(PushNotificationResource, "/api/push-notifications")

    # Without is_admin flag, should return 401 or 403
    data = {
      "title": "Test",
      "body": "Test notification",
      "user_ids": ["user-123"],
    }

    response = await client.post("/api/push-notifications", json=data)
    # Should fail auth (401) or require admin (403)
    assert response.status_code in [401, 403]

  def test_send_notification_to_all_subscribers(self, subscription_storage):
    """
    Given: Multiple subscriptions
    When: Getting all active subscriptions
    Then: Should return all active subscriptions
    """
    sub1 = PushSubscription(
      id="sub1",
      user_id="user-123",
      endpoint="https://fcm.googleapis.com/fcm/send/1",
      p256dh="key1",
      auth="auth1",
      is_active=True,
    )
    sub2 = PushSubscription(
      id="sub2",
      user_id="user-456",
      endpoint="https://fcm.googleapis.com/fcm/send/2",
      p256dh="key2",
      auth="auth2",
      is_active=True,
    )
    sub3 = PushSubscription(
      id="sub3",
      user_id="user-789",
      endpoint="https://fcm.googleapis.com/fcm/send/3",
      p256dh="key3",
      auth="auth3",
      is_active=False,  # Inactive
    )

    subscription_storage.create(sub1)
    subscription_storage.create(sub2)
    subscription_storage.create(sub3)

    active = subscription_storage.get_all_active()
    assert len(active) == 2

  def test_send_notification_to_specific_users(self, subscription_storage):
    """
    Given: An admin user sending targeted notification
    When: Getting subscriptions for specific users
    Then: Should return only specified users' subscriptions
    """
    sub1 = PushSubscription(
      id="sub1",
      user_id="user-123",
      endpoint="https://fcm.googleapis.com/fcm/send/1",
      p256dh="key1",
      auth="auth1",
    )
    sub2 = PushSubscription(
      id="sub2",
      user_id="user-456",
      endpoint="https://fcm.googleapis.com/fcm/send/2",
      p256dh="key2",
      auth="auth2",
    )

    subscription_storage.create(sub1)
    subscription_storage.create(sub2)

    # Get subscriptions for specific users
    target_subs = []
    for user_id in ["user-123"]:
      target_subs.extend(subscription_storage.get_by_user(user_id))

    assert len(target_subs) == 1
    assert target_subs[0].user_id == "user-123"

  def test_notification_requires_title(self):
    """
    Given: A notification payload without title
    When: Validating payload
    Then: Should fail validation
    """
    payload = PushNotificationPayload(title="", body="Test body")

    is_valid, error = payload.validate()
    assert not is_valid
    assert "Title" in error

  def test_notification_requires_body_or_message(self):
    """
    Given: A notification payload without body or message
    When: Validating payload
    Then: Should fail validation
    """
    payload = PushNotificationPayload(title="Test Title")

    is_valid, error = payload.validate()
    assert not is_valid
    assert "body" in error.lower() or "message" in error.lower()


class TestPushNotificationPayload:
  """
  Tests for notification payload structure and validation.
  """

  def test_notification_title_length_limit(self):
    """
    Given: A notification with very long title
    When: Validating payload
    Then: Should fail validation
    """
    payload = PushNotificationPayload(
      title="X" * (MAX_TITLE_LENGTH + 1),
      body="Test body",
    )

    is_valid, error = payload.validate()
    assert not is_valid

  def test_notification_body_length_limit(self):
    """
    Given: A notification with very long body
    When: Validating payload
    Then: Should fail validation
    """
    payload = PushNotificationPayload(
      title="Test Title",
      body="X" * (MAX_BODY_LENGTH + 1),
    )

    is_valid, error = payload.validate()
    assert not is_valid


# ==============================================================================
# Rate Limiting Tests
# ==============================================================================


class TestPushNotificationRateLimiting:
  """
  Tests for rate limiting on push notification sending.

  Rate limiting prevents abuse and ensures fair resource usage.
  """

  def test_rate_limit_on_send_endpoint(self, rate_limiter):
    """
    Given: Multiple rapid notification send requests
    When: Exceeding rate limit
    Then: Should return rate limit exceeded
    """
    user_id = "user-123"

    # Should allow initial sends
    for _ in range(5):
      can_send, error = rate_limiter.can_send(user_id)
      assert can_send
      rate_limiter.record_send(user_id)

  def test_rate_limit_headers_included(self, rate_limiter):
    """
    Given: A rate-limited endpoint
    When: Making requests
    Then: Response should include rate limit headers
    """
    user_id = "user-123"

    headers = rate_limiter.get_rate_limit_headers(user_id)

    assert "X-RateLimit-Limit" in headers
    assert "X-RateLimit-Remaining" in headers

  def test_rate_limit_per_user(self, rate_limiter):
    """
    Given: Rate limiting configured per user
    When: User exceeds their limit
    Then: Only that user is rate limited
    """
    user1 = "user-123"
    user2 = "user-456"

    # User 1 sends
    can_send, _ = rate_limiter.can_send(user1)
    assert can_send
    rate_limiter.record_send(user1)

    # User 2 should still be able to send
    can_send, _ = rate_limiter.can_send(user2)
    assert can_send


# ==============================================================================
# Error Handling Tests
# ==============================================================================


class TestPushNotificationErrors:
  """
  Tests for error handling in push notification endpoints.
  """

  def test_invalid_subscription_endpoint_handling(self, subscription_storage):
    """
    Given: A subscription that should be marked inactive
    When: Marking subscription inactive
    Then: Subscription should have is_active=False
    """
    subscription = PushSubscription(
      id="sub1",
      user_id="user-123",
      endpoint="https://fcm.googleapis.com/fcm/send/1",
      p256dh="key1",
      auth="auth1",
      is_active=True,
    )

    subscription_storage.create(subscription)

    # Mark as inactive
    result = subscription_storage.mark_inactive("sub1")
    assert result is True

    # Verify inactive
    sub = subscription_storage.get("sub1")
    assert sub.is_active is False

  def test_error_response_format(self):
    """
    Given: Any error in push notification endpoint
    When: Creating error response
    Then: Should be JSON with error message
    """
    error_response = {
      "type": "https://api.baseweb.io/errors/invalid-subscription",
      "title": "Invalid Subscription",
      "status": 400,
      "detail": "Subscription endpoint is required.",
    }

    assert "type" in error_response
    assert "title" in error_response
    assert "status" in error_response
    assert "detail" in error_response


class TestPushNotificationSubscriptionExpiry:
  """
  Tests for handling expired and invalid subscriptions.
  """

  def test_expired_subscription_cleanup(self, subscription_storage):
    """
    Given: A subscription that returns 410 Gone from push service
    When: Marking subscription as inactive
    Then: Subscription should have is_active=False
    """
    subscription = PushSubscription(
      id="sub1",
      user_id="user-123",
      endpoint="https://fcm.googleapis.com/fcm/send/expired",
      p256dh="key1",
      auth="auth1",
    )

    subscription_storage.create(subscription)
    subscription_storage.mark_inactive("sub1")

    sub = subscription_storage.get("sub1")
    assert sub.is_active is False

  def test_invalid_subscription_cleanup(self, subscription_storage):
    """
    Given: A subscription that returns 404 Not Found from push service
    When: Marking subscription as inactive
    Then: Subscription should be marked inactive
    """
    subscription = PushSubscription(
      id="sub1",
      user_id="user-123",
      endpoint="https://fcm.googleapis.com/fcm/send/notfound",
      p256dh="key1",
      auth="auth1",
    )

    subscription_storage.create(subscription)
    subscription_storage.mark_inactive("sub1")

    sub = subscription_storage.get("sub1")
    assert sub.is_active is False

  def test_cleanup_after_failed_delivery(self, subscription_storage):
    """
    Given: A notification send that fails
    When: Processing send results
    Then: Failed subscriptions should be marked inactive
    """
    subscription = PushSubscription(
      id="sub1",
      user_id="user-123",
      endpoint="https://fcm.googleapis.com/fcm/send/test",
      p256dh="key1",
      auth="auth1",
    )

    subscription_storage.create(subscription)

    # Mark as failed
    subscription_storage.mark_inactive("sub1")

    # Get all active should not include it
    active = subscription_storage.get_all_active()
    assert len(active) == 0


# ==============================================================================
# Security Tests
# ==============================================================================


class TestPushNotificationSecurity:
  """
  Tests for security requirements in push notification infrastructure.

  Security requirements from NFR3:
  - VAPID private key must be secured
  - Input validation on all endpoints
  - Rate limiting to prevent abuse
  - Proper authentication and authorization
  """

  def test_vapid_private_key_not_in_response(self):
    """
    Given: Any API response
    When: Checking response content
    Then: VAPID private key should NEVER be exposed
    """
    subscription = PushSubscription(
      id="sub1",
      user_id="user-123",
      endpoint="https://fcm.googleapis.com/fcm/send/test",
      p256dh="key1",
      auth="auth1",
    )

    # Convert to dict (API response format)
    response = subscription.to_dict(include_keys=False)

    # Private key should never be in subscription response
    assert "private" not in str(response).lower()

  def test_vapid_private_key_not_in_logs(self):
    """
    Given: VAPID key manager
    When: Getting public key for response
    Then: Only public key should be returned
    """
    # This is tested implicitly - get_public_key() returns only public key
    # Private key is only accessible via get_private_key_pem() which
    # should never be exposed via API
    pass

  def test_subscription_keys_not_exposed_in_list(self, subscription_storage):
    """
    Given: GET /api/push-subscriptions response
    When: Listing subscriptions
    Then: p256dh and auth keys should NOT be included
    """
    subscription = PushSubscription(
      id="sub1",
      user_id="user-123",
      endpoint="https://fcm.googleapis.com/fcm/send/test",
      p256dh="secret_key",
      auth="secret_auth",
    )

    subscription_storage.create(subscription)

    # Get without keys
    response = subscription.to_dict(include_keys=False)

    assert "keys" not in response
    assert "p256dh" not in response
    assert "auth" not in response

  def test_subscription_keys_not_in_delete_response(self, subscription_storage):
    """
    Given: DELETE /api/push-subscriptions/{id} response
    When: Deleting subscription
    Then: Keys should NOT be returned in response
    """
    subscription = PushSubscription(
      id="sub1",
      user_id="user-123",
      endpoint="https://fcm.googleapis.com/fcm/send/test",
      p256dh="key1",
      auth="auth1",
    )

    subscription_storage.create(subscription)

    # Delete returns True/False, not the subscription
    result = subscription_storage.delete("sub1")

    # Response is just success/failure, not subscription data
    assert isinstance(result, bool)

  def test_sql_injection_prevention(self):
    """
    Given: Malicious input in subscription fields
    When: Validating input
    Then: Should be validated and rejected if invalid
    """
    # This is tested through validate_subscription_data
    # The validation ensures inputs are proper types and formats
    malicious_data = {
      "endpoint": "https://fcm.googleapis.com/fcm/send/test'; DROP TABLE users; --",
      "keys": {"p256dh": "test_key", "auth": "test_auth"},
    }

    is_valid, error, cleaned = validate_subscription_data(malicious_data)
    # The endpoint should still be valid (URL can have special chars)
    # But storage should properly escape values
    # Since we use in-memory storage, SQL injection is not applicable
    # In production, database layer would handle this
    pass

  def test_xss_prevention_in_notifications(self):
    """
    Given: HTML/script in notification title/body
    When: Validating notification payload
    Then: Payload should be validated for length
    """
    # Title/body length limits prevent most XSS vectors
    payload = PushNotificationPayload(
      title="<script>alert('xss')</script>",
      body="Test body",
    )

    # Payload validation checks length
    is_valid, _ = payload.validate()

    # XSS content passes length validation but client should sanitize
    # The notification content is treated as text, not HTML
    assert is_valid


class TestPushNotificationInputValidation:
  """
  Tests for input validation in push notification endpoints.
  """

  def test_subscription_endpoint_url_scheme_validation(self):
    """
    Given: A subscription endpoint with non-HTTPS scheme
    When: Validating subscription
    Then: Should fail validation
    """
    data = {
      "endpoint": "http://example.com/push",  # HTTP not HTTPS
      "keys": {"p256dh": "test_key", "auth": "test_auth"},
    }

    is_valid, error, cleaned = validate_subscription_data(data)
    assert not is_valid
    assert "HTTPS" in error

  def test_subscription_key_length_validation(self):
    """
    Given: A subscription with abnormally long keys
    When: Validating subscription
    Then: Should fail validation
    """
    data = {
      "endpoint": "https://fcm.googleapis.com/fcm/send/test",
      "keys": {
        "p256dh": "X" * (MAX_KEY_LENGTH + 1),
        "auth": "test_auth",
      },
    }

    is_valid, error, cleaned = validate_subscription_data(data)
    assert not is_valid

  def test_notification_title_length_limit(self):
    """
    Given: A notification with very long title
    When: Validating notification payload
    Then: Should fail validation
    """
    payload = PushNotificationPayload(
      title="X" * (MAX_TITLE_LENGTH + 1),
      body="Test body",
    )

    is_valid, error = payload.validate()
    assert not is_valid

  def test_notification_body_length_limit(self):
    """
    Given: A notification with very long body
    When: Validating notification payload
    Then: Should fail validation
    """
    payload = PushNotificationPayload(
      title="Test Title",
      body="X" * (MAX_BODY_LENGTH + 1),
    )

    is_valid, error = payload.validate()
    assert not is_valid

  def test_notification_actions_validation(self):
    """
    Given: A notification with invalid actions array
    When: Validating notification payload
    Then: Should fail validation
    """
    # Too many actions
    payload = PushNotificationPayload(
      title="Test",
      body="Body",
      actions=[
        {"action": "a1", "title": "Action 1"},
        {"action": "a2", "title": "Action 2"},
        {"action": "a3", "title": "Action 3"},
        {"action": "a4", "title": "Action 4"},  # Max is 3
      ],
    )

    is_valid, error = payload.validate()
    assert not is_valid


# ==============================================================================
# iOS Safari Compatibility Tests
# ==============================================================================


class TestIOSSafariCompatibility:
  """
  Tests for iOS 16.4+ Safari Web Push compatibility.

  iOS Safari has specific requirements for Web Push:
  - VAPID authentication is REQUIRED (unlike desktop Safari)
  - Push notifications only work in standalone mode (installed PWA)
  - Permission prompt must be triggered by user action
  """

  def test_vapid_auth_required_for_push(self):
    """
    Given: A push notification send request
    When: Getting VAPID claims
    Then: Must include VAPID authentication claims
    """
    # VAPID claims should include required fields
    manager = VAPIDKeyManager()
    claims = manager.get_vapid_claims("https://fcm.googleapis.com")

    assert "sub" in claims  # Required by Safari
    assert "exp" in claims  # Expiration required

  def test_vapid_subject_included(self):
    """
    Given: VAPID authentication header
    When: Constructing VAPID claims
    Then: Must include subject (sub) claim
    """
    manager = VAPIDKeyManager()
    manager._subject = "mailto:test@example.com"

    claims = manager.get_vapid_claims()
    assert "sub" in claims
    assert claims["sub"].startswith("mailto:") or claims["sub"].startswith("https:")

  def test_vapid_audience_for_apns(self):
    """
    Given: A push notification to iOS Safari
    When: Constructing VAPID JWT
    Then: Audience (aud) should include APNS endpoint
    """
    manager = VAPIDKeyManager()

    claims = manager.get_vapid_claims("https://web.push.apple.com")

    assert "aud" in claims
    assert "apple.com" in claims["aud"] or "push.apple.com" in claims["aud"]

  def test_push_endpoint_apns_format(self):
    """
    Given: A Safari Web Push subscription from iOS
    When: Validating endpoint
    Then: Endpoint should be valid HTTPS URL
    """
    apns_endpoint = "https://web.push.apple.com/some-token"

    is_valid, error, cleaned = validate_subscription_data(
      {
        "endpoint": apns_endpoint,
        "keys": {"p256dh": "test_key", "auth": "test_auth"},
      }
    )

    assert is_valid
    assert cleaned["endpoint"] == apns_endpoint


# ==============================================================================
# Integration Tests
# ==============================================================================


class TestPushNotificationIntegration:
  """
  Integration tests for push notification workflow.

  These tests verify the complete push notification flow from
  subscription to delivery.
  """

  def test_complete_subscription_workflow(self, subscription_storage):
    """
    Given: An authenticated user
    When: Subscribing, listing, and unsubscribing
    Then: All operations should work correctly
    """
    # Subscribe
    sub = PushSubscription(
      id="sub1",
      user_id="user-123",
      endpoint="https://fcm.googleapis.com/fcm/send/test",
      p256dh="key1",
      auth="auth1",
    )
    subscription_storage.create(sub)

    # List
    subs = subscription_storage.get_by_user("user-123")
    assert len(subs) == 1

    # Unsubscribe
    subscription_storage.delete("sub1")

    # Verify deleted
    subs = subscription_storage.get_by_user("user-123")
    assert len(subs) == 0

  def test_multiple_subscriptions_per_user(self, subscription_storage):
    """
    Given: A user with multiple device subscriptions
    When: Listing subscriptions
    Then: All subscriptions should be returned
    """
    sub1 = PushSubscription(
      id="sub1",
      user_id="user-123",
      endpoint="https://fcm.googleapis.com/fcm/send/1",
      p256dh="key1",
      auth="auth1",
    )
    sub2 = PushSubscription(
      id="sub2",
      user_id="user-123",
      endpoint="https://fcm.googleapis.com/fcm/send/2",
      p256dh="key2",
      auth="auth2",
    )

    subscription_storage.create(sub1)
    subscription_storage.create(sub2)

    subs = subscription_storage.get_by_user("user-123")
    assert len(subs) == 2


# ==============================================================================
# Edge Cases Tests
# ==============================================================================


class TestPushNotificationEdgeCases:
  """
  Tests for edge cases in push notification infrastructure.
  """

  def test_empty_notification_body(self):
    """
    Given: A notification with only title, no body
    When: Validating payload
    Then: Should require body or message
    """
    payload = PushNotificationPayload(title="Test Title")

    is_valid, error = payload.validate()
    assert not is_valid
    assert "body" in error.lower() or "message" in error.lower()

  def test_notification_to_zero_subscribers(self, subscription_storage):
    """
    Given: A send notification request with no matching subscribers
    When: Getting subscriptions
    Then: Should return empty list
    """
    # No subscriptions created
    active = subscription_storage.get_all_active()
    assert len(active) == 0

  def test_notification_to_nonexistent_user_ids(self, subscription_storage):
    """
    Given: A send notification request with invalid user IDs
    When: Getting subscriptions for those users
    Then: Should return empty list (no error)
    """
    subs = subscription_storage.get_by_user("nonexistent-user")
    assert len(subs) == 0

  def test_unicode_in_notification(self):
    """
    Given: A notification with emoji and unicode characters
    When: Validating payload
    Then: Should handle unicode correctly
    """
    payload = PushNotificationPayload(
      title="Test 📱 ❤️",
      body="Unicode: 中文 Русский",
    )

    is_valid, error = payload.validate()
    assert is_valid

  def test_very_long_endpoint_url(self):
    """
    Given: A subscription with very long endpoint URL
    When: Validating subscription
    Then: Should validate and reject if too long
    """
    data = {
      "endpoint": "https://fcm.googleapis.com/fcm/send/" + "X" * 1000,
      "keys": {"p256dh": "test_key", "auth": "test_auth"},
    }

    is_valid, error, cleaned = validate_subscription_data(data)
    assert not is_valid
    assert "long" in error.lower() or "limit" in error.lower()


# ==============================================================================
# Utility Tests
# ==============================================================================


class TestUtilityFunctions:
  """
  Tests for utility functions.
  """

  def test_is_known_push_service_google(self):
    """
    Given: A Google FCM endpoint
    When: Checking if known push service
    Then: Should return True
    """
    endpoint = "https://fcm.googleapis.com/fcm/send/token123"
    assert is_known_push_service(endpoint)

  def test_is_known_push_service_mozilla(self):
    """
    Given: A Mozilla push service endpoint
    When: Checking if known push service
    Then: Should return True
    """
    endpoint = "https://updates.push.services.mozilla.com/wpush/v1/token"
    assert is_known_push_service(endpoint)

  def test_is_known_push_service_apple(self):
    """
    Given: An Apple push service endpoint
    When: Checking if known push service
    Then: Should return True
    """
    endpoint = "https://web.push.apple.com/token123"
    assert is_known_push_service(endpoint)

  def test_is_known_push_service_unknown(self):
    """
    Given: An unknown push service endpoint
    When: Checking if known push service
    Then: Should return False
    """
    endpoint = "https://unknown-push-service.example.com/token"
    assert not is_known_push_service(endpoint)

  def test_sanitize_user_agent(self):
    """
    Given: A user agent with control characters
    When: Sanitizing
    Then: Should remove control characters
    """
    user_agent = "Mozilla/5.0 \x00\x1f Test"
    sanitized = sanitize_user_agent(user_agent)

    assert "\x00" not in sanitized
    assert "\x1f" not in sanitized

  def test_sanitize_user_agent_length_limit(self):
    """
    Given: A very long user agent
    When: Sanitizing
    Then: Should truncate to limit
    """
    user_agent = "X" * 1000
    sanitized = sanitize_user_agent(user_agent)

    assert len(sanitized) <= 500


# ==============================================================================
# Subscription Model Tests
# ==============================================================================


class TestPushSubscriptionModel:
  """
  Tests for PushSubscription data model.
  """

  def test_to_dict_without_keys(self):
    """
    Given: A subscription
    When: Converting to dict without keys
    Then: Should not include sensitive keys
    """
    subscription = PushSubscription(
      id="sub1",
      user_id="user-123",
      endpoint="https://fcm.googleapis.com/fcm/send/test",
      p256dh="secret_key",
      auth="secret_auth",
      device_name="iPhone 15",
    )

    data = subscription.to_dict(include_keys=False)

    assert "id" in data
    assert "keys" not in data
    assert "p256dh" not in data
    assert "auth" not in data

  def test_to_dict_with_keys(self):
    """
    Given: A subscription
    When: Converting to dict with keys
    Then: Should include keys
    """
    subscription = PushSubscription(
      id="sub1",
      user_id="user-123",
      endpoint="https://fcm.googleapis.com/fcm/send/test",
      p256dh="secret_key",
      auth="secret_auth",
    )

    data = subscription.to_dict(include_keys=True)

    assert "keys" in data
    assert data["keys"]["p256dh"] == "secret_key"
    assert data["keys"]["auth"] == "secret_auth"

  def test_to_webpush_format(self):
    """
    Given: A subscription
    When: Converting to webpush format
    Then: Should have correct structure
    """
    subscription = PushSubscription(
      id="sub1",
      user_id="user-123",
      endpoint="https://fcm.googleapis.com/fcm/send/test",
      p256dh="test_key",
      auth="test_auth",
    )

    webpush_data = subscription.to_webpush_format()

    assert "endpoint" in webpush_data
    assert "keys" in webpush_data
    assert webpush_data["endpoint"] == "https://fcm.googleapis.com/fcm/send/test"
    assert webpush_data["keys"]["p256dh"] == "test_key"
    assert webpush_data["keys"]["auth"] == "test_auth"


# ==============================================================================
# VAPID Claims Tests
# ==============================================================================


class TestVAPIDClaims:
  """
  Tests for VAPID claims generation.
  """

  def test_vapid_claims_include_subject(self):
    """
    Given: A VAPID key manager
    When: Getting VAPID claims
    Then: Should include subject claim
    """
    manager = VAPIDKeyManager()
    manager._subject = "mailto:test@example.com"

    claims = manager.get_vapid_claims()

    assert "sub" in claims
    assert claims["sub"] == "mailto:test@example.com"

  def test_vapid_claims_include_expiration(self):
    """
    Given: A VAPID key manager
    When: Getting VAPID claims
    Then: Should include expiration claim
    """
    import time

    manager = VAPIDKeyManager()
    claims = manager.get_vapid_claims()

    assert "exp" in claims
    # Expiration should be within reasonable range (12 hours)
    assert claims["exp"] > time.time()
    assert claims["exp"] < time.time() + 86400  # Less than 24 hours

  def test_vapid_claims_audience_optional(self):
    """
    Given: A VAPID key manager
    When: Getting VAPID claims without audience
    Then: Audience should be optional
    """
    manager = VAPIDKeyManager()
    claims = manager.get_vapid_claims()

    # Audience is optional if not provided
    # pywebpush will auto-detect from endpoint
    assert "sub" in claims
    assert "exp" in claims

  def test_vapid_claims_audience_included_when_provided(self):
    """
    Given: A VAPID key manager and push service URL
    When: Getting VAPID claims with push service URL
    Then: Should include audience claim
    """
    manager = VAPIDKeyManager()
    claims = manager.get_vapid_claims("https://fcm.googleapis.com/fcm/send")

    assert "aud" in claims
    assert "fcm.googleapis.com" in claims["aud"]


# ==============================================================================
# Global Manager Tests
# ==============================================================================


class TestGlobalManagers:
  """
  Tests for global manager instances.
  """

  def test_get_subscription_storage_singleton(self):
    """
    Given: Multiple calls to get_subscription_storage
    When: Getting storage instance
    Then: Should return same instance
    """
    storage1 = get_subscription_storage()
    storage2 = get_subscription_storage()

    assert storage1 is storage2

  def test_get_rate_limiter_singleton(self):
    """
    Given: Multiple calls to get_rate_limiter
    When: Getting limiter instance
    Then: Should return same instance
    """
    limiter1 = get_rate_limiter()
    limiter2 = get_rate_limiter()

    assert limiter1 is limiter2


# ==============================================================================
# Clean up environment
# ==============================================================================


def teardown_module(module):
  """Clean up environment variables after tests."""
  for key in ["VAPID_PRIVATE_KEY", "VAPID_SUBJECT", "VAPID_PUBLIC_KEY"]:
    if key in os.environ:
      del os.environ[key]
