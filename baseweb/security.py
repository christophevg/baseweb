import logging
logger = logging.getLogger(__name__)

from functools import wraps

from flask import request, Response

from baseweb import config

authenticator = None

def add_authenticator(f):
  global authenticator
  logger.info("authenticator registered")
  authenticator = f

def valid_credentials(scope, *args, **kwargs):
  if authenticator is None: return True
  if not authenticator(scope, request, *args, **kwargs):
    logger.warn("incorrect credentials")
    return False
  return True

def authenticated(scope):
  def decorator(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
      if not valid_credentials(scope, *args, **kwargs):
        return Response( "", 401,
          { 'WWW-Authenticate': 'Basic realm="' + config.app.name + '"' }
        )
      return f(*args, **kwargs)
    return wrapper
  return decorator
