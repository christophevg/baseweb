"""Configuration module for baseweb applications.

This module provides the configuration system for baseweb, using dataclasses
to define all configuration options. Configuration is loaded via Clevis,
which supports:

- Layered configuration (defaults < user-level < project-level < env vars)
- TOML file support
- Environment variable interpolation
- Type-safe dataclass population

Example:
    from baseweb.config import BasewebConfig
    from clevis import get_config

    # Load from TOML file with environment variable overrides
    config = get_config(BasewebConfig, name="baseweb")

    # Create programmatically
    config = BasewebConfig(name="myapp", title="My App")
"""

from dataclasses import dataclass, field
from pathlib import Path

# Registry for application-specific configuration
_app_configs: dict[str, type] = {}


@dataclass
class BrandingColorsConfig:
  """Branding color configuration.

  Attributes:
    scheme: Color scheme ('dark' or 'light')
    primary: Primary color as CSS color value
    primary_name: Color name for Vuetify (e.g., 'blue')
    background: Background color for the application
  """

  scheme: str = "dark"
  primary: str = "rgb(21, 101, 192)"
  primary_name: str = "blue"
  background: str = "rgb(21, 101, 192)"


@dataclass
class BrandingIconsConfig:
  """Branding icons configuration.

  Attributes:
    app: Path to application icon
    social: Path to social media image
  """

  app: str | None = None
  social: str | None = None


@dataclass
class BrandingFaviconConfig:
  """Favicon configuration.

  Attributes:
    enabled: Enable favicon generation
    safari_mask_color: Safari mask icon color
    windows_tile_color: Windows tile color
  """

  enabled: bool = False
  safari_mask_color: str | None = None
  windows_tile_color: str | None = None


@dataclass
class BrandingConfig:
  """Branding configuration.

  Contains nested configuration for colors, icons, and favicon.

  Attributes:
    colors: Color configuration
    icons: Icons configuration
    favicon: Favicon configuration
  """

  colors: BrandingColorsConfig = field(default_factory=BrandingColorsConfig)
  icons: BrandingIconsConfig = field(default_factory=BrandingIconsConfig)
  favicon: BrandingFaviconConfig = field(default_factory=BrandingFaviconConfig)


@dataclass
class FeaturesSocketIOConfig:
  """SocketIO feature configuration.

  Attributes:
    enabled: Enable WebSocket support via SocketIO
  """

  enabled: bool = True


@dataclass
class FeaturesPWAConfig:
  """Progressive Web App feature configuration.

  Attributes:
    display: Display mode ('standalone', 'fullscreen', 'minimal-ui', 'browser')
    orientation: Preferred orientation ('portrait', 'landscape', 'any')
    start_url: Start URL for PWA
    theme_color: Theme color for PWA
    background_color: Background color for PWA
    icons_dir: Directory containing PWA icons (required when style = 'pwa')
  """

  display: str = "standalone"
  orientation: str = "portrait"
  start_url: str = "/"
  theme_color: str = "rgb(21, 101, 192)"
  background_color: str = "rgb(21, 101, 192)"
  icons_dir: str | None = None


@dataclass
class FeaturesConfig:
  """Features configuration.

  Contains nested configuration for SocketIO and PWA features.

  Attributes:
    socketio: SocketIO configuration
    pwa: PWA configuration
  """

  socketio: FeaturesSocketIOConfig = field(default_factory=FeaturesSocketIOConfig)
  pwa: FeaturesPWAConfig = field(default_factory=FeaturesPWAConfig)


@dataclass
class ServerConfig:
  """Server configuration.

  This replaces GunicornConfig to have a more generic name while
  still supporting Gunicorn as the primary server.

  Attributes:
    bind: The socket to bind (e.g., '0.0.0.0:8000' or 'unix:/tmp/socket')
    workers: Number of worker processes
    worker_class: The type of workers to use (e.g., uvicorn.workers.UvicornWorker)
    timeout: Worker timeout in seconds
    keepalive: Time to wait for requests on a Keep-Alive connection
  """

  bind: str = "0.0.0.0:8000"
  workers: int = 1
  worker_class: str = "uvicorn.workers.UvicornWorker"
  timeout: int = 120
  keepalive: int = 5


@dataclass
class BasewebConfig:
  """Baseweb application configuration.

  This dataclass defines all configuration options for a baseweb application.
  Configuration can be loaded from TOML files, environment variables, or
  created programmatically.

  Configuration Priority (via Clevis):
    1. CLI arguments (highest priority)
    2. Environment variables (APP_*, GUNICORN_*)
    3. Project-level TOML (./baseweb.toml)
    4. User-level TOML (~/.baseweb.toml)
    5. Dataclass defaults (lowest priority)

  Attributes:
    app_uri: Application entry point (module:attribute format)
    name: Application name (used for Quart app name)
    title: Application title (displayed in UI)
    short_name: Short name for PWA (defaults to camelCase of name)
    author: Application author
    description: Application description
    version: Application version (optional, not currently used by baseweb)
    url: Application URL (optional)
    main_template: Path to main template file
    style: Application style ('web' or 'pwa')
    keep_alive: Enable keep-alive connections

    branding: Branding configuration (colors, icons, favicon)
    features: Features configuration (socketio, pwa)
    server: Server configuration

  Example:
      >>> config = BasewebConfig(name="myapp", title="My Application")
      >>> config.name
      'myapp'
      >>> config.server.workers
      1
      >>> config.branding.colors.scheme
      'dark'
  """

  # Application entry point (required)
  app_uri: str = "app:asgi_app"

  # Application metadata
  name: str = field(default_factory=lambda: Path.cwd().name)
  title: str = field(default_factory=lambda: Path.cwd().name)
  short_name: str | None = None
  author: str = "Unknown Author"
  description: str = "A baseweb app"
  version: str | None = None

  # URLs and paths
  url: str | None = None
  main_template: str | None = None

  # Application style
  style: str = "web"  # "web" or "pwa"

  # Connection management
  keep_alive: bool = False

  # Nested configuration sections
  branding: BrandingConfig = field(default_factory=BrandingConfig)
  features: FeaturesConfig = field(default_factory=FeaturesConfig)
  server: ServerConfig = field(default_factory=ServerConfig)

  # Flattened access properties for template compatibility
  # These provide convenient access to nested config values

  @property
  def icon(self) -> str | None:
    """Flattened access to branding.icons.app."""
    return self.branding.icons.app

  @property
  def social_image(self) -> str | None:
    """Flattened access to branding.icons.social."""
    return self.branding.icons.social

  @property
  def favicon_support(self) -> bool:
    """Flattened access to branding.favicon.enabled."""
    return self.branding.favicon.enabled

  @property
  def favicon_mask_icon_color(self) -> str | None:
    """Flattened access to branding.favicon.safari_mask_color."""
    return self.branding.favicon.safari_mask_color

  @property
  def favicon_msapp_tile_color(self) -> str | None:
    """Flattened access to branding.favicon.windows_tile_color."""
    return self.branding.favicon.windows_tile_color

  @property
  def color(self) -> str:
    """Flattened access to branding.colors.primary."""
    return self.branding.colors.primary

  @property
  def color_name(self) -> str:
    """Flattened access to branding.colors.primary_name."""
    return self.branding.colors.primary_name

  @property
  def color_scheme(self) -> str:
    """Flattened access to branding.colors.scheme."""
    return self.branding.colors.scheme

  @property
  def socketio(self) -> bool:
    """Flattened access to features.socketio.enabled."""
    return self.features.socketio.enabled

  def toDict(self) -> dict:
    """Convert config to dictionary for template serialization.

    Returns:
      Dictionary representation of the config
    """
    return {
      "name": self.name,
      "title": self.title,
      "short_name": self.short_name,
      "author": self.author,
      "description": self.description,
      "version": self.version,
      "url": self.url,
      "main_template": self.main_template,
      "style": self.style,
      "keep_alive": self.keep_alive,
      "icon": self.icon,
      "social_image": self.social_image,
      "favicon_support": self.favicon_support,
      "favicon_mask_icon_color": self.favicon_mask_icon_color,
      "favicon_msapp_tile_color": self.favicon_msapp_tile_color,
      "color": self.color,
      "color_name": self.color_name,
      "color_scheme": self.color_scheme,
      "socketio": self.socketio,
      "branding": {
        "colors": {
          "scheme": self.branding.colors.scheme,
          "primary": self.branding.colors.primary,
          "primary_name": self.branding.colors.primary_name,
          "background": self.branding.colors.background,
        },
        "icons": {
          "app": self.branding.icons.app,
          "social": self.branding.icons.social,
        },
        "favicon": {
          "enabled": self.branding.favicon.enabled,
          "safari_mask_color": self.branding.favicon.safari_mask_color,
          "windows_tile_color": self.branding.favicon.windows_tile_color,
        },
      },
      "features": {
        "socketio": {
          "enabled": self.features.socketio.enabled,
        },
        "pwa": {
          "display": self.features.pwa.display,
          "orientation": self.features.pwa.orientation,
          "start_url": self.features.pwa.start_url,
          "theme_color": self.features.pwa.theme_color,
          "background_color": self.features.pwa.background_color,
          "icons_dir": self.features.pwa.icons_dir,
        },
      },
      "server": {
        "bind": self.server.bind,
        "workers": self.server.workers,
        "worker_class": self.server.worker_class,
        "timeout": self.server.timeout,
        "keepalive": self.server.keepalive,
      },
    }


def register_app_config(name: str, config_class: type) -> None:
  """Register application-specific configuration.

  Applications can register custom configuration sections that will be
  available under the 'app.{name}' namespace in TOML files and accessible
  as attributes on the config object.

  Args:
    name: Configuration section name (will be accessible as app.{name})
    config_class: Dataclass type for the configuration

  Example:
      >>> from dataclasses import dataclass
      >>> @dataclass
      ... class MyAppConfig:
      ...     debug: bool = False
      ...     custom_setting: str = "default"
      >>> register_app_config("myapp", MyAppConfig)

      In baseweb.toml:
      [app.myapp]
      debug = true
      custom_setting = "custom value"

  Note:
    Configuration will be available in:
      - TOML: [app.{name}] section
      - Environment: APP_{NAME}_* variables (uppercase)
      - Config object: config.app.{name}
  """
  _app_configs[name] = config_class


def get_registered_configs() -> dict[str, type]:
  """Get all registered application-specific configurations.

  Returns:
    Dictionary mapping configuration names to their dataclass types
  """
  return _app_configs.copy()
