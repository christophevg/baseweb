"""Resource base class for RESTful APIs with async support."""

from quart import abort


class Resource:
  """
  Base class for RESTful resources with async support.

  Subclass this and implement async methods for each HTTP verb:
  - get(self, *args, **kwargs)
  - post(self, *args, **kwargs)
  - put(self, *args, **kwargs)
  - delete(self, *args, **kwargs)
  - patch(self, *args, **kwargs)
  - options(self, *args, **kwargs)
  - head(self, *args, **kwargs)

  Methods not implemented return 405 Method Not Allowed.

  Example:
      class UserResource(Resource):
          async def get(self, user_id):
              return {"user": user_id}

          async def post(self):
              data = await request.get_json()
              return {"created": data}, 201

      server.add_resource(UserResource, '/users/<int:user_id>')
  """

  methods = ['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'OPTIONS', 'HEAD']

  async def get(self, *args, **kwargs):
    """Handle GET requests. Override in subclass to implement."""
    abort(405)

  async def post(self, *args, **kwargs):
    """Handle POST requests. Override in subclass to implement."""
    abort(405)

  async def put(self, *args, **kwargs):
    """Handle PUT requests. Override in subclass to implement."""
    abort(405)

  async def delete(self, *args, **kwargs):
    """Handle DELETE requests. Override in subclass to implement."""
    abort(405)

  async def patch(self, *args, **kwargs):
    """Handle PATCH requests. Override in subclass to implement."""
    abort(405)

  async def options(self, *args, **kwargs):
    """Handle OPTIONS requests. Override in subclass to implement."""
    abort(405)

  async def head(self, *args, **kwargs):
    """Handle HEAD requests. Override in subclass to implement."""
    abort(405)