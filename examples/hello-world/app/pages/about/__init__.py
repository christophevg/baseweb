import os
import logging

from ... import server

logger = logging.getLogger(__name__)

# register the Vue component for the UI
server.register_component("about.js", os.path.dirname(__file__))
server.register_app_route("/about", endpoint="about")
