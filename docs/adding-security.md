# Adding Security

To setup a layer of access security, baseweb allows to register an authenticator function:

```python
from baseweb.security import add_authenticator

def authenticator(scope, request, *args, **kwargs):
  logger.debug("AUTH: scope:{} / request:{} / args:{} / kwargs:{}".format(
    scope, str(request), str(args), str(kwargs)
  ))
  return True

add_authenticator(authenticator)
```

After adding this to you initialization code, every request to the user interface part of baseweb will be validated using this function. In this example (taken from the demo app) all requests are logged. From such a log, we can see what the arguments are that are passed to our authenticator function:

```bash
AUTH: scope:ui.section / request:<Request 'http://localhost:8000/page2' [GET]> / args:() / kwargs:{'section': 'page2'}
AUTH: scope:ui.static.store.js / request:<Request 'http://localhost:8000/static/js/store.js' [GET]> / args:() / kwargs:{}
AUTH: scope:ui.static.store.js / request:<Request 'http://localhost:8000/static/js/store.js' [GET]> / args:() / kwargs:{}
AUTH: scope:ui.app.filename / request:<Request 'http://localhost:8000/app/page2.js' [GET]> / args:() / kwargs:{'filename': 'page2.js'}
AUTH: scope:ui.app.filename / request:<Request 'http://localhost:8000/app/page1.js' [GET]> / args:() / kwargs:{'filename': 'page1.js'}
AUTH: scope:ui.app.filename / request:<Request 'http://localhost:8000/app/index.js' [GET]> / args:() / kwargs:{'filename': 'index.js'}
```

The `scope` argument indicates where the request was handled. In this case all requests were handles by the `ui` component. Possible sub-levels are `section`, `static` and `app`, indicating that the request was targetting a section, some static content or content provided by your own application, e.g. those registered using `register_component`.

The `request` argument is the standard Flask `request` object, which, amongst others contains the `authorization` object, that provides a `username` and `password`. Through the `request` argument, all aspects of the request can be taken into account, even the arguments and or posted data, allowing event for even deeper content/data based access, e.g. in case of resources...

## Securing Resources and IO

You can use the same mechanism to add security to your own resources and IO:

```python
from baseweb.security import authenticated

class Hello(Resource):
  @authenticated("app.hello.get")
  def get(self):
    name = request.args["name"]
    log("received hello from {0} via rest/get".format(name))
    return "Hello {0} from REST/GET".format(name)
    
  @authenticated("app.hello.post")
  def post(self):
    name = request.get_json()["name"]
    log("received hello from {0} via rest/post".format(name))
    return "Hello {0} from REST/POST".format(name)
```

By applying the `baseweb.security.authenticated` decorator methods on resources can be secured in exactly the same way as their ui counterparts.

This example also comes from the demo app, so when issuing a get or post request our authenticator function is also called, now with the called instance of our resource:

```bash
AUTH: scope:app.hello.get / request:<Request 'http://localhost:8000/api/hello?name=Christophe' [GET]> / args:(<demo.pages.index.Hello object at 0x10cb10ef0>,) / kwargs:{}
AUTH: scope:app.hello.post / request:<Request 'http://localhost:8000/api/hello' [POST]> / args:(<demo.pages.index.Hello object at 0x10cb10e48>,) / kwargs:{}
```

The scope is provided by means of the single argument to the decorator. There is no mandatory/intended logic implemented, so you can apply any scheme you like.

Finally, also all socket IO requests can be validated, as indicated by these log messages when connecting, handling an incoming event and disconnecting:

```bash
AUTH: scope:io.connect / request:<Request 'http://localhost:8000/socket.io/?EIO=3&transport=polling&t=NC4bkaz' [GET]> / args:() / kwargs:{}
AUTH: scope:app.io.hello / request:<Request 'http://localhost:8000/socket.io/?EIO=3&transport=polling&t=NC4byT2' [GET]> / args:('Christophe',) / kwargs:{}
AUTH: scope:io.disconnect / request:<Request 'http://localhost:8000/socket.io/?EIO=3&transport=polling&t=NC4bkaz' [GET]> / args:() / kwargs:{}
```

Instrumenting our own socket IO event handlers happens in exactly the same way as our resources:

```python
from baseweb.security import authenticated

@socketio.on("hello")
@authenticated("app.io.hello")
def on_hello(name):
  log("received hello from {0} ({1}) via socketio".format(name, request.sid))
  return "Hello {0} from socketio!".format(name)
```

