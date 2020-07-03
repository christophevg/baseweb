import logging
logger = logging.getLogger(__name__)

from functools import wraps

from flask import request

from flask_socketio import SocketIO, emit, join_room, leave_room, disconnect

from baseweb.web      import server
from baseweb.security import authenticated

socketio = SocketIO(server)

@socketio.on('connect')
@authenticated("io.connect")
def on_connect():
  logger.info("connect: {0}".format(request.sid))

@socketio.on('disconnect')
@authenticated("io.disconnect")
def on_disconnect():
  logger.info("disconnect: {0}".format(request.sid))
