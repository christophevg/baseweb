# Adding Security

To setup a layer of access security, baseweb allows to register an authenticator function:

```python
from baseweb import server

def authenticator(scope, request, *args, **kwargs):
  logger.debug(f"AUTH: scope:{scope} / request:{request} / args:{args} / kwargs:{kwargs}")
  return True

server.authenticator = authenticator
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

The `scope` argument indicates where the request was handled. In this case all requests were handled by the `ui` component. Possible sub-levels are `section`, `static` and `app`, indicating that the request was targeting a section, some static content or content provided by your own application, e.g. those registered using `register_component`.

The `request` argument is the standard Quart `request` object, which, amongst others contains the `authorization` object, that provides a `username` and `password`. Through the `request` argument, all aspects of the request can be taken into account, even the arguments and or posted data, allowing even for deeper content/data based access, e.g. in case of resources...

## Securing Resources and IO

You can use the same mechanism to add security to your own resources and IO:

```python
from baseweb import server, Resource
from quart import request

class Hello(Resource):
  @server.authenticated("app.hello.get")
  async def get(self):
    name = request.args["name"]
    await log(f"received hello from {name} via rest/get")
    return f"Hello {name} from REST/GET"

  @server.authenticated("app.hello.post")
  async def post(self):
    data = await request.get_json()
    name = data["name"]
    await log(f"received hello from {name} via rest/post")
    return {"message": f"Hello {name} from REST/POST"}
```

By applying the `server.authenticated` decorator methods on resources can be secured in exactly the same way as their ui counterparts.

This example also comes from the demo app, so when issuing a get or post request our authenticator function is also called, now with the called instance of our resource:

```bash
AUTH: scope:app.hello.get / request:<Request 'http://localhost:8000/api/hello?name=Christophe' [GET]> / args:(<demo.pages.index.Hello object at 0x10cb10ef0>,) / kwargs:{}
AUTH: scope:app.hello.post / request:<Request 'http://localhost:8000/api/hello' [POST]> / args:(<demo.pages.index.Hello object at 0x10cb10e48>,) / kwargs:{}
```

The scope is provided by means of the single argument to the decorator. There is no mandatory/intended logic implemented, so you can apply any scheme you like.

## Securing Socket.IO

Socket.IO handlers can also be secured. Note that Socket.IO handlers receive `sid` (session ID) as the first parameter instead of having access to `request`:

```python
from baseweb import server

@server.socketio.on("hello")
@server.authenticated("app.io.hello")
async def on_hello(sid, name):
  await log(f"received hello from {name} ({sid}) via socketio")
  return f"Hello {name} from socketio!"
```

The authenticator function is called with the same parameters for both HTTP and Socket.IO contexts. The `authenticated` decorator automatically detects which context it's running in and uses the appropriate authentication method.

