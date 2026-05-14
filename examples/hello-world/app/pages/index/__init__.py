import os
import logging

from ... import server

logger = logging.getLogger(__name__)

# register the Vue component for the UI
server.register_component("index.js", os.path.dirname(__file__))
server.register_app_route("/", endpoint="index")
