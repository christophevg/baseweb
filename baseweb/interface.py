import os

import logging
logger = logging.getLogger(__name__)

from flask  import render_template, send_from_directory
from flask  import request, redirect, abort
from jinja2 import TemplateNotFound

from baseweb.config import app
from baseweb.web    import server

components = {}

def render(template="main.html"):
  try:
    return render_template(template, app=app, components=components)
  except TemplateNotFound:
    abort(404)
  
@server.route("/")
def render_landing():
  return render()

def register_component(filename, path):
  logger.info("registered component {0} from {1}".format(filename, path))
  components[filename] = path

@server.route("/app/<path:filename>")
def send_app_static(filename):
  return send_from_directory(os.path.join(components[filename]), filename)

@server.route("/static/js/store.js")
def send_main_js():
  return render("store.js")

# catch-all to always render the main page, which will handle the URL

@server.route("/<path:section>")
def render_section(section):
  return render()
