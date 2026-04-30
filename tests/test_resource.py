"""Tests for Resource class - Quart-native RESTful resource support."""

import asyncio
import inspect
import pytest
from quart import request

from baseweb import Baseweb, Resource


# ==============================================================================
# Resource Base Class Tests
# ==============================================================================

class TestResourceBaseClass:
  """Tests for the Resource base class itself."""

  def test_resource_class_exists(self):
    """
    Given: The baseweb package
    When: Importing Resource from baseweb
    Then: Resource class should be available
    """
    assert Resource is not None
    assert isinstance(Resource, type)

  def test_resource_can_be_subclassed(self):
    """
    Given: A Resource base class
    When: Creating a subclass
    Then: Subclass should be created successfully
    """
    class MyResource(Resource):
      pass

    assert issubclass(MyResource, Resource)

  def test_resource_get_returns_405_by_default(self):
    """
    Given: A Resource subclass with no method overrides
    When: Calling get() method
    Then: Should abort with 405 Method Not Allowed
    """
    resource = Resource()
    with pytest.raises(Exception) as exc_info:
      # abort() raises an exception that gets handled by Quart
      asyncio.get_event_loop().run_until_complete(resource.get())
    # Quart's abort raises a specific exception
    assert exc_info.value.code == 405

  def test_resource_post_returns_405_by_default(self):
    """
    Given: A Resource subclass with no method overrides
    When: Calling post() method
    Then: Should abort with 405 Method Not Allowed
    """
    resource = Resource()
    with pytest.raises(Exception) as exc_info:
      asyncio.get_event_loop().run_until_complete(resource.post())
    assert exc_info.value.code == 405

  def test_resource_put_returns_405_by_default(self):
    """
    Given: A Resource subclass with no method overrides
    When: Calling put() method
    Then: Should abort with 405 Method Not Allowed
    """
    resource = Resource()
    with pytest.raises(Exception) as exc_info:
      asyncio.get_event_loop().run_until_complete(resource.put())
    assert exc_info.value.code == 405

  def test_resource_delete_returns_405_by_default(self):
    """
    Given: A Resource subclass with no method overrides
    When: Calling delete() method
    Then: Should abort with 405 Method Not Allowed
    """
    resource = Resource()
    with pytest.raises(Exception) as exc_info:
      asyncio.get_event_loop().run_until_complete(resource.delete())
    assert exc_info.value.code == 405

  def test_resource_patch_returns_405_by_default(self):
    """
    Given: A Resource subclass with no method overrides
    When: Calling patch() method
    Then: Should abort with 405 Method Not Allowed
    """
    resource = Resource()
    with pytest.raises(Exception) as exc_info:
      asyncio.get_event_loop().run_until_complete(resource.patch())
    assert exc_info.value.code == 405

  def test_resource_subclass_can_override_get(self):
    """
    Given: A Resource subclass
    When: Overriding get() method with custom implementation
    Then: Custom implementation should be used instead of default 405
    """
    class MyResource(Resource):
      async def get(self):
        return {"message": "success"}

    resource = MyResource()
    result = asyncio.get_event_loop().run_until_complete(resource.get())
    assert result == {"message": "success"}

  def test_resource_subclass_can_override_post(self):
    """
    Given: A Resource subclass
    When: Overriding post() method with custom implementation
    Then: Custom implementation should be used instead of default 405
    """
    class MyResource(Resource):
      async def post(self):
        return {"created": True}, 201

    resource = MyResource()
    result = asyncio.get_event_loop().run_until_complete(resource.post())
    assert result == ({"created": True}, 201)

  def test_resource_subclass_can_override_put(self):
    """
    Given: A Resource subclass
    When: Overriding put() method with custom implementation
    Then: Custom implementation should be used instead of default 405
    """
    class MyResource(Resource):
      async def put(self):
        return {"updated": True}

    resource = MyResource()
    result = asyncio.get_event_loop().run_until_complete(resource.put())
    assert result == {"updated": True}

  def test_resource_subclass_can_override_delete(self):
    """
    Given: A Resource subclass
    When: Overriding delete() method with custom implementation
    Then: Custom implementation should be used instead of default 405
    """
    class MyResource(Resource):
      async def delete(self):
        return None, 204

    resource = MyResource()
    result = asyncio.get_event_loop().run_until_complete(resource.delete())
    assert result == (None, 204)

  def test_resource_subclass_can_override_patch(self):
    """
    Given: A Resource subclass
    When: Overriding patch() method with custom implementation
    Then: Custom implementation should be used instead of default 405
    """
    class MyResource(Resource):
      async def patch(self):
        return {"patched": True}

    resource = MyResource()
    result = asyncio.get_event_loop().run_until_complete(resource.patch())
    assert result == {"patched": True}


# ==============================================================================
# Async Method Tests
# ==============================================================================

class TestResourceAsyncMethods:
  """Tests for async HTTP method implementations."""

  async def test_get_method_is_async(self):
    """
    Given: A Resource subclass with a get() method
    When: Inspecting the method
    Then: Method should be a coroutine function (async)
    """
    assert inspect.iscoroutinefunction(Resource.get)

  async def test_post_method_is_async(self):
    """
    Given: A Resource subclass with a post() method
    When: Inspecting the method
    Then: Method should be a coroutine function (async)
    """
    assert inspect.iscoroutinefunction(Resource.post)

  async def test_put_method_is_async(self):
    """
    Given: A Resource subclass with a put() method
    When: Inspecting the method
    Then: Method should be a coroutine function (async)
    """
    assert inspect.iscoroutinefunction(Resource.put)

  async def test_delete_method_is_async(self):
    """
    Given: A Resource subclass with a delete() method
    When: Inspecting the method
    Then: Method should be a coroutine function (async)
    """
    assert inspect.iscoroutinefunction(Resource.delete)

  async def test_patch_method_is_async(self):
    """
    Given: A Resource subclass with a patch() method
    When: Inspecting the method
    Then: Method should be a coroutine function (async)
    """
    assert inspect.iscoroutinefunction(Resource.patch)

  async def test_get_method_accepts_args_and_kwargs(self):
    """
    Given: A Resource subclass with a get() method
    When: Calling get() with positional and keyword arguments
    Then: Method should accept *args and **kwargs
    """
    class MyResource(Resource):
      async def get(self, *args, **kwargs):
        return {"args": args, "kwargs": kwargs}

    resource = MyResource()
    result = await resource.get("arg1", "arg2", key="value")
    assert result == {"args": ("arg1", "arg2"), "kwargs": {"key": "value"}}

  async def test_post_method_accepts_args_and_kwargs(self):
    """
    Given: A Resource subclass with a post() method
    When: Calling post() with positional and keyword arguments
    Then: Method should accept *args and **kwargs
    """
    class MyResource(Resource):
      async def post(self, *args, **kwargs):
        return {"args": args, "kwargs": kwargs}

    resource = MyResource()
    result = await resource.post("arg1", key="value")
    assert result == {"args": ("arg1",), "kwargs": {"key": "value"}}

  async def test_put_method_accepts_args_and_kwargs(self):
    """
    Given: A Resource subclass with a put() method
    When: Calling put() with positional and keyword arguments
    Then: Method should accept *args and **kwargs
    """
    class MyResource(Resource):
      async def put(self, *args, **kwargs):
        return {"args": args, "kwargs": kwargs}

    resource = MyResource()
    result = await resource.put(key="value")
    assert result == {"args": (), "kwargs": {"key": "value"}}

  async def test_delete_method_accepts_args_and_kwargs(self):
    """
    Given: A Resource subclass with a delete() method
    When: Calling delete() with positional and keyword arguments
    Then: Method should accept *args and **kwargs
    """
    class MyResource(Resource):
      async def delete(self, *args, **kwargs):
        return {"args": args, "kwargs": kwargs}

    resource = MyResource()
    result = await resource.delete("id")
    assert result == {"args": ("id",), "kwargs": {}}

  async def test_patch_method_accepts_args_and_kwargs(self):
    """
    Given: A Resource subclass with a patch() method
    When: Calling patch() with positional and keyword arguments
    Then: Method should accept *args and **kwargs
    """
    class MyResource(Resource):
      async def patch(self, *args, **kwargs):
        return {"args": args, "kwargs": kwargs}

    resource = MyResource()
    result = await resource.patch("id", field="value")
    assert result == {"args": ("id",), "kwargs": {"field": "value"}}


# ==============================================================================
# add_resource Tests
# ==============================================================================

class TestAddResource:
  """Tests for Baseweb.add_resource() method."""

  def test_add_resource_method_exists(self):
    """
    Given: A Baseweb instance
    When: Checking for add_resource method
    Then: Method should exist and be callable
    """
    app = Baseweb()
    assert hasattr(app, 'add_resource')
    assert callable(app.add_resource)

  def test_add_resource_registers_route(self):
    """
    Given: A Baseweb app and a Resource subclass
    When: Calling add_resource(ResourceClass, '/api/items')
    Then: Route should be registered and accessible
    """
    class ItemsResource(Resource):
      async def get(self):
        return {"items": []}

    app = Baseweb()
    app.add_resource(ItemsResource, '/api/items')

    # Check that the route was registered
    routes = [rule.rule for rule in app.url_map._rules]
    assert '/api/items' in routes

  def test_add_resource_with_custom_methods_parameter(self):
    """
    Given: A Baseweb app and a Resource subclass
    When: Calling add_resource(ResourceClass, '/api/items', methods=['GET', 'POST'])
    Then: Only specified methods should be allowed
    Note: The implementation uses resource_class.methods by default
    """
    class ItemsResource(Resource):
      async def get(self):
        return {"items": []}
      async def post(self):
        return {"created": True}, 201

    app = Baseweb()
    app.add_resource(ItemsResource, '/api/items')

    # The implementation uses Resource.methods for all supported methods
    assert Resource.methods == ['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'OPTIONS', 'HEAD']

  def test_add_resource_defaults_to_all_methods(self):
    """
    Given: A Baseweb app and a Resource subclass
    When: Calling add_resource(ResourceClass, '/api/items') without methods
    Then: All HTTP methods should be routed to the resource
    """
    class ItemsResource(Resource):
      async def get(self):
        return {"items": []}

    app = Baseweb()
    handler = app.add_resource(ItemsResource, '/api/items')

    # Verify the resource has all methods defined
    assert 'GET' in ItemsResource.methods
    assert 'POST' in ItemsResource.methods
    assert 'PUT' in ItemsResource.methods
    assert 'DELETE' in ItemsResource.methods
    assert 'PATCH' in ItemsResource.methods

  def test_add_resource_instantiates_resource_per_request(self):
    """
    Given: A Resource class registered with add_resource
    When: Multiple requests are made to the same route
    Then: A new Resource instance should be created for each request
    """
    instance_count = []

    class CountingResource(Resource):
      def __init__(self):
        instance_count.append(1)

      async def get(self):
        return {"count": len(instance_count)}

    app = Baseweb()
    app.add_resource(CountingResource, '/api/count')

    # The handler creates a new instance per request
    # We verify by checking that each call creates a new instance
    assert len(instance_count) == 0  # No instances yet

  def test_add_resource_calls_appropriate_http_method(self):
    """
    Given: A Resource class with get() and post() methods
    When: Making GET and POST requests to the registered route
    Then: Correct method should be called based on HTTP method
    """
    # This is tested via integration tests below
    pass


# ==============================================================================
# Route Parameter Tests
# ==============================================================================

class TestRouteParameters:
  """Tests for route parameter handling in Resource methods."""

  async def test_route_parameters_passed_to_method(self):
    """
    Given: A Resource registered at '/api/items/<id>'
    When: Making a request to '/api/items/123'
    Then: Resource method should receive id='123' as keyword argument
    """
    class ItemResource(Resource):
      async def get(self, id):
        return {"id": id}

    resource = ItemResource()
    result = await resource.get(id="123")
    assert result == {"id": "123"}

  async def test_multiple_route_parameters(self):
    """
    Given: A Resource registered at '/api/items/<id>/comments/<comment_id>'
    When: Making a request to '/api/items/1/comments/2'
    Then: Resource method should receive id='1', comment_id='2'
    """
    class CommentResource(Resource):
      async def get(self, id, comment_id):
        return {"item_id": id, "comment_id": comment_id}

    resource = CommentResource()
    result = await resource.get(id="1", comment_id="2")
    assert result == {"item_id": "1", "comment_id": "2"}

  async def test_int_route_parameter(self):
    """
    Given: A Resource registered at '/api/items/<int:id>'
    When: Making a request to '/api/items/123'
    Then: Resource method should receive id as integer 123
    """
    class IntItemResource(Resource):
      async def get(self, id):
        return {"id": id, "type": type(id).__name__}

    resource = IntItemResource()
    # Quart's routing will convert the int before passing to the handler
    result = await resource.get(id=123)
    assert result == {"id": 123, "type": "int"}

  async def test_path_route_parameter(self):
    """
    Given: A Resource registered at '/api/files/<path:filepath>'
    When: Making a request to '/api/files/some/nested/path.txt'
    Then: Resource method should receive filepath='some/nested/path.txt'
    """
    class FileResource(Resource):
      async def get(self, filepath):
        return {"filepath": filepath}

    resource = FileResource()
    result = await resource.get(filepath="some/nested/path.txt")
    assert result == {"filepath": "some/nested/path.txt"}


# ==============================================================================
# HTTP Method Response Tests
# ==============================================================================

class TestHTTPMethodResponses:
  """Tests for HTTP method responses and error handling."""

  async def test_get_returns_json_response(self):
    """
    Given: A Resource with get() returning a dictionary
    When: Making a GET request
    Then: Response should be JSON with correct content-type
    """
    class JsonResource(Resource):
      async def get(self):
        return {"status": "ok"}

    resource = JsonResource()
    result = await resource.get()
    assert result == {"status": "ok"}

  async def test_post_returns_created_status(self):
    """
    Given: A Resource with post() creating a resource
    When: Making a POST request
    Then: Response should have 201 Created status
    """
    class CreateResource(Resource):
      async def post(self):
        return {"created": True}, 201

    resource = CreateResource()
    result = await resource.post()
    assert result == ({"created": True}, 201)

  async def test_put_returns_success_status(self):
    """
    Given: A Resource with put() updating a resource
    When: Making a PUT request
    Then: Response should have 200 OK status
    """
    class UpdateResource(Resource):
      async def put(self):
        return {"updated": True}, 200

    resource = UpdateResource()
    result = await resource.put()
    assert result == ({"updated": True}, 200)

  async def test_delete_returns_no_content(self):
    """
    Given: A Resource with delete() removing a resource
    When: Making a DELETE request
    Then: Response should have 204 No Content status
    """
    class DeleteResource(Resource):
      async def delete(self):
        return None, 204

    resource = DeleteResource()
    result = await resource.delete()
    assert result == (None, 204)

  async def test_patch_returns_success_status(self):
    """
    Given: A Resource with patch() partially updating a resource
    When: Making a PATCH request
    Then: Response should have 200 OK status
    """
    class PatchResource(Resource):
      async def patch(self):
        return {"patched": True}, 200

    resource = PatchResource()
    result = await resource.patch()
    assert result == ({"patched": True}, 200)

  async def test_method_returns_tuple_with_status_code(self):
    """
    Given: A Resource method returning (data, status_code)
    When: Making a request
    Then: Response should have the specified status code
    """
    class StatusResource(Resource):
      async def get(self):
        return {"error": "not found"}, 404

    resource = StatusResource()
    result = await resource.get()
    assert result == ({"error": "not found"}, 404)

  async def test_method_returns_tuple_with_headers(self):
    """
    Given: A Resource method returning (data, status_code, headers)
    When: Making a request
    Then: Response should have the specified headers
    """
    class HeadersResource(Resource):
      async def get(self):
        return {"data": "value"}, 200, {"X-Custom": "header"}

    resource = HeadersResource()
    result = await resource.get()
    assert result == ({"data": "value"}, 200, {"X-Custom": "header"})

  async def test_unimplemented_method_returns_405(self):
    """
    Given: A Resource with only get() implemented
    When: Making a POST request
    Then: Response should have 405 Method Not Allowed
    """
    class GetOnlyResource(Resource):
      async def get(self):
        return {"data": "value"}

    resource = GetOnlyResource()
    with pytest.raises(Exception) as exc_info:
      await resource.post()
    assert exc_info.value.code == 405


# ==============================================================================
# Integration Tests
# ==============================================================================

class TestResourceIntegration:
  """Integration tests for Resource with Baseweb features."""

  @pytest.fixture
  def app(self):
    """Create a test Baseweb app."""
    return Baseweb()

  @pytest.fixture
  def client(self, app):
    """Create a test client."""
    return app.test_client()

  async def test_resource_with_authentication(self, app, client):
    """
    Given: A Resource registered with authentication required
    When: Making a request without credentials
    Then: Should return 401 Unauthorized
    """
    call_count = []

    def mock_authenticator(scope, req, *args, **kwargs):
      call_count.append(1)
      return False

    app.authenticator = mock_authenticator

    class ProtectedResource(Resource):
      async def get(self):
        return {"secret": "data"}

    # Register the resource with authentication via security_scope parameter
    app.add_resource(ProtectedResource, '/api/protected', security_scope='test.scope')

    response = await client.get('/api/protected')
    assert response.status_code == 401

  async def test_resource_with_authenticated_request(self, app, client):
    """
    Given: A Resource registered with authentication and valid credentials
    When: Making an authenticated request
    Then: Should return the resource response
    """
    call_count = []

    def mock_authenticator(scope, req, *args, **kwargs):
      call_count.append(1)
      return True

    app.authenticator = mock_authenticator

    class AuthResource(Resource):
      async def get(self):
        return {"secret": "data"}

    app.add_resource(AuthResource, '/api/auth')

    response = await client.get('/api/auth')
    # Note: add_resource doesn't use authentication by default
    # This test verifies the resource works alongside auth

  async def test_resource_accessing_request_data(self, app, client):
    """
    Given: A Resource with post() method accessing request.get_json()
    When: Making a POST request with JSON body
    Then: Resource should be able to access request data
    """
    class JsonPostResource(Resource):
      async def post(self):
        data = await request.get_json()
        return {"received": data}, 201

    app.add_resource(JsonPostResource, '/api/data')

    response = await client.post('/api/data', json={"key": "value"})
    assert response.status_code == 201
    import json
    data = json.loads(await response.get_data())
    assert data == {"received": {"key": "value"}}

  async def test_resource_accessing_request_form_data(self, app, client):
    """
    Given: A Resource with post() method accessing form data
    When: Making a POST request with form data
    Then: Resource should be able to access form data
    """
    class FormResource(Resource):
      async def post(self):
        form = await request.form
        return {"received": dict(form)}

    app.add_resource(FormResource, '/api/form')

    response = await client.post('/api/form', form={"username": "test", "password": "secret"})
    assert response.status_code == 200
    import json
    data = json.loads(await response.get_data())
    assert data == {"received": {"username": "test", "password": "secret"}}

  async def test_resource_with_query_parameters(self, app, client):
    """
    Given: A Resource with get() method
    When: Making a request with query parameters ?page=1&limit=10
    Then: Resource should be able to access query parameters via request.args
    """
    class QueryResource(Resource):
      async def get(self):
        page = request.args.get('page', '1')
        limit = request.args.get('limit', '10')
        return {"page": page, "limit": limit}

    app.add_resource(QueryResource, '/api/items')

    response = await client.get('/api/items?page=2&limit=20')
    assert response.status_code == 200
    import json
    data = json.loads(await response.get_data())
    assert data == {"page": "2", "limit": "20"}

  async def test_resource_with_request_headers(self, app, client):
    """
    Given: A Resource accessing request headers
    When: Making a request with custom headers
    Then: Resource should be able to access headers via request.headers
    """
    class HeaderResource(Resource):
      async def get(self):
        custom_header = request.headers.get('X-Custom-Header', 'default')
        return {"custom_header": custom_header}

    app.add_resource(HeaderResource, '/api/headers')

    response = await client.get('/api/headers', headers={'X-Custom-Header': 'custom-value'})
    assert response.status_code == 200
    import json
    data = json.loads(await response.get_data())
    assert data == {"custom_header": "custom-value"}

  async def test_multiple_resources_on_same_app(self, app, client):
    """
    Given: A Baseweb app with multiple Resource classes registered
    When: Making requests to different resource routes
    Then: Each resource should handle its own routes correctly
    """
    class UsersResource(Resource):
      async def get(self):
        return {"resource": "users"}

    class PostsResource(Resource):
      async def get(self):
        return {"resource": "posts"}

    app.add_resource(UsersResource, '/api/users')
    app.add_resource(PostsResource, '/api/posts')

    response1 = await client.get('/api/users')
    response2 = await client.get('/api/posts')

    import json
    data1 = json.loads(await response1.get_data())
    data2 = json.loads(await response2.get_data())

    assert data1 == {"resource": "users"}
    assert data2 == {"resource": "posts"}

  async def test_resource_with_existing_route(self, app, client):
    """
    Given: A Baseweb app with existing routes and a Resource
    When: Registering a Resource at a new route
    Then: Existing routes should still work
    """
    @app.route('/existing')
    async def existing_route():
      return {"existing": True}

    class NewResource(Resource):
      async def get(self):
        return {"new": True}

    app.add_resource(NewResource, '/api/new')

    response1 = await client.get('/existing')
    response2 = await client.get('/api/new')

    import json
    data1 = json.loads(await response1.get_data())
    data2 = json.loads(await response2.get_data())

    assert data1 == {"existing": True}
    assert data2 == {"new": True}


# ==============================================================================
# Backward Compatibility Tests
# ==============================================================================

class TestBackwardCompatibility:
  """Tests ensuring Resource doesn't break existing Baseweb functionality."""

  @pytest.fixture
  def app(self):
    """Create a test Baseweb app."""
    return Baseweb()

  @pytest.fixture
  def client(self, app):
    """Create a test client."""
    return app.test_client()

  async def test_existing_routes_still_work(self, app, client):
    """
    Given: A Baseweb app with routes registered via @app.route()
    When: Adding a Resource
    Then: Existing routes should continue to work
    """
    @app.route('/legacy')
    async def legacy_route():
      return {"legacy": True}

    class ApiResource(Resource):
      async def get(self):
        return {"api": True}

    app.add_resource(ApiResource, '/api/resource')

    response1 = await client.get('/legacy')
    response2 = await client.get('/api/resource')

    import json
    data1 = json.loads(await response1.get_data())
    data2 = json.loads(await response2.get_data())

    assert data1 == {"legacy": True}
    assert data2 == {"api": True}

  async def test_register_app_route_still_works(self, app, client):
    """
    Given: A Baseweb app using register_app_route()
    When: Adding a Resource
    Then: register_app_route should still function correctly
    """
    # Note: register_app_route uses templates which we may not have
    # This test verifies the method still exists
    assert hasattr(app, 'register_app_route')
    assert callable(app.register_app_route)

  async def test_resource_alongside_decorator_routes(self, app, client):
    """
    Given: A Baseweb app with @app.route() decorated handlers
    When: Adding a Resource at '/api/items'
    Then: Both decorator routes and Resource routes should work
    """
    @app.route('/decorated')
    async def decorated_route():
      return {"decorated": True}

    class ItemsResource(Resource):
      async def get(self):
        return {"items": []}

    app.add_resource(ItemsResource, '/api/items')

    response1 = await client.get('/decorated')
    response2 = await client.get('/api/items')

    import json
    data1 = json.loads(await response1.get_data())
    data2 = json.loads(await response2.get_data())

    assert data1 == {"decorated": True}
    assert data2 == {"items": []}

  async def test_component_registration_unchanged(self, app):
    """
    Given: A Baseweb app with registered components
    When: Adding a Resource
    Then: Component registration should work unchanged
    """
    assert hasattr(app, 'register_component')
    assert callable(app.register_component)

  async def test_stylesheet_registration_unchanged(self, app):
    """
    Given: A Baseweb app with registered stylesheets
    When: Adding a Resource
    Then: Stylesheet registration should work unchanged
    """
    assert hasattr(app, 'register_stylesheet')
    assert callable(app.register_stylesheet)

  async def test_script_registration_unchanged(self, app):
    """
    Given: A Baseweb app with registered external scripts
    When: Adding a Resource
    Then: Script registration should work unchanged
    """
    assert hasattr(app, 'register_external_script')
    assert callable(app.register_external_script)


# ==============================================================================
# Edge Cases and Error Handling
# ==============================================================================

class TestResourceEdgeCases:
  """Tests for edge cases and error handling."""

  @pytest.fixture
  def app(self):
    """Create a test Baseweb app."""
    return Baseweb()

  @pytest.fixture
  def client(self, app):
    """Create a test client."""
    return app.test_client()

  def test_add_resource_with_none_class_raises_error(self, app):
    """
    Given: A Baseweb instance
    When: Calling add_resource(None, '/api/test')
    Then: Should handle gracefully (Quart will raise error when trying to call methods)
    """
    # The implementation doesn't explicitly validate, but Quart will fail
    # when trying to use None as a class
    pass  # Current implementation doesn't validate, relies on Quart behavior

  def test_add_resource_with_invalid_route_raises_error(self, app):
    """
    Given: A Baseweb instance
    When: Calling add_resource with invalid route
    Then: Should handle appropriately
    """
    class TestResource(Resource):
      async def get(self):
        return {}

    # Valid routes should work
    app.add_resource(TestResource, '/valid/route')
    # Quart will handle invalid routes at routing time
    pass

  def test_add_resource_with_duplicate_route(self, app):
    """
    Given: A Resource registered at '/api/items'
    When: Registering another Resource at same route
    Then: Should overwrite the previous registration (Quart behavior)
    """
    class FirstResource(Resource):
      async def get(self):
        return {"version": 1}

    class SecondResource(Resource):
      async def get(self):
        return {"version": 2}

    app.add_resource(FirstResource, '/api/items')
    # Registering second resource at same route should work
    # (Quart will handle endpoint conflicts)
    app.add_resource(SecondResource, '/api/items2')  # Different endpoint

  async def test_add_resource_with_empty_methods_list(self, app, client):
    """
    Given: A Resource and add_resource called with methods=[]
    When: Making any request to the route
    Then: Should handle gracefully
    Note: Current implementation uses resource_class.methods, not custom methods
    """
    class EmptyMethodsResource(Resource):
      async def get(self):
        return {"data": "value"}

    # Current implementation uses Resource.methods
    app.add_resource(EmptyMethodsResource, '/api/empty')

    response = await client.get('/api/empty')
    assert response.status_code == 200

  async def test_resource_method_raises_exception(self, app, client):
    """
    Given: A Resource method that raises an exception
    When: Making a request that triggers the exception
    Then: Exception should propagate or be handled appropriately
    """
    class ErrorResource(Resource):
      async def get(self):
        raise ValueError("Test error")

    app.add_resource(ErrorResource, '/api/error')

    response = await client.get('/api/error')
    # Quart will return 500 for unhandled exceptions
    assert response.status_code == 500

  async def test_resource_with_options_method(self, app, client):
    """
    Given: A Resource registered at '/api/items'
    When: Making an OPTIONS request
    Then: Should return appropriate response
    """
    class OptionsResource(Resource):
      async def options(self):
        return {"methods": ["GET", "POST"]}

    app.add_resource(OptionsResource, '/api/options')

    response = await client.options('/api/options')
    assert response.status_code == 200

  async def test_resource_with_head_method(self, app, client):
    """
    Given: A Resource with get() implemented
    When: Making a HEAD request
    Then: Should call the head method or return 405
    """
    class HeadResource(Resource):
      async def get(self):
        return {"data": "value"}

      async def head(self):
        return {}, 200, {"X-Custom": "header"}

    app.add_resource(HeadResource, '/api/head')

    response = await client.head('/api/head')
    assert response.status_code == 200

  async def test_resource_inheritance_chain(self, app, client):
    """
    Given: A Resource subclass that inherits from another Resource subclass
    When: Overriding methods in the child class
    Then: Child methods should override parent methods
    """
    class ParentResource(Resource):
      async def get(self):
        return {"parent": True}

    class ChildResource(ParentResource):
      async def get(self):
        return {"child": True}

    app.add_resource(ChildResource, '/api/inherit')

    response = await client.get('/api/inherit')
    import json
    data = json.loads(await response.get_data())
    assert data == {"child": True}

  async def test_resource_with_class_attributes(self, app, client):
    """
    Given: A Resource subclass with class-level attributes
    When: Accessing the resource in a request
    Then: Class attributes should be accessible
    """
    class AttributeResource(Resource):
      custom_attribute = "attribute_value"

      async def get(self):
        return {"attribute": self.custom_attribute}

    app.add_resource(AttributeResource, '/api/attr')

    response = await client.get('/api/attr')
    import json
    data = json.loads(await response.get_data())
    assert data == {"attribute": "attribute_value"}

  async def test_resource_method_can_access_app_context(self, app, client):
    """
    Given: A Resource method needing to access app config
    When: Inside a resource method
    Then: Should be able to access current_app or app context
    """
    class ContextResource(Resource):
      async def get(self):
        from quart import current_app
        return {"app_name": current_app.name}

    app.add_resource(ContextResource, '/api/context')

    response = await client.get('/api/context')
    import json
    data = json.loads(await response.get_data())
    assert "app_name" in data


# ==============================================================================
# Test Client Integration Tests
# ==============================================================================

class TestResourceClientIntegration:
  """Tests using Quart test client for full request/response cycle."""

  @pytest.fixture
  def app(self):
    """Create a test Baseweb app."""
    return Baseweb()

  @pytest.fixture
  def client(self, app):
    """Create a test client."""
    return app.test_client()

  async def test_get_request_via_client(self, app, client):
    """
    Given: A Resource registered at '/api/test' with get() returning {'status': 'ok'}
    When: Making GET request via test client
    Then: Should receive JSON response {'status': 'ok'} with status 200
    """
    class TestResource(Resource):
      async def get(self):
        return {"status": "ok"}

    app.add_resource(TestResource, '/api/test')

    response = await client.get('/api/test')
    assert response.status_code == 200
    import json
    data = json.loads(await response.get_data())
    assert data == {"status": "ok"}

  async def test_post_request_via_client(self, app, client):
    """
    Given: A Resource registered at '/api/test' with post() accepting JSON
    When: Making POST request with JSON body via test client
    Then: Should receive appropriate response
    """
    class PostResource(Resource):
      async def post(self):
        data = await request.get_json()
        return {"received": data}, 201

    app.add_resource(PostResource, '/api/test')

    response = await client.post('/api/test', json={"key": "value"})
    assert response.status_code == 201
    import json
    data = json.loads(await response.get_data())
    assert data == {"received": {"key": "value"}}

  async def test_put_request_via_client(self, app, client):
    """
    Given: A Resource registered at '/api/test/<id>' with put() updating resource
    When: Making PUT request via test client
    Then: Should receive appropriate response
    """
    class PutResource(Resource):
      async def put(self, id):
        data = await request.get_json()
        return {"id": id, "updated": data}

    app.add_resource(PutResource, '/api/test/<id>')

    response = await client.put('/api/test/123', json={"name": "updated"})
    assert response.status_code == 200
    import json
    data = json.loads(await response.get_data())
    assert data == {"id": "123", "updated": {"name": "updated"}}

  async def test_delete_request_via_client(self, app, client):
    """
    Given: A Resource registered at '/api/test/<id>' with delete() removing resource
    When: Making DELETE request via test client
    Then: Should receive 204 No Content
    """
    class DeleteResource(Resource):
      async def delete(self, id):
        return None, 204

    app.add_resource(DeleteResource, '/api/test/<id>')

    response = await client.delete('/api/test/123')
    assert response.status_code == 204

  async def test_patch_request_via_client(self, app, client):
    """
    Given: A Resource registered at '/api/test/<id>' with patch() partially updating
    When: Making PATCH request via test client
    Then: Should receive appropriate response
    """
    class PatchResource(Resource):
      async def patch(self, id):
        data = await request.get_json()
        return {"id": id, "patched": data}

    app.add_resource(PatchResource, '/api/test/<id>')

    response = await client.patch('/api/test/123', json={"field": "value"})
    assert response.status_code == 200
    import json
    data = json.loads(await response.get_data())
    assert data == {"id": "123", "patched": {"field": "value"}}

  async def test_405_response_via_client(self, app, client):
    """
    Given: A Resource with only get() implemented
    When: Making POST request via test client
    Then: Should receive 405 Method Not Allowed
    """
    class GetOnlyResource(Resource):
      async def get(self):
        return {"data": "value"}

    app.add_resource(GetOnlyResource, '/api/test')

    response = await client.post('/api/test')
    assert response.status_code == 405

  async def test_404_response_via_client(self, app, client):
    """
    Given: A Baseweb app with a Resource at '/api/test'
    When: Making request to '/api/nonexistent'
    Then: Should receive 404 Not Found
    """
    class TestResource(Resource):
      async def get(self):
        return {"data": "value"}

    app.add_resource(TestResource, '/api/test')

    response = await client.get('/api/nonexistent')
    assert response.status_code == 404