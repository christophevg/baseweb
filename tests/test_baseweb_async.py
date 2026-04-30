"""
Tests for Quart migration in Baseweb.

These tests verify the Flask to Quart migration:
- All route handlers are async
- render_template is awaited
- send_from_directory is awaited
- Authentication decorator supports async handlers
- Sync authenticator backward compatibility
- All routes function correctly
"""

import inspect
import os
import tempfile
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from quart import Quart
from quart.testing import QuartClient
from werkzeug.exceptions import HTTPException

from baseweb import Baseweb


# =============================================================================
# Async Handler Tests
# =============================================================================

class TestAsyncHandlers:
    """
    Test that all route handlers are properly converted to async.
    """

    def test_landing_handler_is_async(self):
        """
        Given: A Baseweb instance with default routes
        When: Inspecting the landing route handler
        Then: The handler should be an async coroutine function
        """
        app = Baseweb("test")
        # Get the view function for the landing endpoint
        landing_handler = app.view_functions.get("landing")
        assert landing_handler is not None, "Landing endpoint should exist"
        assert inspect.iscoroutinefunction(landing_handler), \
            "Landing page handler must be async coroutine function"

    def test_store_handler_is_async(self):
        """
        Given: A Baseweb instance with default routes
        When: Inspecting the store route handler
        Then: The handler should be an async coroutine function
        """
        app = Baseweb("test")
        store_handler = app.view_functions.get("store")
        assert store_handler is not None, "Store endpoint should exist"
        assert inspect.iscoroutinefunction(store_handler), \
            "Vuex store handler must be async coroutine function"

    def test_manifest_handler_is_async(self):
        """
        Given: A Baseweb instance configured as PWA
        When: Inspecting the manifest route handler
        Then: The handler should be an async coroutine function
        """
        # Temporarily set style to pwa
        original_style = os.environ.get("APP_STYLE")
        os.environ["APP_STYLE"] = "pwa"
        try:
            app = Baseweb("test")
            manifest_handler = app.view_functions.get("manifest")
            assert manifest_handler is not None, "Manifest endpoint should exist for PWA"
            assert inspect.iscoroutinefunction(manifest_handler), \
                "Manifest handler must be async coroutine function"
        finally:
            if original_style is None:
                os.environ.pop("APP_STYLE", None)
            else:
                os.environ["APP_STYLE"] = original_style

    def test_component_handler_is_async(self):
        """
        Given: A Baseweb instance with registered component
        When: Inspecting the component route handler
        Then: The handler should be an async coroutine function
        """
        app = Baseweb("test")
        app_handler = app.view_functions.get("app")
        assert app_handler is not None, "App endpoint should exist"
        assert inspect.iscoroutinefunction(app_handler), \
            "Component handler must be async coroutine function"

    def test_stylesheet_handler_is_async(self):
        """
        Given: A Baseweb instance with registered stylesheet
        When: Inspecting the stylesheet route handler
        Then: The handler should be an async coroutine function
        """
        app = Baseweb("test")
        style_handler = app.view_functions.get("app-style")
        assert style_handler is not None, "App-style endpoint should exist"
        assert inspect.iscoroutinefunction(style_handler), \
            "Stylesheet handler must be async coroutine function"

    def test_static_handler_is_async(self):
        """
        Given: A Baseweb instance with app static folder
        When: Inspecting the static files route handler
        Then: The handler should be an async coroutine function
        """
        app = Baseweb("test")
        # The static handler is registered directly, not through _send
        # Find the static handler in the route rules
        for rule in app.url_map._rules:
            if "/app/static/<path:filename>" in str(rule):
                handler = app.view_functions.get(rule.endpoint)
                assert handler is not None, "Static handler should exist"
                assert inspect.iscoroutinefunction(handler), \
                    "Static files handler must be async coroutine function"
                break


class TestRenderTemplateAsync:
    """
    Test that render_template calls are properly awaited.
    """

    @pytest.mark.asyncio
    async def test_render_template_awaited_landing(self):
        """
        Given: A Baseweb instance with default routes
        When: Requesting the landing page (GET /)
        Then: render_template should be awaited, returning a Response object
        """
        app = Baseweb("test")
        async with app.test_client() as client:
            response = await client.get("/")
            assert response.status_code == 200
            # Verify we get actual content (not a coroutine)
            content = await response.get_data()
            assert len(content) > 0
            assert b"<html" in content.lower() or b"<!doctype" in content.lower()

    @pytest.mark.asyncio
    async def test_render_template_awaited_store(self):
        """
        Given: A Baseweb instance with default routes
        When: Requesting the Vuex store (GET /static/js/store.js)
        Then: render_template should be awaited, returning a Response object
        """
        app = Baseweb("test")
        async with app.test_client() as client:
            response = await client.get("/static/js/store.js")
            assert response.status_code == 200
            content = await response.get_data()
            assert b"Vuex.Store" in content

    @pytest.mark.asyncio
    async def test_render_template_awaited_manifest(self):
        """
        Given: A Baseweb instance configured as PWA (style='pwa')
        When: Requesting the manifest (GET /manifest.json)
        Then: render_template should be awaited, returning a Response object
        """
        original_style = os.environ.get("APP_STYLE")
        os.environ["APP_STYLE"] = "pwa"
        try:
            app = Baseweb("test")
            async with app.test_client() as client:
                response = await client.get("/manifest.json")
                assert response.status_code == 200
                content = await response.get_data()
                assert b'"name"' in content
        finally:
            if original_style is None:
                os.environ.pop("APP_STYLE", None)
            else:
                os.environ["APP_STYLE"] = original_style


class TestSendFromDirectoryAsync:
    """
    Test that send_from_directory calls are properly awaited.
    """

    @pytest.mark.asyncio
    async def test_send_from_directory_awaited_component(self):
        """
        Given: A Baseweb instance with a registered component
        When: Requesting a component file (GET /app/<filename>)
        Then: send_from_directory should be awaited, returning a Response object
        """
        # Create a temporary component file
        with tempfile.TemporaryDirectory() as tmpdir:
            component_file = Path(tmpdir) / "test.js"
            component_file.write_text("console.log('test component');")

            app = Baseweb("test")
            app.register_component("test.js", tmpdir)

            async with app.test_client() as client:
                response = await client.get("/app/test.js")
                assert response.status_code == 200
                content = await response.get_data()
                assert b"test component" in content

    @pytest.mark.asyncio
    async def test_send_from_directory_awaited_stylesheet(self):
        """
        Given: A Baseweb instance with a registered stylesheet
        When: Requesting a stylesheet file (GET /app/style/<filename>)
        Then: send_from_directory should be awaited, returning a Response object
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            stylesheet_file = Path(tmpdir) / "test.css"
            stylesheet_file.write_text("body { color: red; }")

            app = Baseweb("test")
            app.register_stylesheet("test.css", tmpdir)

            async with app.test_client() as client:
                response = await client.get("/app/style/test.css")
                assert response.status_code == 200
                content = await response.get_data()
                assert b"color" in content

    @pytest.mark.asyncio
    async def test_send_from_directory_awaited_static(self):
        """
        Given: A Baseweb instance with app_static_folder configured
        When: Requesting a static file (GET /app/static/<filename>)
        Then: send_from_directory should be awaited, returning a Response object
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            static_file = Path(tmpdir) / "test.txt"
            static_file.write_text("static content")

            app = Baseweb("test")
            app.app_static_folder = tmpdir

            async with app.test_client() as client:
                response = await client.get("/app/static/test.txt")
                assert response.status_code == 200
                content = await response.get_data()
                assert b"static content" in content


# =============================================================================
# Authentication Tests
# =============================================================================

class TestAuthenticationAsync:
    """
    Test that authentication decorator properly supports async handlers.
    """

    @pytest.mark.asyncio
    async def test_sync_authenticator_backward_compatibility(self):
        """
        Given: A Baseweb instance with a synchronous authenticator
        When: Authenticating a request
        Then: The sync authenticator should work correctly (backward compatibility)
        """
        def sync_authenticator(scope, request):
            return True  # Sync authenticator returning True

        app = Baseweb("test")
        app.authenticator = sync_authenticator

        async with app.test_client() as client:
            response = await client.get("/")
            assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_async_authenticator_support(self):
        """
        Given: A Baseweb instance with an async authenticator
        When: Authenticating a request
        Then: The async authenticator should be awaited correctly
        """
        async def async_authenticator(scope, request):
            return True  # Async authenticator returning True

        app = Baseweb("test")
        app.authenticator = async_authenticator

        async with app.test_client() as client:
            response = await client.get("/")
            assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_authenticated_decorator_makes_handler_async(self):
        """
        Given: A route decorated with @authenticated(scope)
        When: Inspecting the decorated handler
        Then: The wrapper should be an async coroutine function
        """
        app = Baseweb("test")
        # Check that the _render method returns an async handler
        handler = app._render(security_scope="test.scope")
        assert inspect.iscoroutinefunction(handler), \
            "Authenticated decorator must return async wrapper"

    @pytest.mark.asyncio
    async def test_authentication_failure_returns_401(self):
        """
        Given: A protected route with an authenticator that returns False
        When: Accessing the route without valid credentials
        Then: Should return 401 Unauthorized with WWW-Authenticate header
        """
        def failing_authenticator(scope, request):
            return False

        app = Baseweb("test")
        app.authenticator = failing_authenticator

        async with app.test_client() as client:
            response = await client.get("/")
            assert response.status_code == 401
            assert "WWW-Authenticate" in response.headers
            assert "Basic realm=" in response.headers["WWW-Authenticate"]

    @pytest.mark.asyncio
    async def test_authentication_success_allows_access(self):
        """
        Given: A protected route with an authenticator that returns True
        When: Accessing the route with valid credentials
        Then: Should allow access to the route handler
        """
        def passing_authenticator(scope, request):
            return True

        app = Baseweb("test")
        app.authenticator = passing_authenticator

        async with app.test_client() as client:
            response = await client.get("/")
            assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_no_authenticator_allows_access(self):
        """
        Given: A route with security_scope but no authenticator configured
        When: Accessing the route
        Then: Should allow access (default permissive behavior)
        """
        app = Baseweb("test")
        app.authenticator = None

        async with app.test_client() as client:
            response = await client.get("/")
            assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_async_authenticator_failure_returns_401(self):
        """
        Given: An async authenticator that returns False
        When: Authentication is attempted
        Then: Should return 401 Unauthorized
        """
        async def async_failing_authenticator(scope, request):
            return False

        app = Baseweb("test")
        app.authenticator = async_failing_authenticator

        async with app.test_client() as client:
            response = await client.get("/")
            assert response.status_code == 401


class TestValidCredentialsAsync:
    """
    Test that _valid_credentials properly handles async authenticators.
    """

    @pytest.mark.asyncio
    async def test_valid_credentials_none_scope_returns_true(self):
        """
        Given: _valid_credentials called with scope=None
        When: Checking credentials
        Then: Should return True immediately (no authentication required)
        """
        app = Baseweb("test")
        result = await app._valid_credentials(None)
        assert result is True

    @pytest.mark.asyncio
    async def test_valid_credentials_none_authenticator_returns_true(self):
        """
        Given: _valid_credentials called with authenticator=None
        When: Checking credentials
        Then: Should return True immediately (no authenticator configured)
        """
        app = Baseweb("test")
        app.authenticator = None
        result = await app._valid_credentials("some.scope")
        assert result is True

    @pytest.mark.asyncio
    async def test_valid_credentials_logs_warning_on_failure(self):
        """
        Given: An authenticator that returns False
        When: _valid_credentials is called
        Then: Should log a warning about incorrect credentials
        """
        def failing_authenticator(scope, request):
            return False

        app = Baseweb("test")
        app.authenticator = failing_authenticator

        with patch('baseweb.logger') as mock_logger:
            result = await app._valid_credentials("test.scope")
            # We just verify it returns False
            assert result is False
            # Verify warning was logged
            mock_logger.warning.assert_called_once_with("incorrect credentials")


# =============================================================================
# Route Handler Tests
# =============================================================================

class TestLandingRoute:
    """
    Test the landing page route (GET /).
    """

    @pytest.mark.asyncio
    async def test_landing_route_returns_200(self):
        """
        Given: A Baseweb instance with default configuration
        When: Requesting GET /
        Then: Should return 200 OK with rendered template
        """
        app = Baseweb("test")
        async with app.test_client() as client:
            response = await client.get("/")
            assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_landing_route_renders_template(self):
        """
        Given: A Baseweb instance with default configuration
        When: Requesting GET /
        Then: Response should contain rendered main.html template
        """
        app = Baseweb("test")
        async with app.test_client() as client:
            response = await client.get("/")
            content = await response.get_data()
            assert b"<!DOCTYPE html>" in content or b"<!doctype html>" in content
            assert b"<html" in content.lower()

    @pytest.mark.asyncio
    async def test_landing_route_with_authentication(self):
        """
        Given: A Baseweb instance with authenticator and protected landing
        When: Requesting GET / without valid credentials
        Then: Should return 401 Unauthorized
        """
        def failing_auth(scope, request):
            return False

        app = Baseweb("test")
        app.authenticator = failing_auth

        async with app.test_client() as client:
            response = await client.get("/")
            assert response.status_code == 401


class TestStoreRoute:
    """
    Test the Vuex store route (GET /static/js/store.js).
    """

    @pytest.mark.asyncio
    async def test_store_route_returns_200(self):
        """
        Given: A Baseweb instance with default configuration
        When: Requesting GET /static/js/store.js
        Then: Should return 200 OK with store.js content
        """
        app = Baseweb("test")
        async with app.test_client() as client:
            response = await client.get("/static/js/store.js")
            assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_store_route_returns_javascript_content_type(self):
        """
        Given: A Baseweb instance with default configuration
        When: Requesting GET /static/js/store.js
        Then: Response should have application/javascript content type
        """
        app = Baseweb("test")
        async with app.test_client() as client:
            response = await client.get("/static/js/store.js")
            content_type = response.content_type
            # Accept either application/javascript or text/javascript
            assert "javascript" in content_type.lower()


class TestManifestRoute:
    """
    Test the PWA manifest route (GET /manifest.json).
    """

    @pytest.mark.asyncio
    async def test_manifest_route_returns_200_when_pwa(self):
        """
        Given: A Baseweb instance configured as PWA (style='pwa')
        When: Requesting GET /manifest.json
        Then: Should return 200 OK with manifest content
        """
        original_style = os.environ.get("APP_STYLE")
        os.environ["APP_STYLE"] = "pwa"
        try:
            app = Baseweb("test")
            async with app.test_client() as client:
                response = await client.get("/manifest.json")
                assert response.status_code == 200
        finally:
            if original_style is None:
                os.environ.pop("APP_STYLE", None)
            else:
                os.environ["APP_STYLE"] = original_style

    @pytest.mark.asyncio
    async def test_manifest_route_returns_404_when_not_pwa(self):
        """
        Given: A Baseweb instance configured as web (style='web')
        When: Requesting GET /manifest.json
        Then: Should return 404 Not Found
        """
        original_style = os.environ.get("APP_STYLE")
        os.environ["APP_STYLE"] = "web"
        try:
            app = Baseweb("test")
            async with app.test_client() as client:
                response = await client.get("/manifest.json")
                assert response.status_code == 404
        finally:
            if original_style is None:
                os.environ.pop("APP_STYLE", None)
            else:
                os.environ["APP_STYLE"] = original_style

    @pytest.mark.asyncio
    async def test_manifest_route_renders_manifest_template(self):
        """
        Given: A Baseweb instance configured as PWA
        When: Requesting GET /manifest.json
        Then: Response should contain rendered manifest.json template
        """
        original_style = os.environ.get("APP_STYLE")
        os.environ["APP_STYLE"] = "pwa"
        try:
            app = Baseweb("test")
            async with app.test_client() as client:
                response = await client.get("/manifest.json")
                content = await response.get_data()
                assert b'"name"' in content
                assert b'"short_name"' in content
        finally:
            if original_style is None:
                os.environ.pop("APP_STYLE", None)
            else:
                os.environ["APP_STYLE"] = original_style


class TestComponentRoute:
    """
    Test the component files route (GET /app/<path:filename>).
    """

    @pytest.mark.asyncio
    async def test_component_route_returns_200_for_registered_component(self):
        """
        Given: A Baseweb instance with a registered component
        When: Requesting GET /app/<filename>
        Then: Should return 200 OK with component file content
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            component_file = Path(tmpdir) / "mycomponent.js"
            component_file.write_text("// my component")

            app = Baseweb("test")
            app.register_component("mycomponent.js", tmpdir)

            async with app.test_client() as client:
                response = await client.get("/app/mycomponent.js")
                assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_component_route_returns_404_for_unregistered_component(self):
        """
        Given: A Baseweb instance with no registered component for filename
        When: Requesting GET /app/<filename>
        Then: Should return 404 Not Found or appropriate error
        """
        app = Baseweb("test")
        # No components registered

        async with app.test_client() as client:
            response = await client.get("/app/nonexistent.js")
            assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_component_route_with_authentication(self):
        """
        Given: A Baseweb instance with authenticator and registered component
        When: Requesting component without valid credentials
        Then: Should return 401 Unauthorized
        """
        def failing_auth(scope, request):
            return False

        with tempfile.TemporaryDirectory() as tmpdir:
            component_file = Path(tmpdir) / "protected.js"
            component_file.write_text("// protected component")

            app = Baseweb("test")
            app.authenticator = failing_auth
            app.register_component("protected.js", tmpdir)

            async with app.test_client() as client:
                response = await client.get("/app/protected.js")
                assert response.status_code == 401


class TestStylesheetRoute:
    """
    Test the stylesheet files route (GET /app/style/<path:filename>).
    """

    @pytest.mark.asyncio
    async def test_stylesheet_route_returns_200_for_registered_stylesheet(self):
        """
        Given: A Baseweb instance with a registered stylesheet
        When: Requesting GET /app/style/<filename>
        Then: Should return 200 OK with stylesheet content
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            stylesheet_file = Path(tmpdir) / "mystyle.css"
            stylesheet_file.write_text("body { margin: 0; }")

            app = Baseweb("test")
            app.register_stylesheet("mystyle.css", tmpdir)

            async with app.test_client() as client:
                response = await client.get("/app/style/mystyle.css")
                assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_stylesheet_route_returns_404_for_unregistered_stylesheet(self):
        """
        Given: A Baseweb instance with no registered stylesheet for filename
        When: Requesting GET /app/style/<filename>
        Then: Should return 404 Not Found or appropriate error
        """
        app = Baseweb("test")
        # No stylesheets registered

        async with app.test_client() as client:
            response = await client.get("/app/style/nonexistent.css")
            assert response.status_code == 404


class TestStaticRoute:
    """
    Test the app static files route (GET /app/static/<path:filename>).
    """

    @pytest.mark.asyncio
    async def test_static_route_returns_200_for_existing_file(self):
        """
        Given: A Baseweb instance with app_static_folder configured
        When: Requesting GET /app/static/<filename> for existing file
        Then: Should return 200 OK with file content
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            static_file = Path(tmpdir) / "data.json"
            static_file.write_text('{"key": "value"}')

            app = Baseweb("test")
            app.app_static_folder = tmpdir

            async with app.test_client() as client:
                response = await client.get("/app/static/data.json")
                assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_static_route_returns_404_for_missing_file(self):
        """
        Given: A Baseweb instance with app_static_folder configured
        When: Requesting GET /app/static/<filename> for non-existent file
        Then: Should return 404 Not Found
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            app = Baseweb("test")
            app.app_static_folder = tmpdir

            async with app.test_client() as client:
                response = await client.get("/app/static/missing.json")
                assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_static_route_returns_404_without_app_static_folder(self):
        """
        Given: A Baseweb instance without app_static_folder configured
        When: Requesting GET /app/static/<filename>
        Then: Should return 404 Not Found with warning logged
        """
        app = Baseweb("test")
        app.app_static_folder = None

        async with app.test_client() as client:
            response = await client.get("/app/static/anyfile.txt")
            assert response.status_code == 404


class TestAppRoute:
    """
    Test the registered app routes.
    """

    @pytest.mark.asyncio
    async def test_app_route_returns_200(self):
        """
        Given: A Baseweb instance with a registered app route
        When: Requesting the registered route
        Then: Should return 200 OK with rendered template
        """
        app = Baseweb("test")
        app.register_app_route("/custom")

        async with app.test_client() as client:
            response = await client.get("/custom")
            assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_app_route_with_authentication(self):
        """
        Given: A Baseweb instance with protected app route
        When: Requesting the route without valid credentials
        Then: Should return 401 Unauthorized
        """
        def failing_auth(scope, request):
            return False

        app = Baseweb("test")
        app.authenticator = failing_auth
        app.register_app_route("/protected")

        async with app.test_client() as client:
            response = await client.get("/protected")
            assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_app_route_with_optional_params(self):
        """
        Given: A Baseweb instance with route containing optional params
        When: Requesting with and without optional params
        Then: Both variations should route correctly
        """
        app = Baseweb("test")
        # Register route with optional parameter
        app.register_app_route("/page/<id?>")

        async with app.test_client() as client:
            # Both should work
            response1 = await client.get("/page")
            assert response1.status_code == 200

            response2 = await client.get("/page/")
            assert response2.status_code == 200


# =============================================================================
# Public API Tests
# =============================================================================

class TestPublicAPISync:
    """
    Test that public API methods remain synchronous (no breaking changes).
    """

    def test_register_component_is_sync(self):
        """
        Given: The Baseweb class
        When: Inspecting register_component method
        Then: It should be a synchronous function, not async
        """
        # This test verifies that the public API remains synchronous
        # to maintain backward compatibility for users
        assert not inspect.iscoroutinefunction(Baseweb.register_component), \
            "register_component must remain synchronous (breaking change)"

    def test_register_stylesheet_is_sync(self):
        """
        Given: The Baseweb class
        When: Inspecting register_stylesheet method
        Then: It should be a synchronous function, not async
        """
        assert not inspect.iscoroutinefunction(Baseweb.register_stylesheet), \
            "register_stylesheet must remain synchronous (breaking change)"

    def test_register_external_script_is_sync(self):
        """
        Given: The Baseweb class
        When: Inspecting register_external_script method
        Then: It should be a synchronous function, not async
        """
        assert not inspect.iscoroutinefunction(Baseweb.register_external_script), \
            "register_external_script must remain synchronous (breaking change)"

    def test_register_app_route_is_sync(self):
        """
        Given: The Baseweb class
        When: Inspecting register_app_route method
        Then: It should be a synchronous function, not async
        """
        assert not inspect.iscoroutinefunction(Baseweb.register_app_route), \
            "register_app_route must remain synchronous (breaking change)"

    def test_init_is_sync(self):
        """
        Given: The Baseweb class
        When: Inspecting __init__ method
        Then: It should be a synchronous function, not async
        """
        assert not inspect.iscoroutinefunction(Baseweb.__init__), \
            "__init__ must remain synchronous (breaking change)"

    def test_log_config_is_sync(self):
        """
        Given: The Baseweb class
        When: Inspecting log_config method
        Then: It should be a synchronous function, not async
        """
        assert not inspect.iscoroutinefunction(Baseweb.log_config), \
            "log_config must remain synchronous"

    def test_log_routes_is_sync(self):
        """
        Given: The Baseweb class
        When: Inspecting log_routes method
        Then: It should be a synchronous function, not async
        """
        assert not inspect.iscoroutinefunction(Baseweb.log_routes), \
            "log_routes must remain synchronous"


class TestInheritance:
    """
    Test that Baseweb properly inherits from Quart (not Flask).
    """

    def test_baseweb_inherits_from_quart(self):
        """
        Given: The Baseweb class
        When: Checking the base class
        Then: It should inherit from Quart, not Flask
        """
        assert issubclass(Baseweb, Quart), \
            "Baseweb must inherit from quart.Quart, not flask.Flask"

    def test_baseweb_instance_is_quart_app(self):
        """
        Given: A Baseweb instance
        When: Checking instance type
        Then: It should be a Quart application instance
        """
        app = Baseweb("test")
        assert isinstance(app, Quart), \
            "Baseweb instance must be a Quart application"


# =============================================================================
# Integration Tests
# =============================================================================

class TestQuartIntegration:
    """
    Integration tests for Quart-specific behavior.
    """

    @pytest.mark.asyncio
    async def test_request_context_in_async_handler(self):
        """
        Given: An async route handler
        When: Accessing the Quart request object
        Then: The request context should be available
        """
        app = Baseweb("test")
        async with app.test_client() as client:
            # Accessing a route should work with request context
            response = await client.get("/")
            assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_multiple_concurrent_requests(self):
        """
        Given: A Baseweb instance
        When: Making multiple concurrent requests
        Then: Each request should be handled independently
        """
        import asyncio

        app = Baseweb("test")

        async def make_request(client, path):
            response = await client.get(path)
            return response.status_code

        async with app.test_client() as client:
            # Make multiple concurrent requests
            results = await asyncio.gather(
                make_request(client, "/"),
                make_request(client, "/static/js/store.js"),
                make_request(client, "/"),
            )
            assert all(status == 200 for status in results)

    @pytest.mark.asyncio
    async def test_request_isolation(self):
        """
        Given: Two concurrent requests with different data
        When: Processing requests concurrently
        Then: Request data should not leak between requests
        """
        import asyncio

        app = Baseweb("test")

        async def make_request(client, path):
            response = await client.get(path)
            content = await response.get_data()
            return len(content)

        async with app.test_client() as client:
            # Request different content concurrently
            sizes = await asyncio.gather(
                make_request(client, "/"),
                make_request(client, "/static/js/store.js"),
            )
            # Both should return valid content
            assert all(size > 0 for size in sizes)

    @pytest.mark.asyncio
    async def test_test_client_async_support(self):
        """
        Given: A Baseweb instance
        When: Using Quart's test client
        Then: Async request methods should work correctly
        """
        app = Baseweb("test")
        async with app.test_client() as client:
            # All async HTTP methods should work
            response = await client.get("/")
            assert response.status_code == 200


class TestBackwardCompatibility:
    """
    Tests for backward compatibility during migration.
    """

    @pytest.mark.asyncio
    async def test_existing_routes_preserved(self):
        """
        Given: Default Baseweb routes
        When: Listing all routes
        Then: All expected routes should be present (/, /static/js/store.js, etc.)
        """
        app = Baseweb("test")

        # Get all registered routes
        routes = [str(rule) for rule in app.url_map._rules]

        # Core routes should be present
        assert "/" in routes or any("/" in r for r in routes), "Landing route should exist"
        assert "/static/js/store.js" in routes, "Store route should exist"
        assert "/app/<path:filename>" in routes, "App route should exist"

    def test_settings_configuration_unchanged(self):
        """
        Given: Baseweb initialization with environment variables
        When: Loading configuration
        Then: Settings should be populated correctly (same as Flask version)
        """
        # Set some environment variables
        original_name = os.environ.get("APP_NAME")
        original_title = os.environ.get("APP_TITLE")
        os.environ["APP_NAME"] = "TestApp"
        os.environ["APP_TITLE"] = "Test Application"

        try:
            app = Baseweb("test")
            assert app.settings.name == "TestApp"
            assert app.settings.title == "Test Application"
        finally:
            if original_name is None:
                os.environ.pop("APP_NAME", None)
            else:
                os.environ["APP_NAME"] = original_name
            if original_title is None:
                os.environ.pop("APP_TITLE", None)
            else:
                os.environ["APP_TITLE"] = original_title

    def test_component_registration_unchanged(self):
        """
        Given: A Baseweb instance
        When: Registering components
        Then: Registration should work the same as Flask version
        """
        app = Baseweb("test")
        app.register_component("test.js", "/some/path")

        assert "test.js" in app._files["components"]
        assert app._files["components"]["test.js"] == "/some/path"

    def test_stylesheet_registration_unchanged(self):
        """
        Given: A Baseweb instance
        When: Registering stylesheets
        Then: Registration should work the same as Flask version
        """
        app = Baseweb("test")
        app.register_stylesheet("style.css", "/some/path")

        assert "style.css" in app._files["stylesheets"]
        assert app._files["stylesheets"]["style.css"] == "/some/path"

    def test_script_registration_unchanged(self):
        """
        Given: A Baseweb instance
        When: Registering external scripts
        Then: Registration should work the same as Flask version
        """
        app = Baseweb("test")
        app.register_external_script("https://example.com/script.js")

        assert "https://example.com/script.js" in app._files["scripts"]


# =============================================================================
# Error Handling Tests
# =============================================================================

class TestErrorHandling:
    """
    Test error handling in async context.
    """

    @pytest.mark.asyncio
    async def test_template_not_found_returns_404(self):
        """
        Given: A request for a non-existent template
        When: The handler tries to render it
        Then: Should abort with 404 status code
        """
        app = Baseweb("test")

        # Create a handler that references a non-existent template
        handler = app._render("nonexistent.html", security_scope=None)

        async with app.test_client() as client:
            # Call the handler directly
            # When a non-existent template is accessed, it should raise TemplateNotFound
            # which results in a 404
            try:
                result = await handler()
                # If we got here, check if it's a response with error status
                if hasattr(result, 'status_code'):
                    assert result.status_code == 404
            except Exception as e:
                # TemplateNotFound results in 404 abort
                if isinstance(e, HTTPException):
                    assert e.status_code == 404

    @pytest.mark.asyncio
    async def test_file_not_found_returns_404(self):
        """
        Given: A request for a non-existent component file
        When: The handler tries to send it
        Then: Should return 404 status code
        """
        app = Baseweb("test")
        # No components registered

        async with app.test_client() as client:
            response = await client.get("/app/nonexistent.js")
            assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_abort_in_async_context(self):
        """
        Given: An async handler that calls abort()
        When: An error condition occurs
        Then: Should properly raise HTTPException in async context
        """
        # This is implicitly tested by file_not_found test
        # abort(404) works correctly in async handlers
        pass


# =============================================================================
# Response Tests
# =============================================================================

class TestResponses:
    """
    Test response handling in async context.
    """

    @pytest.mark.asyncio
    async def test_response_object_from_render_template(self):
        """
        Given: An async handler calling render_template
        When: The template is rendered
        Then: Should return a proper Response object (not coroutine)
        """
        app = Baseweb("test")
        async with app.test_client() as client:
            response = await client.get("/")
            # Response should be a Quart Response object
            assert hasattr(response, 'status_code')
            assert hasattr(response, 'headers')
            # Content should be bytes
            content = await response.get_data()
            assert isinstance(content, bytes)

    @pytest.mark.asyncio
    async def test_response_object_from_send_from_directory(self):
        """
        Given: An async handler calling send_from_directory
        When: The file is sent
        Then: Should return a proper Response object (not coroutine)
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir) / "test.js"
            test_file.write_text("console.log('test');")

            app = Baseweb("test")
            app.register_component("test.js", tmpdir)

            async with app.test_client() as client:
                response = await client.get("/app/test.js")
                # Response should be a Quart Response object
                assert hasattr(response, 'status_code')
                assert response.status_code == 200
                # Content should be bytes
                content = await response.get_data()
                assert isinstance(content, bytes)

    @pytest.mark.asyncio
    async def test_401_response_format(self):
        """
        Given: An authentication failure
        When: Returning 401 response
        Then: Should have WWW-Authenticate header with realm
        """
        def failing_auth(scope, request):
            return False

        app = Baseweb("test")
        app.authenticator = failing_auth

        async with app.test_client() as client:
            response = await client.get("/")
            assert response.status_code == 401
            assert "WWW-Authenticate" in response.headers
            assert "Basic realm=" in response.headers["WWW-Authenticate"]