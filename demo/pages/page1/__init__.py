import os

# register the Vue component for the UI

from baseweb.interface import register_component

register_component("page1.js", os.path.dirname(__file__))
