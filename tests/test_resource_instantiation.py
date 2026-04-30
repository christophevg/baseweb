"""Tests for Resource instantiation patterns.

These tests verify that add_resource accepts both classes and instances.
"""

import pytest

from baseweb import Baseweb, Resource


class TestResourceInstantiation:
  """Tests for Resource class vs instance registration."""

  @pytest.fixture
  def app(self):
    """Create a test Baseweb app."""
    return Baseweb(__name__)

  def test_add_resource_accepts_class(self, app):
    """
    Given: A Resource subclass
    When: Passing to add_resource
    Then: Should be instantiated on each request
    """
    class CounterResource(Resource):
      count = 0

      async def get(self):
        CounterResource.count += 1
        return {"count": CounterResource.count}

    app.add_resource(CounterResource, '/counter')
    assert '/counter' in [r.rule for r in app.url_map.iter_rules()]

  def test_add_resource_accepts_instance(self, app):
    """
    Given: A Resource instance
    When: Passing to add_resource
    Then: Should be reused across requests
    """
    class CounterResource(Resource):
      def __init__(self):
        self.count = 0

      async def get(self):
        self.count += 1
        return {"count": self.count}

    instance = CounterResource()
    app.add_resource(instance, '/counter-instance')
    assert '/counter-instance' in [r.rule for r in app.url_map.iter_rules()]

  @pytest.mark.asyncio
  async def test_class_instantiated_per_request(self, app):
    """
    Given: A Resource class registered
    When: Making multiple requests
    Then: Each request gets a new instance
    """
    class StatefulResource(Resource):
      def __init__(self):
        self.count = 0

      async def get(self):
        self.count += 1
        return {"count": self.count}

    app.add_resource(StatefulResource, '/stateful')

    async with app.test_app() as test_app:
      client = test_app.test_client()

      # Each request should get count=1 (new instance)
      response1 = await client.get('/stateful')
      data1 = await response1.get_json()
      assert data1["count"] == 1

      response2 = await client.get('/stateful')
      data2 = await response2.get_json()
      assert data2["count"] == 1  # New instance, count resets

  @pytest.mark.asyncio
  async def test_instance_reused_across_requests(self, app):
    """
    Given: A Resource instance registered
    When: Making multiple requests
    Then: Same instance is reused
    """
    class StatefulResource(Resource):
      def __init__(self):
        self.count = 0

      async def get(self):
        self.count += 1
        return {"count": self.count}

    instance = StatefulResource()
    app.add_resource(instance, '/stateful-instance')

    async with app.test_app() as test_app:
      client = test_app.test_client()

      # First request: count=1
      response1 = await client.get('/stateful-instance')
      data1 = await response1.get_json()
      assert data1["count"] == 1

      # Second request: count=2 (same instance)
      response2 = await client.get('/stateful-instance')
      data2 = await response2.get_json()
      assert data2["count"] == 2

      # Third request: count=3 (same instance)
      response3 = await client.get('/stateful-instance')
      data3 = await response3.get_json()
      assert data3["count"] == 3

  @pytest.mark.asyncio
  async def test_instance_can_have_prewired_dependencies(self, app):
    """
    Given: A Resource instance with injected dependencies
    When: Making requests
    Then: Dependencies are accessible
    """
    class DatabaseResource(Resource):
      def __init__(self):
        self.db = None

      async def get(self):
        return {"data": self.db.query()}

    instance = DatabaseResource()
    # Simulate dependency injection
    class MockDB:
      def query(self):
        return "mock_data"
    instance.db = MockDB()

    app.add_resource(instance, '/db')

    async with app.test_app() as test_app:
      client = test_app.test_client()
      response = await client.get('/db')
      data = await response.get_json()
      assert data["data"] == "mock_data"

  @pytest.mark.asyncio
  async def test_class_and_instance_work_together(self, app):
    """
    Given: Both class and instance resources registered
    When: Making requests to both
    Then: Each behaves according to its pattern
    """
    class SharedCounter(Resource):
      def __init__(self):
        self.local_count = 0

      async def get(self):
        self.local_count += 1
        return {"local": self.local_count}

    # Register class - each request gets new instance
    app.add_resource(SharedCounter, '/class-counter')

    # Register instance - shared across requests
    shared_instance = SharedCounter()
    app.add_resource(shared_instance, '/instance-counter')

    async with app.test_app() as test_app:
      client = test_app.test_client()

      # Class route: always returns 1 (new instance)
      for i in range(3):
        response = await client.get('/class-counter')
        data = await response.get_json()
        assert data["local"] == 1

      # Instance route: increments (same instance)
      for i in range(1, 4):
        response = await client.get('/instance-counter')
        data = await response.get_json()
        assert data["local"] == i

  @pytest.mark.asyncio
  async def test_instance_methods_attribute_used(self, app):
    """
    Given: A Resource instance registered
    When: Checking route methods
    Then: Should use instance's class methods attribute
    """
    class ReadOnlyResource(Resource):
      methods = ['GET']

      async def get(self):
        return {"read": "only"}

    instance = ReadOnlyResource()
    app.add_resource(instance, '/readonly')

    async with app.test_app() as test_app:
      client = test_app.test_client()

      # GET should work
      response = await client.get('/readonly')
      assert response.status_code == 200

      # POST should return 405
      response = await client.post('/readonly')
      assert response.status_code == 405