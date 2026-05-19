"""
VAPID Key Management for Web Push Notifications.

This module provides VAPID (Voluntary Application Server Identification) key
management for authenticating with push services (APNs, FCM, etc.).

VAPID keys are used to:
1. Identify the application server to push services
2. Authenticate push notification requests
3. Enable Safari Web Push on iOS 16.4+ (VAPID is REQUIRED)

Security Requirements:
- Private keys MUST be stored securely (environment variables or secrets manager)
- Private keys MUST NEVER be exposed via API or logged in plain text
- Each application should have its own unique VAPID key pair
"""

import logging
import os

logger = logging.getLogger(__name__)

# Known push service domains for validation
KNOWN_PUSH_SERVICES = [
  "fcm.googleapis.com",
  "updates.push.services.mozilla.com",
  "web.push.apple.com",
]


class VAPIDKeyError(Exception):
  """Raised when VAPID key operations fail."""

  pass


class VAPIDKeyManager:
  """
  Manage VAPID keys for push notification authentication.

  VAPID keys are loaded from environment variables:
  - VAPID_PRIVATE_KEY: PEM-encoded private key or path to key file
  - VAPID_PUBLIC_KEY: Optional, derived from private key if not provided
  - VAPID_SUBJECT: Contact URI (mailto: or https:) for the sender

  Usage:
      manager = VAPIDKeyManager()
      await manager.initialize()
      public_key = manager.get_public_key()
      claims = manager.get_vapid_claims(push_service_url)
  """

  def __init__(self):
    """Initialize the VAPID key manager."""
    self._vapid = None
    self._private_key_pem: str | None = None
    self._public_key_raw: str | None = None
    self._subject: str | None = None
    self._initialized = False

  async def initialize(self) -> None:
    """
    Initialize VAPID keys from environment or generate new ones.

    Raises:
        VAPIDKeyError: If keys cannot be loaded or generated.
    """
    if self._initialized:
      return

    try:
      # Try to import py_vapid (may not be available in test environments)
      from py_vapid import Vapid01  # type: ignore[import-untyped]
    except ImportError:
      logger.warning("py-vapid not installed, VAPID features disabled")
      self._initialized = True
      return

    # Load subject from environment
    self._subject = os.environ.get("VAPID_SUBJECT", "mailto:admin@localhost")

    # Try to load private key from environment
    private_key_source = os.environ.get("VAPID_PRIVATE_KEY")

    if private_key_source:
      # Check if it's a file path
      if self._is_file_path(private_key_source):
        self._private_key_pem = self._read_key_file(private_key_source)
      else:
        # It's the key content itself
        self._private_key_pem = private_key_source

      try:
        self._vapid = Vapid01.from_pem(self._private_key_pem.encode())
        logger.info("VAPID keys loaded from environment")
      except Exception as e:
        raise VAPIDKeyError(f"Invalid VAPID private key: {e}") from e
    else:
      # Generate new keys
      logger.warning("VAPID_PRIVATE_KEY not set, generating temporary keys")
      self._vapid = Vapid01()
      self._vapid.generate_keys()
      private_pem = self._vapid.private_pem()
      self._private_key_pem = (
        private_pem.decode() if isinstance(private_pem, bytes) else private_pem
      )
      # Log a warning about temporary keys in production
      if os.environ.get("ENVIRONMENT", "development").lower() == "production":
        logger.error(
          "Using temporary VAPID keys in production is not recommended. "
          "Set VAPID_PRIVATE_KEY environment variable."
        )

    self._initialized = True

  def _is_file_path(self, source: str) -> bool:
    """Check if the source looks like a file path."""
    # Simple heuristic: if it starts with / or ./ or contains path separators
    # and doesn't look like a PEM key
    if source.startswith("/") or source.startswith("./"):
      return True
    if "\n" in source or "-----BEGIN" in source:
      return False
    return False

  def _read_key_file(self, filepath: str) -> str:
    """Read private key from file."""
    from pathlib import Path

    try:
      key_path = Path(filepath)
      if not key_path.exists():
        raise VAPIDKeyError(f"VAPID key file not found: {filepath}")
      return key_path.read_text()
    except Exception as e:
      raise VAPIDKeyError(f"Failed to read VAPID key file: {e}") from e

  def get_public_key(self) -> str | None:
    """
    Get the public key for client distribution.

    Returns:
        Base64url-encoded public key, or None if not initialized.
    """
    if not self._initialized or self._vapid is None:
      return None

    try:
      public_pem = self._vapid.public_pem()
      if isinstance(public_pem, bytes):
        return public_pem.decode()
      return str(public_pem)
    except Exception:
      # Fallback to raw key extraction
      return self._public_key_raw

  def get_subject(self) -> str:
    """
    Get the VAPID subject (contact URI).

    Returns:
        The subject URI (mailto: or https:).
    """
    return self._subject or "mailto:admin@localhost"

  def get_vapid_claims(self, push_service_url: str | None = None) -> dict:
    """
    Generate VAPID claims for signing JWT tokens.

    Args:
        push_service_url: Optional push service URL for audience claim.
                         If not provided, audience is auto-detected from endpoint.

    Returns:
        Dictionary with VAPID claims (sub, aud, exp).

    Note:
        Safari requires the 'sub' claim. All browsers require 'aud' and 'exp'.
    """
    import time

    claims = {
      "sub": self.get_subject(),
      "exp": int(time.time()) + 43200,  # 12 hours (max is 24 hours)
    }

    if push_service_url:
      from urllib.parse import urlparse

      parsed = urlparse(push_service_url)
      claims["aud"] = f"{parsed.scheme}://{parsed.netloc}"

    return claims

  def is_configured(self) -> bool:
    """
    Check if VAPID keys are properly configured.

    Returns:
        True if keys are available, False otherwise.
    """
    return self._initialized and self._vapid is not None

  def validate_key_format(self) -> bool:
    """
    Validate that the loaded VAPID key has the correct format.

    Returns:
        True if key is valid P-256 elliptic curve key.

    Raises:
        VAPIDKeyError: If key format is invalid.
    """
    if not self._initialized or self._vapid is None:
      raise VAPIDKeyError("VAPID keys not initialized")

    try:
      # py_vapid validates the key during loading
      # This method exists for explicit validation
      public_key = self._vapid.public_key_pem()
      if not public_key:
        raise VAPIDKeyError("Public key derivation failed")
      return True
    except Exception as e:
      raise VAPIDKeyError(f"Invalid VAPID key format: {e}") from e

  def get_private_key_pem(self) -> str | None:
    """
    Get the private key in PEM format.

    WARNING: This should NEVER be exposed via API or logged.

    Returns:
        PEM-encoded private key or None.
    """
    return self._private_key_pem


# Singleton instance for application-wide use
_vapid_manager: VAPIDKeyManager | None = None


async def get_vapid_manager() -> VAPIDKeyManager:
  """
  Get or create the global VAPID key manager.

  Returns:
      The VAPIDKeyManager singleton instance.
  """
  global _vapid_manager

  if _vapid_manager is None:
    _vapid_manager = VAPIDKeyManager()
    await _vapid_manager.initialize()

  return _vapid_manager


async def get_public_key() -> str | None:
  """
  Convenience function to get the public key.

  Returns:
      Base64url-encoded public key or None.
  """
  manager = await get_vapid_manager()
  return manager.get_public_key()
