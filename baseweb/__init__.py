__version__ = "0.3.2"

import logging
import os
from functools import wraps
from pathlib import Path

from pyfiglet import Figlet
from dotmap import DotMap
import json

from flask import Flask, request, Response, render_template, send_from_directory
from flask import abort
from jinja2 import TemplateNotFound
import flask_restful
import flask_socketio

from baseweb import util

logger = logging.getLogger(__name__)

OK   = [ "yes", "true", "ok" ]
HERE = Path(__file__).resolve().parent

class Baseweb(Flask):
  _banner_shown = False

  def __init__(self, name=None, *args, **kwargs):
    self._show_banner()
    self._load_config()

    if name is None:
      name = self.settings.name

    # create the Fask object part
    super().__init__(name, *args, **kwargs)

    self.template_folder   = HERE / "templates"  # flask property
    self.static_folder     = HERE / "static"     # flask property
    self.app_static_folder = None

    self.request       = request
    self.authenticator = None

    self.api      = flask_restful.Api(self)
    self.socketio = flask_socketio.SocketIO(self)

    self._files = { "components" : {}, "stylesheets" : {}, "scripts" : [] }

    self._setup_routes()

  def _show_banner(self):
    if not Baseweb._banner_shown:
      custom_fig = Figlet(font="standard")
      banner = str(custom_fig.renderText("baseweb")).rstrip()
      logger.info( f"\n{banner} {__version__}")
      Baseweb._banner_shown = True

  # CONFIG

  def _load_config(self):
    # load configuration from environment variables with some sane defaults
    self.settings = DotMap({
      k : os.environ.get(f"APP_{k.upper()}", v)
      for k, v in {
        "version"                  : __version__,
        "url"                      : None,
        "name"                     : os.path.basename(os.getcwd()),
        "title"                    : os.path.basename(os.getcwd()),
        "short_name"               : None,
        "author"                   : "Unknown Author",
        "description"              : "A baseweb app",
        "social_image"             : None,
        "color_scheme"             : "dark",
        "color"                    : "rgb(21, 101, 192)",
        "color_name"               : "blue",
        "background_color"         : "rgb(21, 101, 192)",
        "style"                    : "web",
        "icon"                     : None,
        "socketio"                 : "yes",
        "favicon_support"          : "no",
        "favicon_mask_icon_color"  : None,
        "favicon_msapp_tile_color" : None,
        "keep_alive"               : "no"
    }.items()})

    if self.settings.short_name is None:
      self.settings.short_name = util.to_camel_case(self.settings.name)

    if self.settings.color_scheme == "dark":
      self.settings.color_name += " darken-3"

    self.settings.socketio        = self.settings.socketio.lower() in OK
    self.settings.favicon_support = self.settings.favicon_support.lower() in OK
    self.settings.keep_alive      = self.settings.keep_alive.lower() in OK

  def log_config(self):
    settings = json.dumps(self.settings.toDict(), indent=2)
    logger.info(f"📌 current settings: {settings}")

  # SECURITY

  def authenticated(self, scope):
    def decorator(f):
      @wraps(f)
      def wrapper(*args, **kwargs):
        if not self._valid_credentials(scope, *args, **kwargs):
          return self._return_401()
        return f(*args, **kwargs)
      return wrapper
    return decorator
  
  def _valid_credentials(self, scope, *args, **kwargs):
    if scope is None or self.authenticator is None:
      return True
    if not self.authenticator(scope, request, *args, **kwargs):
      logger.warning("👮‍♂️ incorrect credentials")
      return False
    return True

  def _return_401(self):
    return Response( "", 401,
      { "WWW-Authenticate": f"Basic realm=\"{self.settings.name}\"" }
    )

  # INTERFACE
  
  def register_component(self, filename, path):
    self._files["components"][filename] = path
    logger.debug("🧩 registered component {0} from {1}".format(filename, path))

  def register_stylesheet(self, filename, path):
    self._files["stylesheets"][filename] = path
    logger.debug("🧩 registered stylesheet {0} from {1}".format(filename, path))

  def register_external_script(self, url):
    self._files["scripts"].append(url)
    logger.debug(f"🧩 registered external script: {url}")

  def _setup_routes(self):
    # landing
    self.route("/", endpoint="landing")(
      self._render(security_scope="ui.landing")
    )

    # catch-all to always render the main page, which will handle the URL
    self.route("/<path:section>", endpoint="catch-all")(
      self._render(security_scope="ui.section")
    )

    # the vuex store
    self.route("/static/js/store.js", endpoint="store")(
      self._render("store.js", security_scope="ui.static.store.js")
    )
    
    # only provide manifest when run as PWA
    if self.settings.style == "pwa":
      self.route("/manifest.json", endpoint="manifest")(
        self._render("manifest.json")
      )

    # app files
    self.route("/app/<path:filename>", endpoint="app")(
      self._send(self._files["components"])
    )
    self.route("/app/style/<path:filename>", endpoint="app-style")(
     self._send(self._files["stylesheets"])
    )
    self.route("/app/static/<path:filename>")(
      self._send_app_static
    )
  
  def _render(self, template="main.html", security_scope=None):
    def handler(*args, **kwargs):
      if not self._valid_credentials(security_scope):
        return self._return_401()
      try:
        return render_template(template, app=self.settings, **self._files)
      except TemplateNotFound:
        logger.fatal(f"🕵️‍♂️ template not found: {template}")
        abort(404)
    return handler

  def _send(self, kind, security_scope="ui.app.filename"):
    def handler(filename=None, *args, **kwargs):
      if not self._valid_credentials(security_scope):
        return self._return_401()
      return send_from_directory(kind[filename], filename)
    return handler

  def _send_app_static(self, filename):
    if not self.app_static_folder:
      logger.warning("⚠️ no app static folder configured")
      abort(404)
    return send_from_directory(self.app_static_folder, filename)

# expose the classic global, one-for-all baseweb server instance
server = Baseweb()
