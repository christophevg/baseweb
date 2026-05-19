__version__ = "0.5.1"

import asyncio
import inspect
import json
import logging
import os
import re
from functools import wraps
from pathlib import Path
from typing import TypedDict

import socketio  # type: ignore[import-untyped]
from dotmap import DotMap  # type: ignore[import-untyped]
from jinja2 import TemplateNotFound
from pyfiglet import Figlet
from quart import (
  Quart,
  Response,
  abort,
  render_template,
  render_template_string,
  request,
  send_from_directory,
)
from slugify import slugify
from socketio.exceptions import ConnectionRefusedError  # type: ignore[import-untyped]
from tabulate import tabulate

from baseweb import util
from baseweb.resource import Resource as Resource

OK = ["yes", "true", "ok"]
HERE = Path(__file__).resolve().parent
OPTIONAL_PARAM = re.compile(r"<[^\d\W]\w*\?>", re.UNICODE)


class FilesDict(TypedDict):
  """Type for the _files registry."""

  components: dict[str, Path]
  stylesheets: dict[str, Path]
  scripts: list[str]


class Baseweb(Quart):
  _banner_shown: bool = False

  def __init__(self, name=None, settings=None, *args, **kwargs):
    self._load_config(settings)

    if name is None:
      name = self.settings.name

    # create the Quart object part
    super().__init__(name, *args, **kwargs)

    # wire logging to gunicorn logging if available
    logger = logging.getLogger("gunicorn.error")
    if logger:
      self.logger.handlers = logger.handlers
      self.logger.setLevel(logger.level)

    self._show_banner()

    self.template_folder = str(HERE / "templates")
    self.static_folder = str(HERE / "static")
    self.app_static_folder: Path | None = None

    self.authenticator = None

    # Initialize Socket.IO in ASGI mode for Quart compatibility
    if self.settings.socketio:
      self._sio = socketio.AsyncServer(async_mode="asgi", cors_allowed_origins="*")
      self._asgi_app = socketio.ASGIApp(self._sio, self)
      self.socketio = self._sio
    else:
      self._sio = None
      self._asgi_app = None
      self.socketio = None

    self._files: FilesDict = {"components": {}, "stylesheets": {}, "scripts": []}
    self._app_routes = {}

    self._setup_routes()

  def _show_banner(self):
    if not Baseweb._banner_shown:
      custom_fig = Figlet(font="standard")
      banner = str(custom_fig.renderText("baseweb")).rstrip()
      self.logger.info(f"\n{banner} {__version__}")
      Baseweb._banner_shown = True

  # CONFIG

  def _load_config(self, settings=None):
    # load configuration from environment variables with some sane defaults
    self.settings = DotMap(
      {
        k: os.environ.get(f"APP_{k.upper()}", v)
        for k, v in {
          "version": __version__,
          "url": None,
          "name": os.path.basename(os.getcwd()),
          "title": os.path.basename(os.getcwd()),
          "short_name": None,
          "author": "Unknown Author",
          "description": "A baseweb app",
          "main_template": None,
          "social_image": None,
          "color_scheme": "dark",
          "color": "rgb(21, 101, 192)",
          "color_name": "blue",
          "background_color": "rgb(21, 101, 192)",
          "style": "web",
          "icon": None,
          "socketio": "yes",
          "favicon_support": "no",
          "favicon_mask_icon_color": None,
          "favicon_msapp_tile_color": None,
          "keep_alive": "no",
        }.items()
      }
    )
    if settings:
      self.settings.update(settings)

    if self.settings.short_name is None:
      self.settings.short_name = util.to_camel_case(self.settings.name)

    if self.settings.main_template is None:
      # default to main.html
      self.settings.main_template = "main.html"
    else:
      # if filepath to actual file, use that, else keep simple template name
      filepath = Path(self.settings.main_template).resolve()
      if filepath.is_file():
        self.settings.main_template = str(filepath)

    if self.settings.color_scheme == "dark":
      self.settings.color_name += " darken-3"

    self.settings.socketio = self.settings.socketio.lower() in OK
    self.settings.favicon_support = self.settings.favicon_support.lower() in OK
    self.settings.keep_alive = self.settings.keep_alive.lower() in OK

  def log_config(self):
    settings = tabulate(
      [[setting, value] for setting, value in self.settings.toDict().items()],
      headers=["setting", "value"],
      tablefmt="rounded_outline",
    )
    self.logger.info(f"current settings:\n{settings}")

  def log_routes(self):
    routes = tabulate(
      [
        [route, config["endpoint"], config["security_scope"]]
        for route, config in self._app_routes.items()
      ],
      headers=["route", "endpoint", "security_scope"],
      tablefmt="rounded_outline",
    )
    self.logger.info(f"current app routes:\n{routes}")

  # SECURITY

  def authenticated(self, scope):
    """Decorator for authentication. Works with both HTTP and SocketIO handlers."""

    def decorator(f):
      @wraps(f)
      async def wrapper(*args, **kwargs):
        # Check if this is a SocketIO handler (first arg is sid string)
        # vs HTTP handler (request context is available)
        is_socketio = len(args) > 0 and isinstance(args[0], str) and self._sio is not None

        if is_socketio:
          # SocketIO context: use sid for authentication
          sid = args[0]
          if not await self._valid_socket_credentials(scope, sid, *args[1:], **kwargs):
            raise ConnectionRefusedError("Unauthorized")
        else:
          # HTTP context: use request
          if not await self._valid_credentials(scope, *args, **kwargs):
            return await self._return_401()

        return await f(*args, **kwargs)

      return wrapper

    return decorator

  async def _valid_credentials(self, scope, *args, **kwargs):
    """Validate credentials for HTTP requests."""
    if scope is None or self.authenticator is None:
      return True

    result = self.authenticator(scope, request, *args, **kwargs)
    # Support both sync and async authenticators
    if asyncio.iscoroutine(result):
      result = await result

    if not result:
      self.logger.warning("incorrect credentials")
      return False
    return True

  async def _valid_socket_credentials(self, scope, sid, *args, **kwargs):
    """Validate credentials for Socket.IO connections."""
    if scope is None or self.authenticator is None:
      return True

    # For SocketIO, pass sid instead of request
    # Create a minimal request-like object for compatibility
    class SocketRequest:
      def __init__(self, sid):
        self.sid = sid

    socket_request = SocketRequest(sid)
    result = self.authenticator(scope, socket_request, *args, **kwargs)

    # Support both sync and async authenticators
    if asyncio.iscoroutine(result):
      result = await result

    if not result:
      self.logger.warning(f"incorrect credentials for socket {sid}")
      return False
    return True

  async def _return_401(self):
    return Response("", 401, {"WWW-Authenticate": f'Basic realm="{self.settings.name}"'})

  # INTERFACE

  def register_component(self, filename, path, route=None, endpoint=None, security_scope=None):
    self._files["components"][filename] = path
    self.logger.debug(f"registered component {filename} from {path}")
    if route:
      self.register_app_route(route, endpoint, security_scope)

  def register_stylesheet(self, filename, path):
    self._files["stylesheets"][filename] = path
    self.logger.debug(f"registered stylesheet {filename} from {path}")

  def register_external_script(self, url):
    self._files["scripts"].append(url)
    self.logger.debug(f"registered external script: {url}")

  def register_app_route(self, route, endpoint=None, security_scope=None):
    """
    register a valid app route, which returns the app, just like /
    NOTE: this explicit registration replaces the previous catch-all approach
    """
    # Handle optional parameters: /page/<id?> becomes /page/<id> and /page
    # The regex matches <param?> and we create both variants
    optionless_route = re.sub(OPTIONAL_PARAM, "", route)  # Remove optional param entirely
    optionless_route = optionless_route.rstrip("/")  # Remove trailing slash
    route = re.sub(r"\?>", ">", route)  # Convert <id?> to <id>

    # If there was an optional param, register the optionless variant with unique endpoint
    if optionless_route != route.rstrip("/"):
      # Register the optionless variant (without parameter) with a unique endpoint
      # to avoid endpoint conflicts
      optionless_endpoint = f"{slugify(optionless_route)}_base"
      self.register_app_route(
        optionless_route, endpoint=optionless_endpoint, security_scope=security_scope
      )

    route_slug = slugify(route)

    if not endpoint:
      endpoint = route_slug

    if not security_scope:
      security_scope = f"ui.route.{endpoint}"

    self._app_routes[route] = {"endpoint": endpoint, "security_scope": security_scope}

    self.route(route, endpoint=endpoint, strict_slashes=False)(
      self._render(security_scope=security_scope)
    )
    self.logger.debug(f"registered app '{route}' on '{endpoint}' as '{security_scope}'")

  def _setup_routes(self):
    # landing
    self.route("/", endpoint="landing")(self._render(security_scope="ui.landing"))

    # the vuex store
    self.route("/static/js/store.js", endpoint="store")(
      self._render("store.js", security_scope="ui.static.store.js")
    )

    # only provide manifest when run as PWA
    if self.settings.style == "pwa":
      self.route("/manifest.json", endpoint="manifest")(self._render("manifest.json"))
      self.route("/sw.js", endpoint="service-worker")(self._serve_service_worker())

    # app files
    self.route("/app/<path:filename>", endpoint="app")(self._send(self._files["components"]))
    self.route("/app/style/<path:filename>", endpoint="app-style")(
      self._send(self._files["stylesheets"])
    )
    self.route("/app/static/<path:filename>")(self._send_app_static)

  def _render(self, template=None, security_scope=None):
    if template is None:
      template = self.settings.main_template

    async def handler(*args, **kwargs):
      if security_scope is not None:
        if not await self._valid_credentials(security_scope):
          return await self._return_401()
      try:
        # template can be absolute path or filename of template
        if template.startswith("/"):
          content = await render_template_string(
            Path(template).read_text(), app=self.settings, **self._files
          )
        else:
          content = await render_template(template, app=self.settings, **self._files)

        # Set correct content type based on template extension
        if template.endswith(".js"):
          return Response(content, mimetype="application/javascript")
        elif template.endswith(".json"):
          return Response(content, mimetype="application/json")
        return content
      except TemplateNotFound:
        self.logger.fatal(f"template not found: {template}")
        abort(404)

    return handler

  def _send(self, kind, security_scope="ui.app.filename"):
    async def handler(filename=None, *args, **kwargs):
      if not await self._valid_credentials(security_scope):
        return await self._return_401()
      try:
        directory = kind[filename]
      except KeyError:
        self.logger.warning(f"file not found in registry: {filename}")
        abort(404)
      return await send_from_directory(directory, filename)

    return handler

  async def _send_app_static(self, filename):
    if not self.app_static_folder:
      self.logger.warning("no app static folder configured")
      abort(404)
    try:
      return await send_from_directory(self.app_static_folder, filename)
    except Exception:
      # send_from_directory will raise NotFound if file doesn't exist
      # but we catch any exception to ensure proper 404 handling
      self.logger.warning(f"static file not found: {filename}")
      abort(404)

  def _serve_service_worker(self):
    """Serve the Service Worker script with appropriate headers."""

    async def handler():
      sw_path = HERE / "static" / "js" / "sw.js"
      try:
        content = sw_path.read_text()
        response = Response(content, mimetype="application/javascript")
        response.headers["Service-Worker-Allowed"] = "/"
        return response
      except FileNotFoundError:
        self.logger.warning("service worker script not found")
        abort(404)

    return handler

  def add_resource(self, resource_or_class, route, endpoint=None, security_scope=None):
    """
    Register a Resource at a route.

    Args:
        resource_or_class: A Resource subclass (instantiated on each request)
                           or a Resource instance (reused across requests)
        route: URL pattern (e.g., '/users/<int:user_id>')
        endpoint: Optional endpoint name (default: auto-generated)
        security_scope: Optional security scope for authentication

    Returns:
        The handler function

    Examples:
        # Class - new instance per request (stateless):
        class UserResource(Resource):
            async def get(self, user_id):
                return {"user": user_id}
        server.add_resource(UserResource, '/users/<int:user_id>')

        # Instance - reused across requests (stateful):
        user_resource = UserResource()
        user_resource.db = database_connection
        server.add_resource(user_resource, '/users/<int:user_user_id>')
    """
    # Determine if we got a class or an instance
    is_class = inspect.isclass(resource_or_class)

    if is_class:
      resource_class = resource_or_class
      resource_instance = None
    else:
      resource_class = resource_or_class.__class__
      resource_instance = resource_or_class

    async def handler(*args, **kwargs):
      # Check authentication if security_scope is set
      if security_scope is not None:
        if not await self._valid_credentials(security_scope, *args, **kwargs):
          return await self._return_401()

      # Use existing instance or create new one
      if resource_instance is not None:
        resource = resource_instance
      else:
        resource = resource_class()

      method = request.method.lower()
      method_func = getattr(resource, method, None)
      if method_func is None or not callable(method_func):
        abort(405)
      result = await method_func(*args, **kwargs)

      # Handle tuple responses (body, status, headers) or (body, status)
      if isinstance(result, tuple):
        if len(result) == 2:
          body, status = result
          # For 204 No Content, return empty response without content-type
          if status == 204:
            return Response("", status=status)
          # For other responses, handle body appropriately
          if body is None:
            return Response("", status=status)
          # Convert dict to JSON string if needed
          if isinstance(body, dict):
            body = json.dumps(body)
          return Response(body, status=status, mimetype="application/json")
        elif len(result) == 3:
          body, status, headers = result
          if body is None:
            return Response("", status=status, headers=headers)
          # Convert dict to JSON string if needed
          if isinstance(body, dict):
            body = json.dumps(body)
          return Response(body, status=status, headers=headers, mimetype="application/json")

      # Handle single dict response - convert to JSON
      if isinstance(result, dict):
        return Response(json.dumps(result), mimetype="application/json")

      # For other types (str, Response, etc.), return as-is
      # Let the application code decide the content-type
      return result

    if endpoint is None:
      # Generate endpoint name from route, removing parameter markers
      endpoint = slugify(
        route.replace("<", "")
        .replace(">", "")
        .replace("int:", "")
        .replace("path:", "")
        .replace("string:", "")
      )

    self.route(route, methods=resource_class.methods, endpoint=endpoint)(handler)
    return handler
