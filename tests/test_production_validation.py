"""Tests for Production Environment Validation.

This module tests security validations that enforce production requirements:
- VAPID key validation in production
- IP hash salt validation in production

Requirements:
- Production environments must have VAPID_PRIVATE_KEY set
- Production environments must have IP_HASH_SALT set
- Development environments should work with defaults/automatic generation
"""

import pytest

from baseweb.push import hash_ip
from baseweb.vapid import VAPIDKeyError, _init_vapid


class TestVAPIDProductionValidation:
  """
  Tests for VAPID key validation in production environments.

  In production, VAPID_PRIVATE_KEY must be explicitly set.
  In development, temporary keys can be generated automatically.
  """

  def test_vapid_missing_key_in_production_raises_error(self, monkeypatch):
    """
    Given: ENVIRONMENT=production and VAPID_PRIVATE_KEY not set
    When: Initializing VAPID
    Then: Should raise VAPIDKeyError with helpful message
    """
    # Set production environment
    monkeypatch.setenv("ENVIRONMENT", "production")
    monkeypatch.delenv("VAPID_PRIVATE_KEY", raising=False)

    with pytest.raises(VAPIDKeyError) as exc_info:
      _init_vapid()

    error_message = str(exc_info.value)
    assert "VAPID_PRIVATE_KEY" in error_message
    assert "required in production" in error_message
    assert "Generate keys using" in error_message or "python -c" in error_message

  def test_vapid_missing_key_in_baseweb_production_raises_error(self, monkeypatch):
    """
    Given: BASEWEB_ENV=production and VAPID_PRIVATE_KEY not set
    When: Initializing VAPID
    Then: Should raise VAPIDKeyError
    """
    # Set production environment via BASEWEB_ENV
    monkeypatch.setenv("BASEWEB_ENV", "production")
    monkeypatch.delenv("ENVIRONMENT", raising=False)
    monkeypatch.delenv("VAPID_PRIVATE_KEY", raising=False)

    with pytest.raises(VAPIDKeyError) as exc_info:
      _init_vapid()

    assert "VAPID_PRIVATE_KEY" in str(exc_info.value)

  def test_vapid_missing_key_in_development_generates_temporary_keys(self, monkeypatch):
    """
    Given: ENVIRONMENT=development (default) and VAPID_PRIVATE_KEY not set
    When: Initializing VAPID
    Then: Should generate temporary keys successfully
    """
    # Ensure development environment
    monkeypatch.setenv("ENVIRONMENT", "development")
    monkeypatch.delenv("BASEWEB_ENV", raising=False)
    monkeypatch.delenv("VAPID_PRIVATE_KEY", raising=False)

    # Should not raise error
    _init_vapid()

    # Import after init to check if it worked
    from baseweb.vapid import is_configured

    assert is_configured()

  def test_vapid_key_present_in_production_works(self, monkeypatch):
    """
    Given: ENVIRONMENT=production and VAPID_PRIVATE_KEY is set
    When: Initializing VAPID
    Then: Should load key successfully
    """
    try:
      from py_vapid import Vapid01
    except ImportError:
      pytest.skip("py-vapid not installed")

    # Generate a valid key
    vapid = Vapid01()
    vapid.generate_keys()
    private_key_pem = vapid.private_pem()
    if isinstance(private_key_pem, bytes):
      private_key_pem = private_key_pem.decode()

    # Set production environment with valid key
    monkeypatch.setenv("ENVIRONMENT", "production")
    monkeypatch.setenv("VAPID_PRIVATE_KEY", private_key_pem)

    # Should not raise error
    _init_vapid()

    from baseweb.vapid import is_configured

    assert is_configured()


class TestIPHashSaltProductionValidation:
  """
  Tests for IP hash salt validation in production environments.

  In production, IP_HASH_SALT must be explicitly set.
  In development, a default salt can be used.
  """

  def test_hash_ip_missing_salt_in_production_raises_error(self, monkeypatch):
    """
    Given: ENVIRONMENT=production and IP_HASH_SALT not set
    When: Hashing IP address
    Then: Should raise ValueError with helpful message
    """
    monkeypatch.setenv("ENVIRONMENT", "production")
    monkeypatch.delenv("IP_HASH_SALT", raising=False)

    with pytest.raises(ValueError) as exc_info:
      hash_ip("192.168.1.1")

    error_message = str(exc_info.value)
    assert "IP_HASH_SALT" in error_message
    assert "required in production" in error_message
    assert "secrets.token_hex" in error_message or "python -c" in error_message

  def test_hash_ip_missing_salt_in_baseweb_production_raises_error(self, monkeypatch):
    """
    Given: BASEWEB_ENV=production and IP_HASH_SALT not set
    When: Hashing IP address
    Then: Should raise ValueError
    """
    monkeypatch.setenv("BASEWEB_ENV", "production")
    monkeypatch.delenv("ENVIRONMENT", raising=False)
    monkeypatch.delenv("IP_HASH_SALT", raising=False)

    with pytest.raises(ValueError) as exc_info:
      hash_ip("192.168.1.1")

    assert "IP_HASH_SALT" in str(exc_info.value)

  def test_hash_ip_missing_salt_in_development_uses_default(self, monkeypatch):
    """
    Given: ENVIRONMENT=development (default) and IP_HASH_SALT not set
    When: Hashing IP address
    Then: Should use default salt and return hash
    """
    monkeypatch.setenv("ENVIRONMENT", "development")
    monkeypatch.delenv("BASEWEB_ENV", raising=False)
    monkeypatch.delenv("IP_HASH_SALT", raising=False)

    # Should not raise error
    result = hash_ip("192.168.1.1")

    # Should return a hash
    assert result is not None
    assert len(result) == 16  # First 16 characters of SHA256
    # Same IP should produce same hash with same salt
    result2 = hash_ip("192.168.1.1")
    assert result == result2

  def test_hash_ip_with_salt_returns_consistent_hash(self, monkeypatch):
    """
    Given: IP_HASH_SALT is set
    When: Hashing IP addresses
    Then: Should return consistent hashes
    """
    monkeypatch.setenv("IP_HASH_SALT", "test-salt-value")

    # Hash same IP twice
    hash1 = hash_ip("192.168.1.1")
    hash2 = hash_ip("192.168.1.1")

    # Should be identical
    assert hash1 == hash2

    # Different IPs should produce different hashes
    hash3 = hash_ip("192.168.1.2")
    assert hash1 != hash3

  def test_hash_ip_different_salts_produce_different_hashes(self, monkeypatch):
    """
    Given: Different IP_HASH_SALT values
    When: Hashing same IP address
    Then: Should produce different hashes
    """
    monkeypatch.setenv("IP_HASH_SALT", "salt-1")
    hash1 = hash_ip("192.168.1.1")

    monkeypatch.setenv("IP_HASH_SALT", "salt-2")
    hash2 = hash_ip("192.168.1.1")

    # Different salts should produce different hashes
    assert hash1 != hash2


class TestEnvironmentDetection:
  """
  Tests for environment detection logic.

  Both ENVIRONMENT and BASEWEB_ENV should be checked.
  """

  def test_environment_variable_takes_precedence(self, monkeypatch):
    """
    Given: Both ENVIRONMENT and BASEWEB_ENV set
    When: Checking environment
    Then: Either one being 'production' should trigger production mode
    """
    # Test ENVIRONMENT=production
    monkeypatch.setenv("ENVIRONMENT", "production")
    monkeypatch.setenv("BASEWEB_ENV", "development")
    monkeypatch.delenv("VAPID_PRIVATE_KEY", raising=False)

    with pytest.raises(VAPIDKeyError):
      _init_vapid()

  def test_baseweb_env_variable_checked(self, monkeypatch):
    """
    Given: BASEWEB_ENV=production, ENVIRONMENT not set
    When: Checking environment
    Then: Should detect production mode
    """
    monkeypatch.setenv("BASEWEB_ENV", "production")
    monkeypatch.delenv("ENVIRONMENT", raising=False)
    monkeypatch.delenv("VAPID_PRIVATE_KEY", raising=False)

    with pytest.raises(VAPIDKeyError):
      _init_vapid()

  def test_default_environment_is_development(self, monkeypatch):
    """
    Given: Neither ENVIRONMENT nor BASEWEB_ENV set
    When: Checking environment
    Then: Should default to development mode
    """
    monkeypatch.delenv("ENVIRONMENT", raising=False)
    monkeypatch.delenv("BASEWEB_ENV", raising=False)
    monkeypatch.delenv("VAPID_PRIVATE_KEY", raising=False)

    # Should not raise - development mode allows temporary keys
    _init_vapid()


class TestErrorMessages:
  """
  Tests for error message quality.

  Error messages should be helpful and actionable.
  """

  def test_vapid_error_message_includes_generation_command(self, monkeypatch):
    """
    Given: Missing VAPID_PRIVATE_KEY in production
    When: Error is raised
    Then: Message should include command to generate keys
    """
    monkeypatch.setenv("ENVIRONMENT", "production")
    monkeypatch.delenv("VAPID_PRIVATE_KEY", raising=False)

    with pytest.raises(VAPIDKeyError) as exc_info:
      _init_vapid()

    error_message = str(exc_info.value)
    # Should include instructions
    assert "python -c" in error_message or "Generate" in error_message
    # Should mention VAPID
    assert "VAPID" in error_message.upper() or "vapid" in error_message.lower()

  def test_ip_hash_error_message_includes_generation_command(self, monkeypatch):
    """
    Given: Missing IP_HASH_SALT in production
    When: Error is raised
    Then: Message should include command to generate salt
    """
    monkeypatch.setenv("ENVIRONMENT", "production")
    monkeypatch.delenv("IP_HASH_SALT", raising=False)

    with pytest.raises(ValueError) as exc_info:
      hash_ip("192.168.1.1")

    error_message = str(exc_info.value)
    # Should include instructions
    assert "python -c" in error_message or "secrets" in error_message
    # Should mention IP_HASH_SALT
    assert "IP_HASH_SALT" in error_message
