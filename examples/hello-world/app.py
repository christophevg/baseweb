"""
Hello World Example Application

A minimal example demonstrating Vue 3 + Vuetify 3 integration with baseweb.
This validates that the core baseweb setup works correctly after the migration.
"""

from pathlib import Path
from baseweb import Baseweb

# Create baseweb app with custom name
app = Baseweb("hello-world")

# Configure static folder for this example
app.app_static_folder = Path(__file__).parent / "static"

# Register the HelloWorld component
app.register_component(
  filename="HelloWorld.js",
  path=Path(__file__).parent / "static" / "js"
)

# Register the About component
app.register_component(
  filename="About.js",
  path=Path(__file__).parent / "static" / "js"
)

# Register the root route to show HelloWorld
app.register_app_route("/", endpoint="home")

# ASGI entry point for uvicorn/gunicorn
# Note: If socketio is disabled (APP_SOCKETIO=no), _asgi_app is None
# In that case, use the Quart app directly as the ASGI app
asgi_app = app._asgi_app if app._asgi_app is not None else app