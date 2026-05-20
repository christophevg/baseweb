"""
Simple VAPID Key Management for Web Push Notifications.

Loads VAPID keys from environment:
- VAPID_PRIVATE_KEY: PEM-encoded private key (required for production)
- VAPID_SUBJECT: Contact URI (defaults to mailto:admin@localhost)

If VAPID_PRIVATE_KEY is not set, generates temporary keys (not suitable for production).
"""

import base64
import logging
import os

logger = logging.getLogger("gunicorn.error")

# Global VAPID instance (initialized at module import)
_vapid_instance = None
_public_key_cache = None


def get_public_key() -> str:
    """
    Get the VAPID public key as a base64url string.

    This is the key that must be sent to the browser for push subscription.

    Returns:
        Base64url-encoded public key (65 bytes uncompressed P-256 point).

    Raises:
        RuntimeError: If keys cannot be generated or loaded.
    """
    global _vapid_instance

    if _vapid_instance is None:
        raise RuntimeError("VAPID not initialized")

    # Get the public key (cryptography object)
    pub_key = _vapid_instance.public_key

    if pub_key is None:
        raise RuntimeError("VAPID public key is None - key generation failed")

    # Extract raw bytes (uncompressed point format: 0x04 || X || Y)
    from cryptography.hazmat.primitives import serialization

    pub_bytes = pub_key.public_bytes(
        encoding=serialization.Encoding.X962,
        format=serialization.PublicFormat.UncompressedPoint
    )

    # Encode to base64url (no padding)
    return base64.urlsafe_b64encode(pub_bytes).decode('utf-8').rstrip('=')


def get_vapid_claims(push_service_url: str) -> dict:
    """
    Generate VAPID claims for signing.

    Args:
        push_service_url: The push service endpoint URL.

    Returns:
        Dictionary with VAPID claims (sub, aud, exp).
    """
    import time
    from urllib.parse import urlparse

    subject = os.environ.get("VAPID_SUBJECT", "mailto:admin@localhost")
    parsed = urlparse(push_service_url)

    return {
        "sub": subject,
        "aud": f"{parsed.scheme}://{parsed.netloc}",
        "exp": int(time.time()) + 43200,  # 12 hours
    }


def is_configured() -> bool:
    """
    Check if VAPID keys are available.

    Returns:
        True if keys can be generated or loaded.
    """
    return _vapid_instance is not None


def _init_vapid():
    """Initialize VAPID keys at startup."""
    global _vapid_instance, _public_key_cache

    try:
        from py_vapid import Vapid01
    except ImportError:
        logger.warning("py-vapid not installed, VAPID features disabled")
        return

    # Try to load from environment
    private_key_pem = os.environ.get("VAPID_PRIVATE_KEY")

    if private_key_pem:
        logger.info("Loading VAPID keys from environment...")
        try:
            # Clean up the key (remove extra quotes/whitespace from .env)
            key_content = private_key_pem.strip().strip('"').strip("'")
            _vapid_instance = Vapid01.from_pem(key_content.encode())
            logger.info("✓ VAPID keys loaded successfully from environment")
        except Exception as e:
            logger.error(f"✗ Failed to load VAPID key: {e}")
            logger.warning("Falling back to temporary keys...")
            _vapid_instance = Vapid01()
            _vapid_instance.generate_keys()
    else:
        logger.warning("VAPID_PRIVATE_KEY not set - generating temporary keys")
        logger.warning("Set VAPID_PRIVATE_KEY for production use!")
        _vapid_instance = Vapid01()
        _vapid_instance.generate_keys()

    # Cache the public key immediately
    if _vapid_instance:
        try:
            _public_key_cache = get_public_key()
            logger.info(f"✓ VAPID Public Key: {_public_key_cache}")
        except Exception as e:
            logger.error(f"✗ Failed to generate public key: {e}")


# Initialize at module import
_init_vapid()
