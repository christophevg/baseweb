"""
Hello World Example Application

A minimal example demonstrating Vue 3 + Vuetify 3 integration with baseweb.
This validates that the core baseweb setup works correctly after the migration.
"""

# Load environment variables from .env file (for local development)
from dotenv import load_dotenv
load_dotenv()

from baseweb import Baseweb
from baseweb.config import BasewebConfig

# Create baseweb app with custom name
config = BasewebConfig(name="hello-world")
server = Baseweb(config)

from . import pages # noqa: E402, I001
from .pages import notifications # Ensure notifications page is registered
from baseweb.push import register_push_resources
from quart import request

# Simple dummy authenticator for the hello-world example
# This allows testing push notifications without a full auth system
async def dummy_authenticator(scope, req, *args, **kwargs):
  # Set a dummy user ID on the request object
  req.user_id = "hello-world-user"
  # Allow sending push notifications in demo mode
  req.is_admin = True
  return True

server.authenticator = dummy_authenticator

# Register push notification resources (VAPID, subscriptions, etc.)
register_push_resources(server)


# ASGI entry point for uvicorn/gunicorn
# Note: If socketio is disabled (APP_SOCKETIO=no), _asgi_app is None
# In that case, use the Quart app directly as the ASGI app
asgi_app = server._asgi_app if server._asgi_app is not None else app

# all set up...
server.log_config()
server.log_routes()
