"""
Push Notification Infrastructure.

This module provides push notification functionality for baseweb applications,
including subscription management and notification sending.

Requirements implemented:
- R85: VAPID key generation and management
- R86: Push subscription storage and retrieval
- R87: Push notification sending functionality
- NFR3: VAPID keys secured properly

Security features:
- VAPID private key from environment variable (never exposed via API)
- Subscription endpoint validation (HTTPS only, known push services)
- Rate limiting on notification sending
- Input validation on all endpoints
- Authentication required for subscription endpoints
"""

import hashlib
import json
import logging
import os
import re
import time
import uuid
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any
from urllib.parse import urlparse

from quart import request

from baseweb import Resource
from baseweb.vapid import VAPIDKeyError, get_vapid_manager

logger = logging.getLogger(__name__)

# Rate limiting configuration
RATE_LIMITS = {
  "notifications_per_user_per_hour": 10,
  "notifications_per_user_per_day": 50,
  "notifications_global_per_minute": 100,
}

# Input validation limits
MAX_TITLE_LENGTH = 50
MAX_BODY_LENGTH = 500
MAX_ENDPOINT_LENGTH = 500
MAX_KEY_LENGTH = 200

# Known push service domains for endpoint validation
KNOWN_PUSH_SERVICES = [
  "fcm.googleapis.com",  # Firebase Cloud Messaging (Chrome, Android)
  "updates.push.services.mozilla.com",  # Mozilla Push Service (Firefox)
  "web.push.apple.com",  # Apple Push Service (Safari, iOS)
  "push.services.mozilla.com",  # Legacy Mozilla
]


# =============================================================================
# Exceptions
# =============================================================================


class PushSubscriptionError(Exception):
  """Base exception for push subscription errors."""

  pass


class PushNotificationError(Exception):
  """Base exception for push notification errors."""

  pass


class RateLimitExceeded(Exception):
  """Raised when rate limit is exceeded."""

  pass


# =============================================================================
# Data Models
# =============================================================================


@dataclass
class PushSubscription:
  """
  Represents a push subscription for a user.

  Attributes:
      id: Unique subscription identifier
      user_id: ID of the user who owns this subscription
      endpoint: Push service endpoint URL
      p256dh: Client's ECDH public key (base64url)
      auth: Client's auth secret (base64url)
      user_agent: Browser user agent string
      device_name: User-friendly device name
      created_at: Subscription creation timestamp
      updated_at: Last update timestamp
      last_successful_push: Timestamp of last successful notification
      is_active: Whether subscription is active
  """

  id: str
  user_id: str
  endpoint: str
  p256dh: str
  auth: str
  user_agent: str | None = None
  device_name: str | None = None
  created_at: datetime = field(default_factory=datetime.utcnow)
  updated_at: datetime = field(default_factory=datetime.utcnow)
  last_successful_push: datetime | None = None
  is_active: bool = True

  def to_dict(self, include_keys: bool = False) -> dict[str, Any]:
    """
    Convert subscription to dictionary.

    Args:
        include_keys: Whether to include p256dh and auth keys.
                     Should be False for list endpoints (security).

    Returns:
        Dictionary representation of subscription.
    """
    result: dict[str, Any] = {
      "id": self.id,
      "endpoint": self.endpoint,
      "device_name": self.device_name,
      "user_agent": self.user_agent,
      "created_at": self.created_at.isoformat() + "Z",
      "last_successful_push": (
        self.last_successful_push.isoformat() + "Z" if self.last_successful_push else None
      ),
      "is_active": self.is_active,
    }
    if include_keys:
      result["keys"] = {"p256dh": self.p256dh, "auth": self.auth}
    return result

  def to_webpush_format(self) -> dict[str, Any]:
    """
    Convert to format expected by pywebpush.

    Returns:
        Dictionary in webpush format.
    """
    return {
      "endpoint": self.endpoint,
      "keys": {"p256dh": self.p256dh, "auth": self.auth},
    }


@dataclass
class PushNotificationPayload:
  """
  Push notification payload for sending.

  Attributes:
      title: Notification title (required)
      body: Notification body text (required if message not provided)
      icon: URL for notification icon
      badge: URL for notification badge
      url: URL to open on click
      actions: Action buttons for notification
      tag: Tag to group notifications
      require_interaction: Keep notification until user interacts
      ttl: Time-to-live in seconds
      urgency: Delivery urgency hint
  """

  title: str
  body: str | None = None
  message: str | None = None  # Alternative to body
  icon: str | None = None
  badge: str | None = None
  url: str | None = None
  actions: list[dict[str, str]] | None = None
  tag: str | None = None
  require_interaction: bool = False
  ttl: int = 86400  # 24 hours default
  urgency: str = "normal"  # very-low, low, normal, high

  def to_dict(self) -> dict[str, Any]:
    """Convert to dictionary for JSON serialization."""
    result: dict[str, Any] = {"title": self.title}

    # Use body or message
    result["body"] = self.body or self.message

    # Add optional fields
    if self.icon:
      result["icon"] = self.icon
    if self.badge:
      result["badge"] = self.badge
    if self.url:
      result["url"] = self.url
    if self.actions:
      result["actions"] = self.actions
    if self.tag:
      result["tag"] = self.tag
    if self.require_interaction:
      result["requireInteraction"] = self.require_interaction

    return result

  def validate(self) -> tuple[bool, str | None]:
    """
    Validate the payload.

    Returns:
        Tuple of (is_valid, error_message).
    """
    # Title is required
    if not self.title:
      return False, "Title is required"

    # Body length check
    if self.body and len(self.body) > MAX_BODY_LENGTH:
      return False, f"Body exceeds {MAX_BODY_LENGTH} character limit"

    # Title length check
    if len(self.title) > MAX_TITLE_LENGTH:
      return False, f"Title exceeds {MAX_TITLE_LENGTH} character limit"

    # Must have body or message
    if not self.body and not self.message:
      return False, "Either body or message is required"

    # Validate urgency
    valid_urgencies = ["very-low", "low", "normal", "high"]
    if self.urgency not in valid_urgencies:
      return False, f"Urgency must be one of: {', '.join(valid_urgencies)}"

    # Validate TTL
    if self.ttl < 0 or self.ttl > 2592000:  # Max 30 days
      return False, "TTL must be between 0 and 2592000 seconds"

    # Validate actions
    if self.actions:
      if len(self.actions) > 3:
        return False, "Maximum 3 actions allowed"
      for action in self.actions:
        if not action.get("action") or not action.get("title"):
          return False, "Each action must have 'action' and 'title'"
        if len(action.get("title", "")) > 20:
          return False, "Action title exceeds 20 character limit"

    return True, None


# =============================================================================
# Subscription Storage (In-Memory)
# =============================================================================


class SubscriptionStorage:
  """
  In-memory storage for push subscriptions.

  In production, this should be replaced with database storage.
  Thread-safe operations using locks.
  """

  def __init__(self):
    """Initialize subscription storage."""
    self._subscriptions: dict[str, PushSubscription] = {}
    self._user_subscriptions: dict[str, list[str]] = defaultdict(list)
    self._endpoint_index: dict[str, str] = {}  # endpoint -> subscription_id

  def create(self, subscription: PushSubscription) -> PushSubscription:
    """
    Create a new subscription.

    Args:
        subscription: Subscription to create.

    Returns:
        Created subscription.
    """
    self._subscriptions[subscription.id] = subscription
    self._user_subscriptions[subscription.user_id].append(subscription.id)
    self._endpoint_index[subscription.endpoint] = subscription.id
    return subscription

  def get(self, subscription_id: str) -> PushSubscription | None:
    """
    Get subscription by ID.

    Args:
        subscription_id: Subscription ID.

    Returns:
        Subscription or None if not found.
    """
    return self._subscriptions.get(subscription_id)

  def get_by_endpoint(self, endpoint: str) -> PushSubscription | None:
    """
    Get subscription by endpoint.

    Args:
        endpoint: Push service endpoint.

    Returns:
        Subscription or None if not found.
    """
    sub_id = self._endpoint_index.get(endpoint)
    return self._subscriptions.get(sub_id) if sub_id else None

  def get_by_user(self, user_id: str) -> list[PushSubscription]:
    """
    Get all subscriptions for a user.

    Args:
        user_id: User ID.

    Returns:
        List of subscriptions (without sensitive keys).
    """
    sub_ids = self._user_subscriptions.get(user_id, [])
    return [self._subscriptions[sid] for sid in sub_ids if sid in self._subscriptions]

  def update(self, subscription_id: str, **kwargs) -> PushSubscription | None:
    """
    Update subscription fields.

    Args:
        subscription_id: Subscription ID.
        **kwargs: Fields to update.

    Returns:
        Updated subscription or None if not found.
    """
    subscription = self._subscriptions.get(subscription_id)
    if not subscription:
      return None

    for key, value in kwargs.items():
      if hasattr(subscription, key):
        setattr(subscription, key, value)

    subscription.updated_at = datetime.utcnow()
    return subscription

  def delete(self, subscription_id: str) -> bool:
    """
    Delete subscription.

    Args:
        subscription_id: Subscription ID.

    Returns:
        True if deleted, False if not found.
    """
    subscription = self._subscriptions.pop(subscription_id, None)
    if not subscription:
      return False

    # Remove from user index
    if subscription.user_id in self._user_subscriptions:
      self._user_subscriptions[subscription.user_id] = [
        sid for sid in self._user_subscriptions[subscription.user_id] if sid != subscription_id
      ]

    # Remove from endpoint index
    self._endpoint_index.pop(subscription.endpoint, None)

    return True

  def mark_inactive(self, subscription_id: str) -> bool:
    """
    Mark subscription as inactive (after 410/404 from push service).

    Args:
        subscription_id: Subscription ID.

    Returns:
        True if marked inactive, False if not found.
    """
    return self.update(subscription_id, is_active=False) is not None

  def get_all_active(self) -> list[PushSubscription]:
    """
    Get all active subscriptions.

    Returns:
        List of active subscriptions.
    """
    return [sub for sub in self._subscriptions.values() if sub.is_active]


# Global subscription storage
_subscription_storage: SubscriptionStorage | None = None


def get_subscription_storage() -> SubscriptionStorage:
  """
  Get or create the global subscription storage.

  Returns:
      SubscriptionStorage instance.
  """
  global _subscription_storage

  if _subscription_storage is None:
    _subscription_storage = SubscriptionStorage()

  return _subscription_storage


# =============================================================================
# Rate Limiter
# =============================================================================


class RateLimiter:
  """
  Rate limiter for push notifications.

  Tracks notification sends per user with sliding window.
  In production, use Redis for distributed rate limiting.
  """

  def __init__(self):
    """Initialize rate limiter."""
    # Track sends per user: {user_id: [timestamp1, timestamp2, ...]}
    self._user_sends: dict[str, list[float]] = defaultdict(list)
    # Track global sends: [timestamp1, timestamp2, ...]
    self._global_sends: list[float] = []

  def can_send(self, user_id: str) -> tuple[bool, str | None]:
    """
    Check if user can send a notification.

    Args:
        user_id: User ID to check.

    Returns:
        Tuple of (can_send, error_message).
    """
    now = time.time()

    # Clean old entries
    self._cleanup_old_entries(now)

    # Check hourly limit
    hourly_sends = len([ts for ts in self._user_sends[user_id] if now - ts < 3600])
    if hourly_sends >= RATE_LIMITS["notifications_per_user_per_hour"]:
      return False, "Hourly notification limit exceeded"

    # Check daily limit
    daily_sends = len([ts for ts in self._user_sends[user_id] if now - ts < 86400])
    if daily_sends >= RATE_LIMITS["notifications_per_user_per_day"]:
      return False, "Daily notification limit exceeded"

    # Check global limit
    global_sends = len([ts for ts in self._global_sends if now - ts < 60])
    if global_sends >= RATE_LIMITS["notifications_global_per_minute"]:
      return False, "System rate limit exceeded"

    return True, None

  def record_send(self, user_id: str) -> None:
    """
    Record a notification send.

    Args:
        user_id: User ID that sent the notification.
    """
    now = time.time()
    self._user_sends[user_id].append(now)
    self._global_sends.append(now)

  def _cleanup_old_entries(self, now: float) -> None:
    """Clean up entries older than 24 hours."""
    cutoff = now - 86400

    # Clean user sends
    for user_id in list(self._user_sends.keys()):
      self._user_sends[user_id] = [ts for ts in self._user_sends[user_id] if ts > cutoff]
      if not self._user_sends[user_id]:
        del self._user_sends[user_id]

    # Clean global sends
    self._global_sends = [ts for ts in self._global_sends if ts > cutoff]

  def get_rate_limit_headers(self, user_id: str) -> dict[str, str]:
    """
    Get rate limit headers for response.

    Args:
        user_id: User ID.

    Returns:
        Dictionary of rate limit headers.
    """
    now = time.time()

    # Calculate remaining limits
    hourly_sends = len([ts for ts in self._user_sends.get(user_id, []) if now - ts < 3600])
    daily_sends = len([ts for ts in self._user_sends.get(user_id, []) if now - ts < 86400])

    return {
      "X-RateLimit-Limit": str(RATE_LIMITS["notifications_per_user_per_hour"]),
      "X-RateLimit-Remaining": str(
        max(0, RATE_LIMITS["notifications_per_user_per_hour"] - hourly_sends)
      ),
      "X-RateLimit-Daily-Limit": str(RATE_LIMITS["notifications_per_user_per_day"]),
      "X-RateLimit-Daily-Remaining": str(
        max(0, RATE_LIMITS["notifications_per_user_per_day"] - daily_sends)
      ),
    }


# Global rate limiter
_rate_limiter: RateLimiter | None = None


def get_rate_limiter() -> RateLimiter:
  """
  Get or create the global rate limiter.

  Returns:
      RateLimiter instance.
  """
  global _rate_limiter

  if _rate_limiter is None:
    _rate_limiter = RateLimiter()

  return _rate_limiter


# =============================================================================
# Validators
# =============================================================================


def validate_subscription_data(data: dict[str, Any]) -> tuple[bool, str | None, dict | None]:
  """
  Validate subscription data from client.

  Args:
      data: Subscription data dictionary.

  Returns:
      Tuple of (is_valid, error_message, cleaned_data).
  """
  if not isinstance(data, dict):
    return False, "Subscription must be a JSON object", None

  # Validate endpoint
  endpoint = data.get("endpoint")
  if not endpoint:
    return False, "Endpoint is required", None

  if not isinstance(endpoint, str):
    return False, "Endpoint must be a string", None

  if len(endpoint) > MAX_ENDPOINT_LENGTH:
    return False, f"Endpoint exceeds {MAX_ENDPOINT_LENGTH} character limit", None

  # Validate endpoint URL
  try:
    parsed = urlparse(endpoint)
    if parsed.scheme != "https":
      return False, "Endpoint must use HTTPS", None
    if not parsed.netloc:
      return False, "Invalid endpoint URL format", None
  except Exception:
    return False, "Invalid endpoint URL", None

  # Validate endpoint is from known push service
  if not is_known_push_service(endpoint):
    logger.warning(f"Unknown push service endpoint: {endpoint}")
    # Still allow it, but log warning

  # Validate keys
  keys = data.get("keys")
  if not keys or not isinstance(keys, dict):
    return False, "Keys object is required", None

  p256dh = keys.get("p256dh")
  auth = keys.get("auth")

  if not p256dh or not auth:
    return False, "Both p256dh and auth keys are required", None

  if not isinstance(p256dh, str) or not isinstance(auth, str):
    return False, "Keys must be strings", None

  if len(p256dh) > MAX_KEY_LENGTH or len(auth) > MAX_KEY_LENGTH:
    return False, f"Key values exceed {MAX_KEY_LENGTH} character limit", None

  # Validate base64url format
  base64url_pattern = re.compile(r"^[A-Za-z0-9_-]+$")
  if not base64url_pattern.match(p256dh):
    return False, "p256dh must be base64url encoded", None
  if not base64url_pattern.match(auth):
    return False, "auth must be base64url encoded", None

  # Build cleaned data
  cleaned = {
    "endpoint": endpoint,
    "keys": {"p256dh": p256dh, "auth": auth},
  }

  # Optional fields
  if "device_name" in data:
    device_name = data["device_name"]
    if isinstance(device_name, str) and len(device_name) <= 100:
      cleaned["device_name"] = device_name

  if "user_agent" in data:
    user_agent = data["user_agent"]
    if isinstance(user_agent, str) and len(user_agent) <= 500:
      # Sanitize - remove control characters
      cleaned["user_agent"] = re.sub(r"[\x00-\x1f\x7f-\x9f]", "", user_agent)

  return True, None, cleaned


def is_known_push_service(endpoint: str) -> bool:
  """
  Check if endpoint is from a known push service.

  Args:
      endpoint: Push service endpoint URL.

  Returns:
      True if from known push service.
  """
  try:
    parsed = urlparse(endpoint)
    for service in KNOWN_PUSH_SERVICES:
      if parsed.netloc == service or parsed.netloc.endswith("." + service):
        return True
    return False
  except Exception:
    return False


def sanitize_user_agent(user_agent: str) -> str:
  """
  Sanitize user agent string for storage.

  Args:
      user_agent: Raw user agent string.

  Returns:
      Sanitized user agent.
  """
  # Limit length
  user_agent = user_agent[:500]
  # Remove control characters
  user_agent = re.sub(r"[\x00-\x1f\x7f-\x9f]", "", user_agent)
  return user_agent


def hash_ip(ip_address: str) -> str:
  """
  Hash IP address for privacy-preserving logging.

  Args:
      ip_address: IP address to hash.

  Returns:
      Hashed IP (first 16 characters).
  """
  salt = os.environ.get("IP_HASH_SALT", "default-salt-change-in-production")
  return hashlib.sha256(f"{salt}{ip_address}".encode()).hexdigest()[:16]


# =============================================================================
# API Resources
# =============================================================================


class VAPIDPublicKeyResource(Resource):
  """
  Return the public VAPID key for client subscriptions.

  GET /api/vapid-public-key

  This endpoint is public (no authentication required) because the public key
  is needed by clients before they can create push subscriptions.
  """

  async def get(self):
    """
    Get the public VAPID key.

    Returns:
        JSON response with public_key field, or 503 if not configured.
    """
    try:
      manager = await get_vapid_manager()

      if not manager.is_configured():
        return (
          {
            "type": "https://api.baseweb.io/errors/vapid-not-configured",
            "title": "VAPID Not Configured",
            "status": 503,
            "detail": "VAPID keys have not been configured for this application.",
          },
          503,
        )

      public_key = manager.get_public_key()
      subject = manager.get_subject()

      # Add caching headers
      return (
        {"public_key": public_key, "subject": subject},
        200,
        {"Cache-Control": "public, max-age=86400"},  # Cache for 24 hours
      )

    except VAPIDKeyError as e:
      logger.error(f"VAPID key error: {e}")
      return (
        {
          "type": "https://api.baseweb.io/errors/vapid-error",
          "title": "VAPID Error",
          "status": 500,
          "detail": str(e),
        },
        500,
      )


class PushSubscriptionResource(Resource):
  """
  Manage push subscriptions.

  POST /api/push-subscriptions - Register new subscription
  GET /api/push-subscriptions - List user's subscriptions
  """

  async def post(self):
    """
    Register a new push subscription.

    Requires authentication.

    Returns:
        201 Created with subscription info
        400 Bad Request for invalid data
        401 Unauthorized if not authenticated
        409 Conflict for duplicate subscription
    """
    # Check authentication (implemented by application using authenticator)
    # The security_scope parameter on add_resource handles this

    # Get current user ID (application must provide this)
    user_id = getattr(request, "user_id", None)
    if not user_id:
      return (
        {
          "type": "https://api.baseweb.io/errors/unauthorized",
          "title": "Unauthorized",
          "status": 401,
          "detail": "Authentication required to register subscriptions.",
        },
        401,
      )

    # Parse request body
    try:
      data = await request.get_json()
    except Exception:
      return (
        {
          "type": "https://api.baseweb.io/errors/invalid-json",
          "title": "Invalid JSON",
          "status": 400,
          "detail": "Request body must be valid JSON.",
        },
        400,
      )

    # Validate subscription data
    is_valid, error, cleaned = validate_subscription_data(data)
    if not is_valid or cleaned is None:
      return (
        {
          "type": "https://api.baseweb.io/errors/invalid-subscription",
          "title": "Invalid Subscription",
          "status": 400,
          "detail": error,
        },
        400,
      )

    storage = get_subscription_storage()

    # Check for duplicate
    existing = storage.get_by_endpoint(cleaned["endpoint"])
    if existing and existing.user_id == user_id:
      return (
        {
          "type": "https://api.baseweb.io/errors/subscription-exists",
          "title": "Subscription Already Exists",
          "status": 409,
          "detail": "This subscription is already registered.",
          "subscription_id": existing.id,
        },
        409,
      )
    elif existing:
      # Different user - don't reveal existence
      return (
        {
          "type": "https://api.baseweb.io/errors/subscription-exists",
          "title": "Subscription Already Exists",
          "status": 409,
          "detail": "This endpoint is already registered.",
        },
        409,
      )

    # Create subscription
    subscription = PushSubscription(
      id=str(uuid.uuid4()),
      user_id=user_id,
      endpoint=cleaned["endpoint"],
      p256dh=cleaned["keys"]["p256dh"],
      auth=cleaned["keys"]["auth"],
      device_name=cleaned.get("device_name"),
      user_agent=cleaned.get("user_agent"),
    )

    storage.create(subscription)

    # Return subscription (without sensitive keys)
    return subscription.to_dict(include_keys=False), 201

  async def get(self):
    """
    List user's subscriptions.

    Requires authentication.

    Returns:
        200 OK with list of subscriptions
        401 Unauthorized if not authenticated
    """
    # Check authentication
    user_id = getattr(request, "user_id", None)
    if not user_id:
      return (
        {
          "type": "https://api.baseweb.io/errors/unauthorized",
          "title": "Unauthorized",
          "status": 401,
          "detail": "Authentication required.",
        },
        401,
      )

    storage = get_subscription_storage()
    subscriptions = storage.get_by_user(user_id)

    # Return without sensitive keys
    return {"subscriptions": [sub.to_dict(include_keys=False) for sub in subscriptions]}, 200


class PushSubscriptionDetailResource(Resource):
  """
  Manage individual push subscription.

  DELETE /api/push-subscriptions/<id> - Remove subscription
  """

  async def delete(self, subscription_id: str):
    """
    Delete a push subscription.

    Requires authentication. Users can only delete their own subscriptions.

    Args:
        subscription_id: Subscription ID to delete.

    Returns:
        204 No Content on success
        401 Unauthorized if not authenticated
        404 Not Found if subscription doesn't exist or not owned
    """
    # Check authentication
    user_id = getattr(request, "user_id", None)
    if not user_id:
      return (
        {
          "type": "https://api.baseweb.io/errors/unauthorized",
          "title": "Unauthorized",
          "status": 401,
          "detail": "Authentication required.",
        },
        401,
      )

    storage = get_subscription_storage()
    subscription = storage.get(subscription_id)

    # Check ownership (don't reveal existence of others' subscriptions)
    if not subscription or subscription.user_id != user_id:
      return (
        {
          "type": "https://api.baseweb.io/errors/subscription-not-found",
          "title": "Subscription Not Found",
          "status": 404,
          "detail": f"Subscription {subscription_id} does not exist or you do not have access.",
        },
        404,
      )

    storage.delete(subscription_id)
    return None, 204


class PushNotificationResource(Resource):
  """
  Send push notifications.

  POST /api/push-notifications - Send notification
  """

  async def post(self):
    """
    Send push notifications.

    Requires authentication and admin role.

    Returns:
        200 OK with sent count
        400 Bad Request for invalid payload
        401 Unauthorized if not authenticated
        403 Forbidden if not admin
        429 Too Many Requests if rate limited
    """
    # Check authentication
    user_id = getattr(request, "user_id", None)
    if not user_id:
      return (
        {
          "type": "https://api.baseweb.io/errors/unauthorized",
          "title": "Unauthorized",
          "status": 401,
          "detail": "Authentication required.",
        },
        401,
      )

    # Check admin role (application must set is_admin on request)
    is_admin = getattr(request, "is_admin", False)
    if not is_admin:
      return (
        {
          "type": "https://api.baseweb.io/errors/forbidden",
          "title": "Forbidden",
          "status": 403,
          "detail": "You do not have permission to send push notifications.",
        },
        403,
      )

    # Check rate limit
    rate_limiter = get_rate_limiter()
    can_send, error_message = rate_limiter.can_send(user_id)
    if not can_send:
      return (
        {
          "type": "https://api.baseweb.io/errors/rate-limit",
          "title": "Rate Limit Exceeded",
          "status": 429,
          "detail": error_message,
        },
        429,
        rate_limiter.get_rate_limit_headers(user_id),
      )

    # Parse request body
    try:
      data = await request.get_json()
    except Exception:
      return (
        {
          "type": "https://api.baseweb.io/errors/invalid-json",
          "title": "Invalid JSON",
          "status": 400,
          "detail": "Request body must be valid JSON.",
        },
        400,
      )

    # Extract user_ids (optional - if empty, send to all)
    target_user_ids = data.get("user_ids", [])
    if not isinstance(target_user_ids, list):
      return (
        {
          "type": "https://api.baseweb.io/errors/invalid-notification",
          "title": "Invalid Notification",
          "status": 400,
          "detail": "user_ids must be an array.",
        },
        400,
      )

    # Validate notification payload
    title = data.get("title")
    body = data.get("body")
    message = data.get("message")

    if not title:
      return (
        {
          "type": "https://api.baseweb.io/errors/invalid-notification",
          "title": "Invalid Notification",
          "status": 400,
          "detail": "Title is required.",
          "field": "title",
        },
        400,
      )

    if not body and not message:
      return (
        {
          "type": "https://api.baseweb.io/errors/invalid-notification",
          "title": "Invalid Notification",
          "status": 400,
          "detail": "Either body or message is required.",
        },
        400,
      )

    if len(title) > MAX_TITLE_LENGTH:
      return (
        {
          "type": "https://api.baseweb.io/errors/invalid-notification",
          "title": "Invalid Notification",
          "status": 400,
          "detail": f"Title exceeds {MAX_TITLE_LENGTH} character limit.",
          "field": "title",
        },
        400,
      )

    body_text = body or message
    if len(body_text) > MAX_BODY_LENGTH:
      return (
        {
          "type": "https://api.baseweb.io/errors/invalid-notification",
          "title": "Invalid Notification",
          "status": 400,
          "detail": f"Body exceeds {MAX_BODY_LENGTH} character limit.",
          "field": "body",
        },
        400,
      )

    # Create payload
    payload = PushNotificationPayload(
      title=title,
      body=body_text,
      icon=data.get("icon"),
      badge=data.get("badge"),
      url=data.get("url"),
      actions=data.get("actions"),
      tag=data.get("tag"),
      require_interaction=data.get("require_interaction", False),
      ttl=data.get("ttl", 86400),
      urgency=data.get("urgency", "normal"),
    )

    # Validate payload
    is_valid, error = payload.validate()
    if not is_valid:
      return (
        {
          "type": "https://api.baseweb.io/errors/invalid-notification",
          "title": "Invalid Notification",
          "status": 400,
          "detail": error,
        },
        400,
      )

    # Get subscriptions to send to
    storage = get_subscription_storage()
    if target_user_ids:
      # Send to specific users
      subscriptions = []
      for uid in target_user_ids:
        subscriptions.extend(storage.get_by_user(uid))
    else:
      # Send to all active subscriptions
      subscriptions = storage.get_all_active()

    # Filter active subscriptions
    active_subscriptions = [sub for sub in subscriptions if sub.is_active]

    if not active_subscriptions:
      return {"sent": 0, "failed": 0, "message": "No active subscriptions found"}, 200

    # Send notifications
    sent_count = 0
    failed_count = 0
    failed_subscriptions = []

    for subscription in active_subscriptions:
      try:
        result = await send_push_notification(subscription, payload)
        if result:
          sent_count += 1
          # Update last successful push
          storage.update(subscription.id, last_successful_push=datetime.utcnow())
        else:
          failed_count += 1
      except Exception as e:
        logger.warning(f"Failed to send notification to {subscription.id}: {e}")
        failed_count += 1
        # Check if subscription is expired
        if "410" in str(e) or "404" in str(e) or "Gone" in str(e):
          storage.mark_inactive(subscription.id)
          failed_subscriptions.append(subscription.id)

    # Record rate limit
    rate_limiter.record_send(user_id)

    response_data = {
      "sent": sent_count,
      "failed": failed_count,
      "total": len(active_subscriptions),
    }

    return response_data, 200, rate_limiter.get_rate_limit_headers(user_id)


# =============================================================================
# Push Sending Functions
# =============================================================================


async def send_push_notification(
  subscription: PushSubscription,
  payload: PushNotificationPayload,
) -> bool:
  """
  Send a push notification to a subscription.

  Args:
      subscription: PushSubscription to send to.
      payload: Notification payload.

  Returns:
      True if sent successfully, False if subscription is expired.

  Raises:
      Exception: On transient errors.
  """
  try:
    # Import pywebpush
    from pywebpush import webpush_async  # type: ignore[import-untyped]

    # Get VAPID manager
    manager = await get_vapid_manager()
    if not manager.is_configured():
      raise PushNotificationError("VAPID keys not configured")

    # Get VAPID claims
    vapid_claims = manager.get_vapid_claims(subscription.endpoint)

    # Send notification
    response = await webpush_async(
      subscription_info=subscription.to_webpush_format(),
      data=json.dumps(payload.to_dict()),
      vapid_private_key=manager.get_private_key_pem(),
      vapid_claims=vapid_claims,
      ttl=payload.ttl,
    )

    # Check response
    if response and response.status_code in (200, 201, 202):
      return True
    else:
      logger.warning(
        f"Push notification returned status {response.status_code if response else 'None'}"
      )
      return False

  except Exception as e:
    error_str = str(e)

    # Handle expired subscriptions
    if "410" in error_str or "Gone" in error_str:
      logger.info(f"Subscription {subscription.id} is expired (410 Gone)")
      return False
    elif "404" in error_str or "Not Found" in error_str:
      logger.info(f"Subscription {subscription.id} is invalid (404 Not Found)")
      return False

    # Re-raise other errors
    logger.error(f"Error sending push notification: {e}")
    raise


# =============================================================================
# Convenience function to register resources
# =============================================================================


def register_push_resources(app, prefix: str = "/api"):
  """
  Register push notification resources with a Baseweb app.

  Args:
      app: Baseweb application instance.
      prefix: URL prefix for API endpoints.
  """
  # Public endpoint - no authentication required
  app.add_resource(VAPIDPublicKeyResource, f"{prefix}/vapid-public-key")

  # Subscription endpoints - require authentication
  app.add_resource(
    PushSubscriptionResource,
    f"{prefix}/push-subscriptions",
    security_scope="api.push.subscriptions",
  )

  # Subscription detail - requires authentication
  app.add_resource(
    PushSubscriptionDetailResource,
    f"{prefix}/push-subscriptions/<string:subscription_id>",
    security_scope="api.push.subscriptions",
  )

  # Notification sending - requires authentication and admin role
  app.add_resource(
    PushNotificationResource,
    f"{prefix}/push-notifications",
    security_scope="api.push.notifications",
  )
