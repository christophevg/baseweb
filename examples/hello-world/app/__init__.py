"""
Hello World Example Application

A minimal example demonstrating Vue 3 + Vuetify 3 integration with baseweb.
This validates that the core baseweb setup works correctly after the migration.
"""

# Load environment variables from .env file (for local development)
from dotenv import load_dotenv
load_dotenv()

from baseweb import Baseweb

# Create baseweb app with custom name
server = Baseweb(
  "hello-world",
  settings={
    "main_template": "minimal.html"   # use the minimal.html template
  }
)

from . import pages # noqa: E402, I001

# ASGI entry point for uvicorn/gunicorn
# Note: If socketio is disabled (APP_SOCKETIO=no), _asgi_app is None
# In that case, use the Quart app directly as the ASGI app
asgi_app = server._asgi_app if server._asgi_app is not None else app

# all set up...
server.log_config()
server.log_routes()
