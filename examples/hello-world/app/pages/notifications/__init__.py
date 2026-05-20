import os
from ... import server

# Register the Vue component for the UI
# The JS file is stored in the same directory as this __init__.py
server.register_component("notifications.js", os.path.dirname(__file__))
server.register_app_route("/settings/notifications", endpoint="notifications")
