import logging
logger = logging.getLogger(__name__)

import os

# register the Vue component for the UI

from baseweb.interface import register_component

register_component("index.js", os.path.dirname(__file__))

from flask import request
from baseweb.socketio import socketio

# log all messages both to logging infrastructure and connected clients

def log(msg):
  logger.info(msg)
  socketio.emit("log", msg)

# set up socketio event handlers to handle events from the UI

@socketio.on("hello")
def on_hello(name):
  log("received hello from {0} ({1}) via socketio".format(name, request.sid))
  return "Hello {0} from socketio!".format(name)

# set up a REST resource to handle requests from the UI

from flask_restful import Resource
from baseweb.rest import api

class Hello(Resource):
  def get(self):
    name = request.args["name"]
    log("received hello from {0} via rest/get".format(name))
    return "Hello {0} from REST/GET".format(name)
    
  def post(self):
    name = request.get_json()["name"]
    log("received hello from {0} via rest/post".format(name))
    return "Hello {0} from REST/POST".format(name)

api.add_resource(Hello, "/api/hello")
