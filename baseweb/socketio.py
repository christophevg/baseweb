import logging
logger = logging.getLogger(__name__)

from functools import wraps

from flask import request

from flask_socketio import SocketIO, emit, join_room, leave_room, disconnect

from baseweb.web import server

socketio = SocketIO(server)

@socketio.on('connect')
def on_connect():
  logger.info("connect: {0}".format(request.sid))

@socketio.on('disconnect')
def on_disconnect():
  logger.info("disconnect: {0}".format(request.sid))
