import logging
logger = logging.getLogger(__name__)

import os

import socket

from baseweb       import __version__

CWD = os.getcwd()

class app(object):
  version     = __version__
  name        = os.environ.get("APP_NAME")        or os.path.basename(CWD)
  root        = os.environ.get("APP_ROOT")        or CWD
  author      = os.environ.get("APP_AUTHOR")      or "Unknown Author"
  description = os.environ.get("APP_DESCRIPTION") or "A baseweb app"

logger.debug("baseAdmin config = " + str({
  "app" : {
    "name"        : app.name,
    "root"        : app.root,
    "author"      : app.author,
    "description" : app.description
  }
}))
