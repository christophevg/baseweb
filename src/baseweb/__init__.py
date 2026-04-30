__version__ = "0.4.3"

import asyncio
import logging
import os
import re
from functools import wraps
from pathlib import Path

import flask_socketio
from dotmap import DotMap
from jinja2 import TemplateNotFound
from pyfiglet import Figlet
from quart import Quart, Response, abort, render_template, request, send_from_directory
from slugify import slugify
from tabulate import tabulate

from baseweb import util

logger = logging.getLogger(__name__)

OK             = [ "yes", "true", "ok" ]
HERE           = Path(__file__).resolve().parent
OPTIONAL_PARAM = re.compile(r"<[^\d\W]\w*\?>", re.UNICODE)

class Baseweb(Quart):
  _banner_shown = False

  def __init__(self, name=None, *args, **kwargs):
    self._show_banner()
    self._load_config()

    if name is None:
      name = self.settings.name

    # create the Quart object part
    super().__init__(name, *args, **kwargs)

    self.template_folder   = HERE / "templates"  # quart property
    self.static_folder     = HERE / "static"     # quart property
    self.app_static_folder = None

    self.authenticator = None

    # TODO: task-3.3 - Migrate to Quart native WebSocket
    # Flask-SocketIO is not compatible with Quart (ASGI)
    # WebSocket support will be re-enabled in task-3.3
    self.socketio = None

    self._files = { "components" : {}, "stylesheets" : {}, "scripts" : [] }
    self._app_routes = {}

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
    settings = tabulate([ [setting, value]
      for setting, value in self.settings.toDict().items()
    ], headers=["setting", "value"], tablefmt="rounded_outline" )
    logger.info(f"current settings:\n{settings}")

  def log_routes(self):
    routes = tabulate([ [ route, config["endpoint"], config["security_scope"]]
      for route, config in self._app_routes.items()
    ], headers=["route", "endpoint", "security_scope"], tablefmt="rounded_outline")
    logger.info(f"current app routes:\n{routes}")

  # SECURITY

  def authenticated(self, scope):
    def decorator(f):
      @wraps(f)
      async def wrapper(*args, **kwargs):
        if not await self._valid_credentials(scope, *args, **kwargs):
          return await self._return_401()
        return await f(*args, **kwargs)
      return wrapper
    return decorator

  async def _valid_credentials(self, scope, *args, **kwargs):
    if scope is None or self.authenticator is None:
      return True

    result = self.authenticator(scope, request, *args, **kwargs)
    # Support both sync and async authenticators
    if asyncio.iscoroutine(result):
      result = await result

    if not result:
      logger.warning("incorrect credentials")
      return False
    return True

  async def _return_401(self):
    return Response("", 401,
      { "WWW-Authenticate": f"Basic realm=\"{self.settings.name}\"" }
    )

  # INTERFACE

  def register_component(self, filename, path, route=None, endpoint=None, security_scope=None):
    self._files["components"][filename] = path
    logger.debug(f"registered component {filename} from {path}")
    if route:
      self.register_app_route(route, endpoint, security_scope)

  def register_stylesheet(self, filename, path):
    self._files["stylesheets"][filename] = path
    logger.debug(f"registered stylesheet {filename} from {path}")

  def register_external_script(self, url):
    self._files["scripts"].append(url)
    logger.debug(f"registered external script: {url}")

  def register_app_route(self, route, endpoint=None, security_scope=None):
    """
    register a valid app route, which returns the app, just like /
    NOTE: this explicit registration replaces the previous catch-all approach
    """
    # Handle optional parameters: /page/<id?> becomes /page/<id> and /page
    # The regex matches <param?> and we create both variants
    optionless_route = re.sub(OPTIONAL_PARAM, "", route)  # Remove optional param entirely
    optionless_route = optionless_route.rstrip('/')  # Remove trailing slash
    route = re.sub(r"\?>", ">", route)  # Convert <id?> to <id>

    # If there was an optional param, register the optionless variant with unique endpoint
    if optionless_route != route.rstrip('/'):
      # Register the optionless variant (without parameter) with a unique endpoint
      # to avoid endpoint conflicts
      optionless_endpoint = f"{slugify(optionless_route)}_base"
      self.register_app_route(optionless_route, endpoint=optionless_endpoint, security_scope=security_scope)

    route_slug = slugify(route)

    if not endpoint:
      endpoint = route_slug

    if not security_scope:
      security_scope = f"ui.route.{endpoint}"

    self._app_routes[route] = {
      "endpoint"       : endpoint,
      "security_scope" : security_scope
    }

    self.route(route, endpoint=endpoint, strict_slashes=False)(
      self._render(security_scope=security_scope)
    )
    logger.debug(f"registered app '{route}' on '{endpoint}' as '{security_scope}'")

  def _setup_routes(self):
    # landing
    self.route("/", endpoint="landing")(
      self._render(security_scope="ui.landing")
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
    async def handler(*args, **kwargs):
      if security_scope is not None:
        if not await self._valid_credentials(security_scope):
          return await self._return_401()
      try:
        content = await render_template(template, app=self.settings, **self._files)
        # Set correct content type based on template extension
        if template.endswith('.js'):
          return Response(content, mimetype='application/javascript')
        elif template.endswith('.json'):
          return Response(content, mimetype='application/json')
        return content
      except TemplateNotFound:
        logger.fatal(f"template not found: {template}")
        abort(404)
    return handler

  def _send(self, kind, security_scope="ui.app.filename"):
    async def handler(filename=None, *args, **kwargs):
      if not await self._valid_credentials(security_scope):
        return await self._return_401()
      try:
        directory = kind[filename]
      except KeyError:
        logger.warning(f"file not found in registry: {filename}")
        abort(404)
      return await send_from_directory(directory, filename)
    return handler

  async def _send_app_static(self, filename):
    if not self.app_static_folder:
      logger.warning("no app static folder configured")
      abort(404)
    try:
      return await send_from_directory(self.app_static_folder, filename)
    except Exception as e:
      # send_from_directory will raise NotFound if file doesn't exist
      # but we catch any exception to ensure proper 404 handling
      logger.warning(f"static file not found: {filename}")
      abort(404)

# expose the classic global, one-for-all baseweb server instance
server = Baseweb()
