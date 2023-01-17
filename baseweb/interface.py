import os

import logging
logger = logging.getLogger(__name__)

from flask  import render_template, send_from_directory
from flask  import request, redirect, abort
from jinja2 import TemplateNotFound

from baseweb.config   import app
from baseweb.web      import server
from baseweb.security import authenticated

components  = {}
stylesheets = {}
scripts     = []

def render(template="main.html"):
  try:
    return render_template(template, app=app, components=components, scripts=scripts, stylesheets=stylesheets)
  except TemplateNotFound:
    abort(404)
  
@server.route("/")
@authenticated("ui.landing")
def render_landing():
  return render()

def register_component(filename, path):
  logger.debug("registered component {0} from {1}".format(filename, path))
  components[filename] = path

@server.route("/app/<path:filename>")
@authenticated("ui.app.filename")
def send_app_static(filename):
  return send_from_directory(os.path.join(components[filename]), filename)

def register_stylesheet(filename, path):
  logger.debug("registered stylesheet {0} from {1}".format(filename, path))
  stylesheets[filename] = path

def register_external_script(url):
  logger.debug(f"registered external script {url}")
  scripts.append(url)

def register_static_folder(folder):
  global send_local_app_static
  @server.route('/app/static/<path:filename>')
  def send_local_app_static(filename):
    return send_from_directory(folder, filename)

@server.route("/app/style/<path:filename>")
@authenticated("ui.app.filename")
def send_app_style(filename):
  return send_from_directory(stylesheets[filename], filename)

@server.route("/static/js/store.js")
@authenticated("ui.static.store.js")
def send_main_js():
  return render("store.js")

if app.style == "pwa":
  @server.route("/manifest.json")
  def manifest():
    return render("manifest.json")

# catch-all to always render the main page, which will handle the URL

@server.route("/<path:section>")
@authenticated("ui.section")
def render_section(section):
  return render()
