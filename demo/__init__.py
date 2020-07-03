import logging
logger = logging.getLogger(__name__)

import os

# load the environment variables for this setup
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())

LOG_LEVEL = os.environ.get("LOG_LEVEL") or "INFO"

# setup logging infrastructure

logging.getLogger("urllib3").setLevel(logging.WARN)

FORMAT  = "[%(asctime)s] [%(name)s] [%(process)d] [%(levelname)s] %(message)s"
DATEFMT = "%Y-%m-%d %H:%M:%S %z"

logging.basicConfig(level=LOG_LEVEL, format=FORMAT, datefmt=DATEFMT)
formatter = logging.Formatter(FORMAT, DATEFMT)

# adjust gunicorn logger to global level and formatting 
logging.getLogger("gunicorn.error").handlers[0].setFormatter(formatter)
logging.getLogger("gunicorn.error").setLevel(logging.INFO)
logging.getLogger("engineio.client").setLevel(logging.WARN)
logging.getLogger("engineio.server").setLevel(logging.WARN)
logging.getLogger("socketio.client").setLevel(logging.WARN)
logging.getLogger("socketio.server").setLevel(logging.WARN)

logging.getLogger().handlers[0].setFormatter(formatter)


from baseweb.web import server

from baseweb.security import add_authenticator

def authenticator(scope, request, *args, **kwargs):
  logger.debug("AUTH: scope:{} / request:{} / args:{} / kwargs:{}".format(
    scope, str(request), str(args), str(kwargs)
  ))
  return True

add_authenticator(authenticator)

import demo.pages.index
import demo.pages.page1
import demo.pages.page2
