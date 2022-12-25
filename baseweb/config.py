import logging
logger = logging.getLogger(__name__)

import os

import socket

from baseweb import __version__

CWD = os.getcwd()

def to_camel_case(text):
  """
  credits to https://stackoverflow.com/a/60978847
  """
  s = text.replace("-", " ").replace("_", " ")
  s = s.split()
  if len(text) == 0:
    return text
  return "".join(i.capitalize() for i in s)

class app(object):
  version     = __version__
  name        = os.environ.get("APP_NAME",             os.path.basename(CWD))
  short_name  = os.environ.get("APP_SHORT_NAME",       to_camel_case(name))
  root        = os.environ.get("APP_ROOT",             CWD)
  author      = os.environ.get("APP_AUTHOR",           "Unknown Author")
  description = os.environ.get("APP_DESCRIPTION",      "A baseweb app")
  scheme      = os.environ.get("APP_COLOR_SCHEME",     "dark")
  color       = os.environ.get("APP_COLOR",            "rgb(21, 101, 192)")
  color_name  = os.environ.get("APP_COLOR_NAME",       "blue") + " darken-3" if scheme == "dark" else ""
  bgcolor     = os.environ.get("APP_BACKGROUND_COLOR", "rgb(21, 101, 192)")
  style       = os.environ.get("APP_STYLE",            "web")
  icon        = os.environ.get("APP_ICON",             None)
  socketio    = os.environ.get("APP_SOCKETIO",         "yes").lower() in [ "yes", "true", "ok" ]

logger.debug("baseAdmin config = " + str({
  "app" : {
    "version"     : app.version,
    "name"        : app.name,
    "short_name"  : app.short_name,
    "root"        : app.root,
    "author"      : app.author,
    "description" : app.description,
    "scheme"      : app.scheme,
    "color"       : app.color,
    "color_name"  : app.color_name,
    "bgcolor"     : app.bgcolor,
    "style"       : app.style,
    "icon"        : app.icon,
    "socketio"    : app.socketio
  }
}))
