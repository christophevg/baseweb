import logging

# import traceback

from flask import Flask

logger = logging.getLogger(__name__)

server = Flask(__name__)

logger.info("baseweb web server is ready...")
