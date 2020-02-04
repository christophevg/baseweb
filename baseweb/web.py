import logging
logger = logging.getLogger(__name__)

# import traceback

from flask import Flask

server = Flask(__name__)

import baseweb.interface
import baseweb.rest
import baseweb.socketio

logger.info("baseweb web server is ready...")
