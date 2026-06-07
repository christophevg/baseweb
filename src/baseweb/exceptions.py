"""Custom exceptions for baseweb."""


class BasewebError(Exception):
  """Base exception for baseweb."""

  pass


class VAPIDKeyError(BasewebError):
  """Raised when VAPID configuration is missing or invalid."""

  pass


class ConfigurationError(BasewebError):
  """Raised when configuration is invalid."""

  pass


class PushNotificationError(BasewebError):
  """Raised when push notification fails."""

  pass
