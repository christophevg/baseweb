"""Tests for baseweb configuration module."""

from dataclasses import dataclass, field
from pathlib import Path
from unittest.mock import patch

from baseweb.config import (
  BasewebConfig,
  ServerConfig,
  get_registered_configs,
  register_app_config,
)

# ==============================================================================
# ServerConfig Tests
# ==============================================================================


class TestServerConfig:
  """Tests for ServerConfig dataclass."""

  def test_default_values(self):
    """
    Given: A new ServerConfig instance
    When: Creating with no arguments
    Then: All default values should be set correctly
    """
    config = ServerConfig()

    assert config.bind == "0.0.0.0:8000"
    assert config.workers == 1
    assert config.worker_class == "uvicorn.workers.UvicornWorker"
    assert config.timeout == 120
    assert config.keepalive == 5

  def test_custom_values(self):
    """
    Given: Custom configuration values
    When: Creating ServerConfig with custom values
    Then: All custom values should be set
    """
    config = ServerConfig(
      bind="127.0.0.1:9000",
      workers=4,
      worker_class="sync",
      timeout=60,
      keepalive=10,
    )

    assert config.bind == "127.0.0.1:9000"
    assert config.workers == 4
    assert config.worker_class == "sync"
    assert config.timeout == 60
    assert config.keepalive == 10

  def test_bind_variations(self):
    """
    Given: Different bind address formats
    When: Setting bind parameter
    Then: Should accept various formats
    """
    # IP and port
    config1 = ServerConfig(bind="192.168.1.1:8080")
    assert config1.bind == "192.168.1.1:8080"

    # Unix socket
    config2 = ServerConfig(bind="unix:/tmp/gunicorn.sock")
    assert config2.bind == "unix:/tmp/gunicorn.sock"

    # All interfaces
    config3 = ServerConfig(bind="0.0.0.0:8000")
    assert config3.bind == "0.0.0.0:8000"


# ==============================================================================
# BasewebConfig Tests
# ==============================================================================


class TestBasewebConfig:
  """Tests for BasewebConfig dataclass."""

  def test_default_values(self, tmp_path):
    """
    Given: A new BasewebConfig instance
    When: Creating with no arguments
    Then: All default values should be set correctly
    """
    with patch.object(Path, "cwd", return_value=tmp_path):
      config = BasewebConfig()

      # Application identification
      assert config.name == tmp_path.name
      assert config.title == tmp_path.name
      assert config.author == "Unknown Author"
      assert config.description == "A baseweb app"
      assert config.version is None

      # URLs and paths
      assert config.url is None
      assert config.main_template is None

      # Visual settings
      assert config.short_name is None
      assert config.branding.colors.scheme == "dark"
      assert config.branding.colors.primary == "rgb(21, 101, 192)"
      assert config.branding.colors.primary_name == "blue"
      assert config.branding.colors.background == "rgb(21, 101, 192)"
      assert config.branding.icons.app is None
      assert config.branding.icons.social is None

      # Application type
      assert config.style == "web"

      # Features
      assert config.features.socketio.enabled is True
      assert config.branding.favicon.enabled is False
      assert config.branding.favicon.safari_mask_color is None
      assert config.branding.favicon.windows_tile_color is None
      assert config.keep_alive is False

      # Server configuration
      assert isinstance(config.server, ServerConfig)
      assert config.server.bind == "0.0.0.0:8000"

      # Entry point
      assert config.app_uri == "app:asgi_app"

  def test_custom_values(self):
    """
    Given: Custom configuration values
    When: Creating BasewebConfig with custom values
    Then: All custom values should be set
    """
    from baseweb.config import (
      BrandingColorsConfig,
      BrandingConfig,
      BrandingFaviconConfig,
      BrandingIconsConfig,
      FeaturesConfig,
      FeaturesSocketIOConfig,
    )

    config = BasewebConfig(
      name="myapp",
      title="My Application",
      author="Test Author",
      description="Test description",
      version="1.0.0",
      url="https://example.com",
      main_template="custom.html",
      short_name="MyApp",
      branding=BrandingConfig(
        colors=BrandingColorsConfig(
          scheme="light",
          primary="rgb(255, 0, 0)",
          primary_name="red",
          background="rgb(255, 255, 255)",
        ),
        icons=BrandingIconsConfig(
          app="icon.png",
          social="social.png",
        ),
        favicon=BrandingFaviconConfig(
          enabled=True,
          safari_mask_color="rgb(0, 0, 0)",
          windows_tile_color="rgb(0, 0, 0)",
        ),
      ),
      style="pwa",
      features=FeaturesConfig(
        socketio=FeaturesSocketIOConfig(enabled=False),
      ),
      keep_alive=True,
      app_uri="main:app",
    )

    assert config.name == "myapp"
    assert config.title == "My Application"
    assert config.author == "Test Author"
    assert config.description == "Test description"
    assert config.version == "1.0.0"
    assert config.url == "https://example.com"
    assert config.main_template == "custom.html"
    assert config.short_name == "MyApp"
    assert config.branding.colors.scheme == "light"
    assert config.branding.colors.primary == "rgb(255, 0, 0)"
    assert config.branding.colors.primary_name == "red"
    assert config.branding.colors.background == "rgb(255, 255, 255)"
    assert config.branding.icons.app == "icon.png"
    assert config.branding.icons.social == "social.png"
    assert config.style == "pwa"
    assert config.features.socketio.enabled is False
    assert config.branding.favicon.enabled is True
    assert config.branding.favicon.safari_mask_color == "rgb(0, 0, 0)"
    assert config.branding.favicon.windows_tile_color == "rgb(0, 0, 0)"
    assert config.keep_alive is True
    assert config.app_uri == "main:app"

  def test_nested_gunicorn_config(self):
    """
    Given: A BasewebConfig with custom ServerConfig
    When: Setting nested server values
    Then: ServerConfig should be properly configured
    """
    server = ServerConfig(
      bind="0.0.0.0:9000",
      workers=4,
    )
    config = BasewebConfig(server=server)

    assert config.server.bind == "0.0.0.0:9000"
    assert config.server.workers == 4

  def test_boolean_features(self):
    """
    Given: Various boolean feature settings
    When: Creating config with boolean values
    Then: Boolean values should be set correctly
    """
    from baseweb.config import FeaturesConfig, FeaturesSocketIOConfig

    config1 = BasewebConfig(features=FeaturesConfig(socketio=FeaturesSocketIOConfig(enabled=True)))
    assert config1.features.socketio.enabled is True

    config2 = BasewebConfig(features=FeaturesConfig(socketio=FeaturesSocketIOConfig(enabled=False)))
    assert config2.features.socketio.enabled is False

    from baseweb.config import BrandingConfig, BrandingFaviconConfig

    config3 = BasewebConfig(branding=BrandingConfig(favicon=BrandingFaviconConfig(enabled=True)))
    assert config3.branding.favicon.enabled is True

    config4 = BasewebConfig(keep_alive=True)
    assert config4.keep_alive is True


# ==============================================================================
# register_app_config Tests
# ==============================================================================


class TestRegisterAppConfig:
  """Tests for application-specific configuration registration."""

  def test_register_simple_config(self):
    """
    Given: A simple configuration dataclass
    When: Registering it with register_app_config
    Then: It should be available in the registry
    """

    @dataclass
    class SimpleConfig:
      debug: bool = False

    register_app_config("simple", SimpleConfig)
    configs = get_registered_configs()

    assert "simple" in configs
    assert configs["simple"] == SimpleConfig

  def test_register_nested_config(self):
    """
    Given: A configuration dataclass with nested fields
    When: Registering it with register_app_config
    Then: It should be available in the registry
    """

    @dataclass
    class DatabaseConfig:
      host: str = "localhost"
      port: int = 5432

    @dataclass
    class MyAppConfig:
      debug: bool = False
      database: DatabaseConfig = field(default_factory=DatabaseConfig)

    register_app_config("myapp", MyAppConfig)
    configs = get_registered_configs()

    assert "myapp" in configs
    assert configs["myapp"] == MyAppConfig

  def test_register_multiple_configs(self):
    """
    Given: Multiple configuration dataclasses
    When: Registering them with different names
    Then: All should be available in the registry
    """

    @dataclass
    class Config1:
      value: int = 1

    @dataclass
    class Config2:
      value: str = "test"

    register_app_config("config1", Config1)
    register_app_config("config2", Config2)
    configs = get_registered_configs()

    assert "config1" in configs
    assert "config2" in configs
    assert configs["config1"] == Config1
    assert configs["config2"] == Config2

  def test_overwrite_existing_config(self):
    """
    Given: A registered configuration
    When: Registering another config with the same name
    Then: The new config should replace the old one
    """

    @dataclass
    class OldConfig:
      value: int = 1

    @dataclass
    class NewConfig:
      value: str = "new"

    register_app_config("overwrite", OldConfig)
    register_app_config("overwrite", NewConfig)
    configs = get_registered_configs()

    assert configs["overwrite"] == NewConfig
    assert configs["overwrite"] != OldConfig


# ==============================================================================
# get_registered_configs Tests
# ==============================================================================


class TestGetRegisteredConfigs:
  """Tests for getting registered configurations."""

  def test_returns_copy_of_registry(self):
    """
    Given: Registered configurations
    When: Calling get_registered_configs
    Then: Should return a copy, not the original dict
    """

    @dataclass
    class TestConfig:
      value: int = 1

    register_app_config("test_copy", TestConfig)
    configs1 = get_registered_configs()
    configs2 = get_registered_configs()

    # Modify one copy
    configs1["new_key"] = "new_value"

    # Other copy should not be affected
    assert "new_key" not in configs2

  def test_empty_registry_initially(self):
    """
    Given: Fresh module import
    When: Calling get_registered_configs before any registrations
    Then: Should return a dict (may contain previous test registrations)
    """
    configs = get_registered_configs()
    assert isinstance(configs, dict)


# ==============================================================================
# Integration Tests
# ==============================================================================


class TestConfigIntegration:
  """Integration tests for configuration system."""

  def test_config_immutability(self):
    """
    Given: A BasewebConfig instance
    When: Modifying nested gunicorn config
    Then: Changes should be reflected
    Note: dataclasses are mutable by default
    """
    config = BasewebConfig()
    config.server.workers = 4

    assert config.server.workers == 4

  def test_config_equality(self):
    """
    Given: Two BasewebConfig instances with same values
    When: Comparing them
    Then: They should be equal
    """
    config1 = BasewebConfig(name="test", title="Test")
    config2 = BasewebConfig(name="test", title="Test")

    assert config1 == config2

  def test_config_inequality(self):
    """
    Given: Two BasewebConfig instances with different values
    When: Comparing them
    Then: They should not be equal
    """
    config1 = BasewebConfig(name="test1")
    config2 = BasewebConfig(name="test2")

    assert config1 != config2

  def test_config_repr(self):
    """
    Given: A BasewebConfig instance
    When: Converting to string representation
    Then: Should contain field names and values
    """
    config = BasewebConfig(name="myapp")
    repr_str = repr(config)

    assert "myapp" in repr_str
    assert "BasewebConfig" in repr_str
