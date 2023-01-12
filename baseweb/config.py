import logging
logger = logging.getLogger(__name__)

import os
from dotmap import DotMap

import json

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

app = DotMap({
  k : os.environ.get(f"APP_{k.upper()}", v)
  for k, v in {
    "version"                  : __version__,
    "name"                     : os.path.basename(CWD),
    "short_name"               : None,
    "author"                   : "Unknown Author",
    "description"              : "A baseweb app",
    "color_scheme"             : "dark",
    "color"                    : "rgb(21, 101, 192)",
    "color_name"               : "blue",
    "background_color"         : "rgb(21, 101, 192)",
    "style"                    : "web",
    "icon"                     : None,
    "socketio"                 : "yes",
    "favicon_support"          : "no",
    "favicon_mask_icon_color"  : None,
    "favicon_msapp_tile_color" : None
}.items()})

if app.short_name is None:
  app.short_name = to_camel_case(app.name)

if app.color_scheme == "dark":
  app.color_name += " darken-3"

OK = [ "yes", "true", "ok" ]

app.socketio = app.socketio.lower() in OK
app.favicon_support = app.favicon_support.lower() in OK

logger.info(json.dumps(app.toDict(), indent=2))
