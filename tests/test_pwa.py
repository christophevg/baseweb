"""Tests for PWA manifest and service worker functionality.

This module contains tests for task-6.1: PWA manifest and service worker
foundation. Tests verify:
- Manifest endpoint serves valid JSON with required fields for iOS compatibility
- Service Worker endpoint serves script with correct headers
- HTML template includes iOS-specific meta tags for standalone mode
"""

import json
import os

import pytest
from quart.testing import QuartClient

from baseweb import Baseweb

# ==============================================================================
# Test Infrastructure
# ==============================================================================


def create_pwa_app(name: str = "test") -> Baseweb:
  """Create a Baseweb instance configured as PWA for testing.

  Args:
    name: Application name

  Returns:
    Baseweb instance with APP_STYLE=pwa
  """
  original_style = os.environ.get("APP_STYLE")
  os.environ["APP_STYLE"] = "pwa"
  try:
    return Baseweb(name)
  finally:
    if original_style is None:
      os.environ.pop("APP_STYLE", None)
    else:
      os.environ["APP_STYLE"] = original_style


def create_web_app(name: str = "test") -> Baseweb:
  """Create a Baseweb instance configured as regular web app.

  Args:
    name: Application name

  Returns:
    Baseweb instance with APP_STYLE=web
  """
  original_style = os.environ.get("APP_STYLE")
  os.environ["APP_STYLE"] = "web"
  try:
    return Baseweb(name)
  finally:
    if original_style is None:
      os.environ.pop("APP_STYLE", None)
    else:
      os.environ["APP_STYLE"] = original_style


# ==============================================================================
# Manifest Endpoint Tests - Valid JSON
# ==============================================================================


class TestManifestValidJSON:
  """
  Tests verifying the manifest endpoint returns valid JSON.
  """

  @pytest.mark.asyncio
  async def test_manifest_returns_valid_json(self):
    """
    Given: A Baseweb instance configured as PWA
    When: Requesting GET /manifest.json
    Then: Response should be valid JSON that can be parsed
    """
    app = create_pwa_app()
    client: QuartClient = app.test_client()
    response = await client.get("/manifest.json")
    assert response.status_code == 200
    manifest = json.loads(await response.get_data())
    assert isinstance(manifest, dict)

  @pytest.mark.asyncio
  async def test_manifest_returns_json_content_type(self):
    """
    Given: A Baseweb instance configured as PWA
    When: Requesting GET /manifest.json
    Then: Content-Type header should be application/json or application/manifest+json
    """
    app = create_pwa_app()
    client: QuartClient = app.test_client()
    response = await client.get("/manifest.json")
    content_type = response.content_type
    assert content_type in ("application/json", "application/manifest+json")


# ==============================================================================
# Manifest Required Fields Tests
# ==============================================================================


class TestManifestRequiredFields:
  """
  Tests verifying the manifest contains all required PWA fields.

  Required fields per W3C Web App Manifest spec:
  - name: The name of the web application
  - short_name: A short version of the name
  - display: Preferred display mode (standalone, fullscreen, minimal-ui, browser)
  - icons: Array of icon objects with src, sizes, and type
  """

  @pytest.mark.asyncio
  async def test_manifest_contains_name_field(self):
    """
    Given: A PWA manifest endpoint
    When: Parsing the manifest JSON
    Then: Manifest should contain 'name' field with non-empty string
    """
    app = create_pwa_app()
    client: QuartClient = app.test_client()
    response = await client.get("/manifest.json")
    manifest = json.loads(await response.get_data())
    assert "name" in manifest
    assert isinstance(manifest["name"], str)
    assert len(manifest["name"]) > 0

  @pytest.mark.asyncio
  async def test_manifest_contains_short_name_field(self):
    """
    Given: A PWA manifest endpoint
    When: Parsing the manifest JSON
    Then: Manifest should contain 'short_name' field with non-empty string
    """
    app = create_pwa_app()
    client: QuartClient = app.test_client()
    response = await client.get("/manifest.json")
    manifest = json.loads(await response.get_data())
    assert "short_name" in manifest
    assert isinstance(manifest["short_name"], str)
    assert len(manifest["short_name"]) > 0

  @pytest.mark.asyncio
  async def test_manifest_contains_display_field(self):
    """
    Given: A PWA manifest endpoint
    When: Parsing the manifest JSON
    Then: Manifest should contain 'display' field set to 'standalone' or 'minimal-ui'

    Note: iOS Safari requires 'standalone' or 'minimal-ui' for Home Screen
    installation to work properly.
    """
    app = create_pwa_app()
    client: QuartClient = app.test_client()
    response = await client.get("/manifest.json")
    manifest = json.loads(await response.get_data())
    assert "display" in manifest
    assert manifest["display"] in ["standalone", "minimal-ui"]

  @pytest.mark.asyncio
  async def test_manifest_display_is_standalone(self):
    """
    Given: A PWA manifest endpoint
    When: Parsing the manifest JSON
    Then: 'display' field should be 'standalone' for full PWA experience

    iOS Safari supports 'standalone' mode which hides browser UI and
    provides native app-like experience when launched from Home Screen.
    """
    app = create_pwa_app()
    client: QuartClient = app.test_client()
    response = await client.get("/manifest.json")
    manifest = json.loads(await response.get_data())
    assert manifest["display"] == "standalone"

  @pytest.mark.asyncio
  async def test_manifest_contains_icons_array(self):
    """
    Given: A PWA manifest endpoint
    When: Parsing the manifest JSON
    Then: Manifest should contain 'icons' field as non-empty array
    """
    app = create_pwa_app()
    client: QuartClient = app.test_client()
    response = await client.get("/manifest.json")
    manifest = json.loads(await response.get_data())
    assert "icons" in manifest
    assert isinstance(manifest["icons"], list)
    assert len(manifest["icons"]) > 0

  @pytest.mark.asyncio
  async def test_manifest_icons_have_required_properties(self):
    """
    Given: A PWA manifest with icons array
    When: Parsing each icon entry
    Then: Each icon should have 'src', 'sizes', and 'type' properties
    """
    app = create_pwa_app()
    client: QuartClient = app.test_client()
    response = await client.get("/manifest.json")
    manifest = json.loads(await response.get_data())
    for icon in manifest["icons"]:
      assert "src" in icon
      assert "sizes" in icon
      assert "type" in icon


# ==============================================================================
# Manifest iOS Compatibility Tests
# ==============================================================================


class TestManifestIOSCompatibility:
  """
  Tests verifying iOS Safari compatibility requirements for manifest.

  iOS 16.4+ Safari requirements:
  - 180x180 icon for Home Screen (apple-touch-icon)
  - 192x192 icon for splash screen
  - description field for app store compatibility
  - scope field for Service Worker boundary
  """

  @pytest.mark.asyncio
  async def test_manifest_contains_180x180_icon(self):
    """
    Given: A PWA manifest for iOS compatibility
    When: Parsing the manifest icons array
    Then: Icons should include an entry with sizes="180x180"

    iOS Safari uses the 180x180 icon for the Home Screen icon.
    Without this, iOS will fall back to apple-touch-icon or favicon.
    """
    app = create_pwa_app()
    client: QuartClient = app.test_client()
    response = await client.get("/manifest.json")
    manifest = json.loads(await response.get_data())
    icon_sizes = [icon["sizes"] for icon in manifest["icons"]]
    assert "180x180" in icon_sizes

  @pytest.mark.asyncio
  async def test_manifest_contains_192x192_icon(self):
    """
    Given: A PWA manifest for iOS compatibility
    When: Parsing the manifest icons array
    Then: Icons should include an entry with sizes="192x192"

    Required for splash screen and general PWA compatibility.
    """
    app = create_pwa_app()
    client: QuartClient = app.test_client()
    response = await client.get("/manifest.json")
    manifest = json.loads(await response.get_data())
    icon_sizes = [icon["sizes"] for icon in manifest["icons"]]
    assert "192x192" in icon_sizes

  @pytest.mark.asyncio
  async def test_manifest_contains_description_field(self):
    """
    Given: A PWA manifest for iOS compatibility
    When: Parsing the manifest JSON
    Then: Manifest should contain 'description' field

    The description field is used by app stores and for accessibility.
    It should describe the purpose of the application.
    """
    app = create_pwa_app()
    client: QuartClient = app.test_client()
    response = await client.get("/manifest.json")
    manifest = json.loads(await response.get_data())
    assert "description" in manifest
    assert isinstance(manifest["description"], str)

  @pytest.mark.asyncio
  async def test_manifest_contains_scope_field(self):
    """
    Given: A PWA manifest for iOS compatibility
    When: Parsing the manifest JSON
    Then: Manifest should contain 'scope' field set to "/"

    The scope defines the navigation boundary for the Service Worker.
    "/" allows the Service Worker to control all pages on the domain.
    """
    app = create_pwa_app()
    client: QuartClient = app.test_client()
    response = await client.get("/manifest.json")
    manifest = json.loads(await response.get_data())
    assert "scope" in manifest

  @pytest.mark.asyncio
  async def test_manifest_scope_is_root(self):
    """
    Given: A PWA manifest with scope field
    When: Reading the scope value
    Then: Scope should be "/" to allow Service Worker to control all pages

    This is important for iOS Safari to properly handle navigation
    within the installed PWA context.
    """
    app = create_pwa_app()
    client: QuartClient = app.test_client()
    response = await client.get("/manifest.json")
    manifest = json.loads(await response.get_data())
    assert manifest["scope"] == "/"


# ==============================================================================
# Service Worker Endpoint Tests
# ==============================================================================


class TestServiceWorkerEndpoint:
  """
  Tests verifying the Service Worker script endpoint.

  Service Worker must be served at the root scope or with proper
  Service-Worker-Allowed header to control all pages.
  """

  @pytest.mark.asyncio
  async def test_service_worker_endpoint_returns_200(self):
    """
    Given: A Baseweb instance configured as PWA
    When: Requesting GET /sw.js
    Then: Should return 200 OK with Service Worker script

    The Service Worker script should be available at /sw.js for
    registration from the root scope.
    """
    app = create_pwa_app()
    client: QuartClient = app.test_client()
    response = await client.get("/sw.js")
    assert response.status_code == 200

  @pytest.mark.asyncio
  async def test_service_worker_returns_javascript_content_type(self):
    """
    Given: A Service Worker endpoint
    When: Requesting GET /sw.js
    Then: Content-Type header should be application/javascript or text/javascript
    """
    app = create_pwa_app()
    client: QuartClient = app.test_client()
    response = await client.get("/sw.js")
    content_type = response.content_type
    # Accept both with and without charset
    assert content_type in (
      "application/javascript",
      "text/javascript",
      "application/javascript; charset=utf-8",
      "text/javascript; charset=utf-8",
    )

  @pytest.mark.asyncio
  async def test_service_worker_has_allowed_header(self):
    """
    Given: A Service Worker endpoint
    When: Requesting GET /sw.js
    Then: Response should include 'Service-Worker-Allowed: /' header

    This header allows the Service Worker to be registered from any page
    on the domain, not just from the same directory as sw.js.
    """
    app = create_pwa_app()
    client: QuartClient = app.test_client()
    response = await client.get("/sw.js")
    assert "Service-Worker-Allowed" in response.headers
    assert response.headers["Service-Worker-Allowed"] == "/"

  @pytest.mark.asyncio
  async def test_service_worker_not_available_when_not_pwa(self):
    """
    Given: A Baseweb instance configured as web (not PWA)
    When: Requesting GET /sw.js
    Then: Should return 404 Not Found

    Service Worker should only be available when APP_STYLE=pwa.
    """
    app = create_web_app()
    client: QuartClient = app.test_client()
    response = await client.get("/sw.js")
    assert response.status_code == 404


# ==============================================================================
# Service Worker Content Tests
# ==============================================================================


class TestServiceWorkerContent:
  """
  Tests verifying the Service Worker script contains required event handlers.

  Service Worker must implement:
  - install event: Cache static assets (app shell)
  - activate event: Clean up old caches
  - fetch event: Serve from cache or network
  """

  @pytest.mark.asyncio
  async def test_service_worker_contains_install_handler(self):
    """
    Given: The Service Worker script content
    When: Reading the script
    Then: Script should contain 'install' event listener

    The install handler should cache static assets (app shell)
    for offline access.
    """
    app = create_pwa_app()
    client: QuartClient = app.test_client()
    response = await client.get("/sw.js")
    content = await response.get_data(as_text=True)
    assert "addEventListener('install'" in content or 'addEventListener("install"' in content

  @pytest.mark.asyncio
  async def test_service_worker_contains_activate_handler(self):
    """
    Given: The Service Worker script content
    When: Reading the script
    Then: Script should contain 'activate' event listener

    The activate handler should clean up old cache versions
    when a new Service Worker takes control.
    """
    app = create_pwa_app()
    client: QuartClient = app.test_client()
    response = await client.get("/sw.js")
    content = await response.get_data(as_text=True)
    assert "addEventListener('activate'" in content or 'addEventListener("activate"' in content

  @pytest.mark.asyncio
  async def test_service_worker_contains_fetch_handler(self):
    """
    Given: The Service Worker script content
    When: Reading the script
    Then: Script should contain 'fetch' event listener

    The fetch handler implements the caching strategy:
    - Cache-first for static assets
    - Network-first for API calls
    """
    app = create_pwa_app()
    client: QuartClient = app.test_client()
    response = await client.get("/sw.js")
    content = await response.get_data(as_text=True)
    assert "addEventListener('fetch'" in content or 'addEventListener("fetch"' in content

  @pytest.mark.asyncio
  async def test_service_worker_skips_cache_for_api(self):
    """
    Given: The Service Worker fetch handler
    When: Reading the script
    Then: Fetch handler should skip caching for /api/ routes

    API calls should always go to the network to ensure fresh data.
    """
    app = create_pwa_app()
    client: QuartClient = app.test_client()
    response = await client.get("/sw.js")
    content = await response.get_data(as_text=True)
    assert "/api/" in content

  @pytest.mark.asyncio
  async def test_service_worker_skips_cache_for_socketio(self):
    """
    Given: The Service Worker fetch handler
    When: Reading the script
    Then: Fetch handler should skip caching for /socket.io/ routes

    WebSocket connections should never be cached.
    """
    app = create_pwa_app()
    client: QuartClient = app.test_client()
    response = await client.get("/sw.js")
    content = await response.get_data(as_text=True)
    assert "/socket.io/" in content


# ==============================================================================
# HTML Template iOS Meta Tags Tests
# ==============================================================================


class TestHTMLTemplateIOSMetaTags:
  """
  Tests verifying iOS Safari meta tags in the HTML template.

  iOS Safari requires specific meta tags for Home Screen installation:
  - apple-mobile-web-app-capable: Enable standalone mode
  - apple-mobile-web-app-status-bar-style: Status bar appearance
  - apple-mobile-web-app-title: Home Screen title
  - apple-touch-icon: Home Screen icon
  """

  @pytest.mark.asyncio
  async def test_html_contains_apple_mobile_web_app_capable(self):
    """
    Given: A Baseweb instance configured as PWA
    When: Requesting the main page (GET /)
    Then: HTML should contain apple-mobile-web-app-capable meta tag

    This meta tag tells iOS Safari to run the app in standalone mode
    (without browser UI) when launched from Home Screen.
    """
    app = create_pwa_app()
    client: QuartClient = app.test_client()
    response = await client.get("/")
    html = await response.get_data(as_text=True)
    assert "apple-mobile-web-app-capable" in html

  @pytest.mark.asyncio
  async def test_apple_mobile_web_app_capable_is_yes(self):
    """
    Given: An apple-mobile-web-app-capable meta tag
    When: Reading the content attribute
    Then: Content should be "yes"

    Only "yes" enables standalone mode. Any other value or missing tag
    will open the app in Safari browser tabs.
    """
    app = create_pwa_app()
    client: QuartClient = app.test_client()
    response = await client.get("/")
    html = await response.get_data(as_text=True)
    assert 'apple-mobile-web-app-capable" content="yes"' in html

  @pytest.mark.asyncio
  async def test_html_contains_apple_mobile_web_app_status_bar_style(self):
    """
    Given: A Baseweb instance configured as PWA
    When: Requesting the main page (GET /)
    Then: HTML should contain apple-mobile-web-app-status-bar-style meta tag

    This controls the appearance of the status bar in standalone mode:
    - default: White status bar
    - black: Black status bar
    - black-translucent: Translucent status bar (content underneath)
    """
    app = create_pwa_app()
    client: QuartClient = app.test_client()
    response = await client.get("/")
    html = await response.get_data(as_text=True)
    assert "apple-mobile-web-app-status-bar-style" in html

  @pytest.mark.asyncio
  async def test_html_contains_apple_mobile_web_app_title(self):
    """
    Given: A Baseweb instance configured as PWA
    When: Requesting the main page (GET /)
    Then: HTML should contain apple-mobile-web-app-title meta tag

    This sets the title shown under the app icon on the Home Screen.
    Should be short (ideally <= 12 characters) for best display.
    """
    app = create_pwa_app()
    client: QuartClient = app.test_client()
    response = await client.get("/")
    html = await response.get_data(as_text=True)
    assert "apple-mobile-web-app-title" in html

  @pytest.mark.asyncio
  async def test_html_contains_apple_touch_icon_link(self):
    """
    Given: A Baseweb instance configured as PWA
    When: Requesting the main page (GET /)
    Then: HTML should contain apple-touch-icon link element

    This provides the icon for iOS Home Screen.
    iOS will automatically add rounded corners and gloss effect.
    """
    app = create_pwa_app()
    client: QuartClient = app.test_client()
    response = await client.get("/")
    html = await response.get_data(as_text=True)
    assert "apple-touch-icon" in html

  @pytest.mark.asyncio
  async def test_apple_touch_icon_is_180x180(self):
    """
    Given: An apple-touch-icon link element
    When: Reading the sizes attribute
    Then: Sizes should include "180x180"

    iOS requires 180x180 for devices with @3x display (iPhone Plus, iPhone X+).
    The icon should be a square PNG without transparency for best results.
    """
    app = create_pwa_app()
    client: QuartClient = app.test_client()
    response = await client.get("/")
    html = await response.get_data(as_text=True)
    assert "180x180" in html


# ==============================================================================
# Service Worker Registration Tests
# ==============================================================================


class TestServiceWorkerRegistration:
  """
  Tests verifying Service Worker registration in the HTML template.

  Service Worker must be registered:
  - After the page loads (window.load event)
  - Only when APP_STYLE=pwa
  - With proper scope ("/")
  """

  @pytest.mark.asyncio
  async def test_html_contains_service_worker_registration(self):
    """
    Given: A Baseweb instance configured as PWA
    When: Requesting the main page (GET /)
    Then: HTML should contain Service Worker registration code

    Registration should use:
    navigator.serviceWorker.register('/sw.js', { scope: '/' })
    """
    app = create_pwa_app()
    client: QuartClient = app.test_client()
    response = await client.get("/")
    html = await response.get_data(as_text=True)
    assert "serviceWorker.register" in html

  @pytest.mark.asyncio
  async def test_service_worker_registration_on_load(self):
    """
    Given: Service Worker registration code in HTML
    When: Reading the script
    Then: Registration should be triggered on window.load event

    Registering on load ensures the Service Worker doesn't compete
    with initial page resources for bandwidth.
    """
    app = create_pwa_app()
    client: QuartClient = app.test_client()
    response = await client.get("/")
    html = await response.get_data(as_text=True)
    assert "window.addEventListener('load'" in html or 'window.addEventListener("load"' in html

  @pytest.mark.asyncio
  async def test_service_worker_registration_only_when_pwa(self):
    """
    Given: A Baseweb instance configured as web (not PWA)
    When: Requesting the main page (GET /)
    Then: HTML should NOT contain Service Worker registration code

    Service Worker should only be registered when APP_STYLE=pwa
    to avoid caching in regular web mode.
    """
    app = create_web_app()
    client: QuartClient = app.test_client()
    response = await client.get("/")
    html = await response.get_data(as_text=True)
    assert "serviceWorker.register" not in html

  @pytest.mark.asyncio
  async def test_service_worker_registration_with_scope(self):
    """
    Given: Service Worker registration code
    When: Reading the register() call
    Then: Scope should be explicitly set to "/"

    Explicit scope ensures the Service Worker controls all pages,
    not just those in the same directory as sw.js.
    """
    app = create_pwa_app()
    client: QuartClient = app.test_client()
    response = await client.get("/")
    html = await response.get_data(as_text=True)
    assert "scope: '/'" in html or 'scope: "/"' in html


# ==============================================================================
# Offline Support Tests
# ==============================================================================


class TestOfflineSupport:
  """
  Tests verifying offline functionality is properly configured.

  Offline support requires:
  - Service Worker with fetch handler
  - Cached static assets (app shell)
  - isOnline state in Vuex store
  - Offline indicator UI component
  """

  @pytest.mark.asyncio
  async def test_store_has_connection_state(self):
    """
    Given: The Vuex store template (store.js)
    When: Reading the store template
    Then: Store should define 'connection' state with 'isOnline' property

    This state tracks whether the app has network connectivity
    and can be used to show/hide offline indicators.
    """
    from pathlib import Path

    store_path = Path(__file__).parent.parent / "src" / "baseweb" / "templates" / "store.js"
    store_content = store_path.read_text()

    # Check for connection state in state definition
    assert "connection:" in store_content or "connection :" in store_content
    assert "isOnline" in store_content
    assert "navigator.onLine" in store_content

  @pytest.mark.asyncio
  async def test_store_has_set_online_mutation(self):
    """
    Given: The Vuex store template (store.js)
    When: Reading the store template
    Then: Store should define 'setOnline' mutation

    This mutation is used to update the online state when
    the browser fires online/offline events.
    """
    from pathlib import Path

    store_path = Path(__file__).parent.parent / "src" / "baseweb" / "templates" / "store.js"
    store_content = store_path.read_text()

    # Check for setOnline mutation
    assert "setOnline" in store_content

  @pytest.mark.asyncio
  async def test_store_has_is_online_getter(self):
    """
    Given: The Vuex store template (store.js)
    When: Reading the store template
    Then: Store should define 'isOnline' getter

    This getter allows components to access the online state
    via $store.getters.isOnline
    """
    from pathlib import Path

    store_path = Path(__file__).parent.parent / "src" / "baseweb" / "templates" / "store.js"
    store_content = store_path.read_text()

    # Check for isOnline getter
    assert "isOnline:" in store_content or "isOnline :" in store_content

  @pytest.mark.asyncio
  async def test_html_has_offline_badge(self):
    """
    Given: A Baseweb instance configured as PWA
    When: Requesting the main page (GET /)
    Then: HTML should contain offline indicator badge

    The offline badge shows when the app loses network connectivity.
    """
    app = create_pwa_app()
    client: QuartClient = app.test_client()
    response = await client.get("/")
    html = await response.get_data(as_text=True)

    # Check for offline badge using v-chip with wifi-off icon
    assert "mdi-wifi-off" in html
    assert "Offline" in html

  @pytest.mark.asyncio
  async def test_html_has_online_event_listener(self):
    """
    Given: A Baseweb instance configured as PWA
    When: Requesting the main page (GET /)
    Then: HTML should contain 'online' event listener setup

    The online event listener updates the store when connectivity is restored.
    """
    app = create_pwa_app()
    client: QuartClient = app.test_client()
    response = await client.get("/")
    html = await response.get_data(as_text=True)

    # Check for online event listener
    assert "addEventListener('online'" in html or 'addEventListener("online"' in html
    assert "setOnline" in html

  @pytest.mark.asyncio
  async def test_html_has_offline_event_listener(self):
    """
    Given: A Baseweb instance configured as PWA
    When: Requesting the main page (GET /)
    Then: HTML should contain 'offline' event listener setup

    The offline event listener updates the store when connectivity is lost.
    """
    app = create_pwa_app()
    client: QuartClient = app.test_client()
    response = await client.get("/")
    html = await response.get_data(as_text=True)

    # Check for offline event listener
    assert "addEventListener('offline'" in html or 'addEventListener("offline"' in html
    assert "setOnline" in html

  @pytest.mark.skip(reason="Offline badge not visible when online requires browser automation")
  async def test_offline_badge_not_visible_when_online(self):
    """
    Given: A Baseweb instance configured as PWA
    When: The app has network connectivity (isOnline = true)
    Then: Offline badge should not be visible

    This test requires browser automation to verify reactive UI state.
    """
    pytest.fail("Not implemented: offline badge not visible when online")


# ==============================================================================
# PWA Mode Conditional Tests
# ==============================================================================


class TestPWAModeConditional:
  """
  Tests verifying PWA features are conditionally enabled based on APP_STYLE.
  """

  @pytest.mark.asyncio
  async def test_manifest_not_available_when_not_pwa(self):
    """
    Given: A Baseweb instance with APP_STYLE=web
    When: Requesting GET /manifest.json
    Then: Should return 404 Not Found
    """
    app = create_web_app()
    client: QuartClient = app.test_client()
    response = await client.get("/manifest.json")
    assert response.status_code == 404

  @pytest.mark.asyncio
  async def test_ios_meta_tags_only_when_pwa(self):
    """
    Given: A Baseweb instance with APP_STYLE=web
    When: Requesting the main page (GET /)
    Then: HTML should NOT contain iOS PWA meta tags
    """
    app = create_web_app()
    client: QuartClient = app.test_client()
    response = await client.get("/")
    html = await response.get_data(as_text=True)
    assert "apple-mobile-web-app-capable" not in html
    assert "apple-mobile-web-app-status-bar-style" not in html
    assert "apple-mobile-web-app-title" not in html

  @pytest.mark.asyncio
  async def test_manifest_link_only_when_pwa(self):
    """
    Given: A Baseweb instance with APP_STYLE=web
    When: Requesting the main page (GET /)
    Then: HTML should NOT contain <link rel="manifest"> tag
    """
    app = create_web_app()
    client: QuartClient = app.test_client()
    response = await client.get("/")
    html = await response.get_data(as_text=True)
    assert '<link rel="manifest"' not in html
