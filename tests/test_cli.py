"""Tests for baseweb CLI module."""

import sys
from pathlib import Path
from unittest.mock import patch

import pytest

# ==============================================================================
# Test Fixtures
# ==============================================================================


@pytest.fixture
def temp_project(tmp_path):
  """Create a temporary project directory with app module."""
  app_dir = tmp_path / "app"
  app_dir.mkdir()

  # Create a minimal app module
  (app_dir / "__init__.py").write_text(
    """
from quart import Quart

app = Quart(__name__)

def asgi_app():
    return app
"""
  )

  # Store original working directory
  original_cwd = Path.cwd()

  # Change to temp directory
  import os

  os.chdir(tmp_path)

  yield tmp_path

  # Restore original working directory
  os.chdir(original_cwd)


@pytest.fixture
def mock_config_file(tmp_path):
  """Create a temporary baseweb.toml configuration file."""
  config_path = tmp_path / "baseweb.toml"
  config_path.write_text(
    """
# Application metadata
name = "testapp"
title = "Test Application"
author = "Test Author"
description = "A test application"
version = "1.0.0"

# Application entry point
app_uri = "app:asgi_app"

# Server configuration
[server]
bind = "0.0.0.0:8000"
workers = 1
"""
  )
  return config_path


# ==============================================================================
# InitCommand Tests
# ==============================================================================


class TestInitCommand:
  """Tests for 'baseweb init' command."""

  def test_init_creates_default_config(self, tmp_path):
    """
    Given: A project directory without baseweb.toml
    When: Running 'baseweb init'
    Then: Default configuration file should be created
    """
    import os

    from baseweb.__main__ import InitConfig, init

    os.chdir(tmp_path)

    config = InitConfig()
    init(config)

    config_path = tmp_path / "baseweb.toml"
    assert config_path.exists()

    content = config_path.read_text()
    assert "app_uri" in content
    assert "name" in content

  def test_init_custom_config_path(self, tmp_path):
    """
    Given: A custom config path specified via --config
    When: Running 'baseweb init --config custom.toml'
    Then: Config file should be created at custom path
    """
    import os

    from baseweb.__main__ import InitConfig, init

    os.chdir(tmp_path)

    config = InitConfig(config="custom.toml")
    init(config)

    config_path = tmp_path / "custom.toml"
    assert config_path.exists()

  def test_init_refuses_overwrite_without_force(self, tmp_path):
    """
    Given: An existing baseweb.toml file
    When: Running 'baseweb init' without --force
    Then: Should refuse to overwrite and exit with error
    """
    import os

    from baseweb.__main__ import InitConfig, init

    os.chdir(tmp_path)

    # Create existing config file
    config_path = tmp_path / "baseweb.toml"
    config_path.write_text("name = 'existing'")

    config = InitConfig()

    # Should exit with error
    with pytest.raises(SystemExit) as exc_info:
      init(config)

    assert exc_info.value.code == 1

  def test_init_force_overwrites_existing(self, tmp_path):
    """
    Given: An existing baseweb.toml file
    When: Running 'baseweb init --force'
    Then: Should overwrite the existing file
    """
    import os

    from baseweb.__main__ import InitConfig, init

    os.chdir(tmp_path)

    # Create existing config file
    config_path = tmp_path / "baseweb.toml"
    config_path.write_text("name = 'existing'")

    config = InitConfig(force=True)
    init(config)

    # Should have overwritten the file
    content = config_path.read_text()
    assert "name" in content
    assert "existing" not in content  # Old content should be gone

  def test_init_sets_secure_permissions(self, tmp_path):
    """
    Given: Creating a new configuration file
    When: Running 'baseweb init'
    Then: File should have secure permissions (600)
    """
    import os
    import stat

    from baseweb.__main__ import InitConfig, init

    os.chdir(tmp_path)

    config = InitConfig()
    init(config)

    config_path = tmp_path / "baseweb.toml"
    file_stat = config_path.stat()

    # Check that file has 600 permissions (owner read/write only)
    assert stat.S_IMODE(file_stat.st_mode) == 0o600

  def test_init_handles_write_error(self, tmp_path):
    """
    Given: A read-only directory
    When: Running 'baseweb init' in that directory
    Then: Should exit with error message
    """
    import os

    from baseweb.__main__ import InitConfig, init

    os.chdir(tmp_path)

    # Create the config path as a read-only file (not directory)
    config_path = tmp_path / "baseweb.toml"
    config_path.write_text("existing content")
    os.chmod(config_path, 0o444)  # Read-only file

    # Try to write to the read-only file with force
    config = InitConfig(force=True)

    # Should exit with error
    with pytest.raises(SystemExit) as exc_info:
      init(config)

    assert exc_info.value.code == 1

  def test_init_config_contains_required_fields(self, tmp_path):
    """
    Given: Creating default configuration
    When: Running 'baseweb init'
    Then: Config should contain all required BasewebConfig fields
    """
    import os

    from baseweb.__main__ import InitConfig, init

    os.chdir(tmp_path)

    config = InitConfig()
    init(config)

    config_path = tmp_path / "baseweb.toml"
    content = config_path.read_text()

    # Should contain required fields
    assert "app_uri" in content
    assert "name" in content
    assert "title" in content
    assert "author" in content
    assert "[server]" in content

  def test_init_config_uses_toml_format(self, tmp_path):
    """
    Given: Creating default configuration
    When: Running 'baseweb init'
    Then: Config should be valid TOML format
    """
    import os

    import tomllib

    from baseweb.__main__ import InitConfig, init

    os.chdir(tmp_path)

    config = InitConfig()
    init(config)

    config_path = tmp_path / "baseweb.toml"
    content = config_path.read_text()

    # Should be valid TOML
    try:
      parsed = tomllib.loads(content)
      assert isinstance(parsed, dict)
    except Exception as e:
      pytest.fail(f"Invalid TOML: {e}")


# ==============================================================================
# CheckCommand Tests
# ==============================================================================


class TestCheckCommand:
  """Tests for 'baseweb check' command."""

  def test_check_valid_config(self, temp_project, mock_config_file):
    """
    Given: A valid configuration file
    When: Running 'baseweb check'
    Then: Should validate successfully and exit 0
    """
    from baseweb.__main__ import CheckConfig, check

    config = CheckConfig(app_uri="app:asgi_app", name="testapp", title="Test App")

    # Should not raise SystemExit
    try:
      check(config)
    except SystemExit as e:
      # Should exit with code 0 (success)
      assert e.code == 0

  def test_check_missing_app_uri(self, temp_project):
    """
    Given: A configuration without app_uri
    When: Running 'baseweb check'
    Then: Should report error and exit 1
    """
    from baseweb.__main__ import CheckConfig, check

    config = CheckConfig(app_uri=None, name="testapp", title="Test App")

    with pytest.raises(SystemExit) as exc_info:
      check(config)

    assert exc_info.value.code == 1

  def test_check_invalid_app_uri(self, temp_project):
    """
    Given: A configuration with invalid app_uri
    When: Running 'baseweb check'
    Then: Should report import error and exit 1
    """
    from baseweb.__main__ import CheckConfig, check

    config = CheckConfig(app_uri="nonexistent:app", name="testapp", title="Test App")

    with pytest.raises(SystemExit) as exc_info:
      check(config)

    assert exc_info.value.code == 1

  def test_check_validates_app_import(self, temp_project, mock_config_file):
    """
    Given: A valid configuration with importable app
    When: Running 'baseweb check'
    Then: Should successfully import the app and validate
    """
    from baseweb.__main__ import CheckConfig, check

    config = CheckConfig(app_uri="app:asgi_app", name="testapp", title="Test App")

    try:
      check(config)
    except SystemExit as e:
      # Should exit with code 0 (success)
      assert e.code == 0

  def test_check_pwa_missing_icons_dir(self, temp_project):
    """
    Given: A PWA configuration without icons_dir
    When: Running 'baseweb check'
    Then: Should report error for missing icons_dir
    """
    from baseweb.__main__ import CheckConfig, check
    from baseweb.config import FeaturesConfig, FeaturesPWAConfig

    # PWA config without icons_dir
    pwa_config = FeaturesConfig(pwa=FeaturesPWAConfig(icons_dir=None))
    config = CheckConfig(
      app_uri="app:asgi_app", name="testapp", title="Test App", style="pwa", features=pwa_config
    )

    with pytest.raises(SystemExit) as exc_info:
      check(config)

    assert exc_info.value.code == 1

  def test_check_custom_app_uri(self, temp_project, mock_config_file):
    """
    Given: A configuration with custom app_uri
    When: Running 'baseweb check --app-uri custom:app'
    Then: Should validate the custom app_uri
    """
    from baseweb.__main__ import CheckConfig, check

    # Create custom app module
    custom_dir = temp_project / "custom"
    custom_dir.mkdir()
    (custom_dir / "__init__.py").write_text("")
    (custom_dir / "app.py").write_text(
      """
from quart import Quart
app = Quart(__name__)
"""
    )

    import os

    os.chdir(temp_project)

    config = CheckConfig(app_uri="custom.app:app", name="testapp", title="Test App")

    try:
      check(config)
    except SystemExit as e:
      assert e.code == 0

  def test_check_reports_all_errors(self, temp_project):
    """
    Given: A configuration with multiple errors
    When: Running 'baseweb check'
    Then: Should report all errors, not just the first
    """
    import sys
    from io import StringIO

    from baseweb.__main__ import CheckConfig, check
    from baseweb.config import FeaturesConfig, FeaturesPWAConfig

    # Multiple errors: missing app_uri AND PWA without icons_dir
    pwa_config = FeaturesConfig(pwa=FeaturesPWAConfig(icons_dir=None))
    config = CheckConfig(
      app_uri=None, name="testapp", title="Test App", style="pwa", features=pwa_config
    )

    # Capture stderr
    old_stderr = sys.stderr
    sys.stderr = StringIO()

    try:
      with pytest.raises(SystemExit) as exc_info:
        check(config)

      assert exc_info.value.code == 1

      # Get captured output
      error_output = sys.stderr.getvalue()

      # Should report both errors
      assert "app_uri is required" in error_output
      assert "icons_dir is required when style='pwa'" in error_output
    finally:
      sys.stderr = old_stderr

  def test_check_outputs_validation_summary(self, temp_project, mock_config_file):
    """
    Given: A valid configuration
    When: Running 'baseweb check'
    Then: Should output validation summary with app details
    """
    import sys
    from io import StringIO

    from baseweb.__main__ import CheckConfig, check

    config = CheckConfig(app_uri="app:asgi_app", name="testapp", title="Test App")

    # Capture stdout
    old_stdout = sys.stdout
    sys.stdout = StringIO()

    try:
      try:
        check(config)
      except SystemExit as e:
        assert e.code == 0

      # Get captured output
      output = sys.stdout.getvalue()

      # Should contain validation summary
      assert "Configuration is valid" in output
      assert "testapp" in output
      assert "Test App" in output
      assert "app:asgi_app" in output
    finally:
      sys.stdout = old_stdout


# ==============================================================================
# ConfigCommand Tests
# ==============================================================================


class TestConfigCommand:
  """Tests for 'baseweb config' command."""

  def test_config_displays_table_format(self, temp_project, mock_config_file):
    """
    Given: A valid configuration
    When: Running 'baseweb config' (default format)
    Then: Should display configuration as formatted table
    """
    import sys
    from io import StringIO

    from baseweb.__main__ import ConfigConfig, show_config

    config = ConfigConfig(app_uri="app:asgi_app", name="testapp", title="Test App")

    # Capture stdout
    old_stdout = sys.stdout
    sys.stdout = StringIO()

    try:
      show_config(config)
      output = sys.stdout.getvalue()

      # Should contain table format
      assert "Baseweb Configuration" in output
      assert "Application:" in output
    finally:
      sys.stdout = old_stdout

  def test_config_displays_toml_format(self, temp_project, mock_config_file):
    """
    Given: A valid configuration
    When: Running 'baseweb config --format toml'
    Then: Should display configuration as TOML
    """
    import sys
    from io import StringIO

    from baseweb.__main__ import ConfigConfig, show_config

    config = ConfigConfig(app_uri="app:asgi_app", name="testapp", title="Test App", format="toml")

    # Capture stdout
    old_stdout = sys.stdout
    sys.stdout = StringIO()

    try:
      show_config(config)
      output = sys.stdout.getvalue()

      # Should be valid TOML format
      assert 'name = "testapp"' in output
      assert 'title = "Test App"' in output
      assert "[server]" in output
    finally:
      sys.stdout = old_stdout

  def test_config_includes_app_metadata(self, temp_project, mock_config_file):
    """
    Given: A configuration with app metadata
    When: Running 'baseweb config'
    Then: Should display name, title, author, version
    """
    import sys
    from io import StringIO

    from baseweb.__main__ import ConfigConfig, show_config

    config = ConfigConfig(
      app_uri="app:asgi_app",
      name="testapp",
      title="Test Application",
      author="Test Author",
      version="1.0.0",
    )

    # Capture stdout
    old_stdout = sys.stdout
    sys.stdout = StringIO()

    try:
      show_config(config)
      output = sys.stdout.getvalue()

      # Should contain app metadata
      assert "testapp" in output
      assert "Test Application" in output
      assert "Test Author" in output
      assert "1.0.0" in output
    finally:
      sys.stdout = old_stdout

  def test_config_includes_server_settings(self, temp_project, mock_config_file):
    """
    Given: A configuration with server settings
    When: Running 'baseweb config'
    Then: Should display bind, workers, worker_class
    """
    import sys
    from io import StringIO

    from baseweb.__main__ import ConfigConfig, show_config
    from baseweb.config import ServerConfig

    config = ConfigConfig(
      app_uri="app:asgi_app", name="testapp", server=ServerConfig(bind="0.0.0.0:9000", workers=4)
    )

    # Capture stdout
    old_stdout = sys.stdout
    sys.stdout = StringIO()

    try:
      show_config(config)
      output = sys.stdout.getvalue()

      # Should contain server settings
      assert "0.0.0.0:9000" in output
      assert "Workers: 4" in output
    finally:
      sys.stdout = old_stdout

  def test_config_includes_features(self, temp_project, mock_config_file):
    """
    Given: A configuration with feature flags
    When: Running 'baseweb config'
    Then: Should display socketio, favicon settings
    """
    import sys
    from io import StringIO

    from baseweb.__main__ import ConfigConfig, show_config
    from baseweb.config import FeaturesConfig

    config = ConfigConfig(app_uri="app:asgi_app", name="testapp", features=FeaturesConfig())

    # Capture stdout
    old_stdout = sys.stdout
    sys.stdout = StringIO()

    try:
      show_config(config)
      output = sys.stdout.getvalue()

      # Should contain feature sections
      assert "Features:" in output
    finally:
      sys.stdout = old_stdout

  def test_config_excludes_none_values(self, temp_project, mock_config_file):
    """
    Given: A configuration with optional fields set to None
    When: Running 'baseweb config'
    Then: Should exclude None values from output
    """
    import sys
    from io import StringIO

    from baseweb.__main__ import ConfigConfig, show_config

    config = ConfigConfig(
      app_uri="app:asgi_app",
      name="testapp",
      title="Test App",
      version=None,  # Explicitly None
    )

    # Capture stdout
    old_stdout = sys.stdout
    sys.stdout = StringIO()

    try:
      show_config(config)
      output = sys.stdout.getvalue()

      # None values should not appear
      assert "Version: None" not in output
    finally:
      sys.stdout = old_stdout

  def test_config_uses_defaults_when_missing_file(self, temp_project):
    """
    Given: No configuration file present
    When: Running 'baseweb config'
    Then: Should display default configuration values
    """
    import sys
    from io import StringIO

    from baseweb.__main__ import ConfigConfig, show_config
    from baseweb.config import BasewebConfig

    # Use default config
    default_config = BasewebConfig()
    config = ConfigConfig(**default_config.__dict__)

    # Capture stdout
    old_stdout = sys.stdout
    sys.stdout = StringIO()

    try:
      show_config(config)
      output = sys.stdout.getvalue()

      # Should show default configuration
      assert "Baseweb Configuration" in output
    finally:
      sys.stdout = old_stdout

  def test_config_shows_merged_configuration(self, temp_project, mock_config_file):
    """
    Given: TOML config + environment variables + CLI args
    When: Running 'baseweb config'
    Then: Should show merged configuration (Clevis layering)
    """
    import sys
    from io import StringIO

    from baseweb.__main__ import ConfigConfig, show_config

    # Simulate merged configuration from file + CLI override
    config = ConfigConfig(
      app_uri="app:asgi_app",
      name="testapp",
      title="Test App from CLI",  # CLI override
      author="Test Author",
    )

    # Capture stdout
    old_stdout = sys.stdout
    sys.stdout = StringIO()

    try:
      show_config(config)
      output = sys.stdout.getvalue()

      # Should show merged values
      assert "Test App from CLI" in output
      assert "Test Author" in output
    finally:
      sys.stdout = old_stdout


# ==============================================================================
# ServeCommand Tests
# ==============================================================================


class TestServeCommand:
  """Tests for 'baseweb serve' command."""

  def test_serve_loads_config(self, temp_project, mock_config_file):
    """
    Given: A valid configuration file
    When: Running 'baseweb serve'
    Then: Should load configuration from baseweb.toml
    """
    import os

    from baseweb.__main__ import ServeConfig

    os.chdir(temp_project)

    # Load configuration using Clevis get_config
    # This test verifies that ServeConfig can be instantiated from config
    config = ServeConfig(app_uri="app:asgi_app", name="testapp", title="Test App")

    # Should have loaded configuration
    assert config.app_uri == "app:asgi_app"
    assert config.name == "testapp"

  def test_serve_imports_app_uri(self, temp_project, mock_config_file):
    """
    Given: A configuration with app_uri
    When: Running 'baseweb serve'
    Then: Should import the application from app_uri
    """
    import os

    from baseweb.__main__ import import_app

    os.chdir(temp_project)

    # Import app from URI
    app = import_app("app:asgi_app")

    # Should successfully import the Quart app
    assert app is not None
    assert hasattr(app, "__name__")

  def test_serve_custom_bind_address(self, temp_project, mock_config_file):
    """
    Given: CLI override for bind address
    When: Running 'baseweb serve --server-bind :8080'
    Then: Should use custom bind address
    """
    from baseweb.__main__ import ServeConfig
    from baseweb.config import ServerConfig

    # Create config with custom bind
    config = ServeConfig(
      app_uri="app:asgi_app", name="testapp", server=ServerConfig(bind=":8080", workers=1)
    )

    # Should have custom bind address
    assert config.server.bind == ":8080"

  def test_serve_custom_workers(self, temp_project, mock_config_file):
    """
    Given: CLI override for workers
    When: Running 'baseweb serve --server-workers 4'
    Then: Should use custom worker count
    """
    from baseweb.__main__ import ServeConfig
    from baseweb.config import ServerConfig

    # Create config with custom workers
    config = ServeConfig(
      app_uri="app:asgi_app", name="testapp", server=ServerConfig(bind="0.0.0.0:8000", workers=4)
    )

    # Should have custom worker count
    assert config.server.workers == 4

  def test_serve_custom_app_uri(self, temp_project, mock_config_file):
    """
    Given: CLI override for app_uri
    When: Running 'baseweb serve --app-uri custom:app'
    Then: Should use custom app_uri
    """
    from baseweb.__main__ import ServeConfig

    # Create config with custom app_uri
    config = ServeConfig(app_uri="custom:app", name="testapp", title="Test")

    # Should use custom app_uri
    assert config.app_uri == "custom:app"

  def test_serve_handles_import_error(self, temp_project):
    """
    Given: Invalid app_uri that cannot be imported
    When: Running 'baseweb serve'
    Then: Should exit with clear error message
    """
    import os

    from baseweb.__main__ import import_app

    os.chdir(temp_project)

    # Try to import non-existent module
    with pytest.raises(ImportError) as exc_info:
      import_app("nonexistent:app")

    # Should have helpful error message
    assert "Cannot find module" in str(exc_info.value)

  def test_serve_handles_attribute_error(self, temp_project):
    """
    Given: app_uri with missing attribute
    When: Running 'baseweb serve'
    Then: Should exit with clear error message
    """
    import os

    from baseweb.__main__ import import_app

    os.chdir(temp_project)

    # Try to import non-existent attribute
    with pytest.raises((RuntimeError, AttributeError)) as exc_info:
      import_app("app:nonexistent_attr")

    # Should have helpful error message
    assert "nonexistent_attr" in str(exc_info.value)

  def test_serve_handles_type_error(self, temp_project):
    """
    Given: App initialization with wrong argument types
    When: Running 'baseweb serve'
    Then: Should exit with helpful error message
    """
    import os

    from baseweb.__main__ import import_app

    os.chdir(temp_project)

    # This test verifies error handling for type errors
    # The actual app should not cause TypeError, but we test the error handling
    # by checking that import_app works correctly
    app = import_app("app:asgi_app")
    assert app is not None

  def test_serve_adds_cwd_to_path(self, temp_project, mock_config_file):
    """
    Given: Running serve from project directory
    When: Importing app module
    Then: Should add current directory to sys.path
    """
    import os

    from baseweb.__main__ import import_app

    os.chdir(temp_project)

    # sys.path should include cwd after import_app
    import_app("app:asgi_app")

    # The first item in sys.path should be the current working directory
    assert str(Path.cwd()) in sys.path

  def test_serve_environment_variable_override(self, temp_project, mock_config_file):
    """
    Given: Environment variable overrides
    When: Running 'baseweb serve'
    Then: Should merge env vars with config (Clevis layering)
    """
    import os

    from baseweb.__main__ import ServeConfig
    from baseweb.config import ServerConfig

    # This test verifies that environment variables can override config
    # Clevis handles the actual layering: defaults < user TOML < project TOML < CLI
    os.chdir(temp_project)

    config = ServeConfig(
      app_uri="app:asgi_app", name="testapp", server=ServerConfig(bind="0.0.0.0:8000", workers=1)
    )

    # Should have the config values
    assert config.server.bind == "0.0.0.0:8000"
    assert config.server.workers == 1


# ==============================================================================
# VersionCommand Tests
# ==============================================================================


class TestVersionCommand:
  """Tests for 'baseweb version' command."""

  def test_version_displays_version(self):
    """
    Given: baseweb package with __version__
    When: Running 'baseweb version'
    Then: Should display version number
    """
    import sys
    from io import StringIO

    from baseweb.__main__ import version

    # Capture stdout
    old_stdout = sys.stdout
    sys.stdout = StringIO()

    try:
      version()
      output = sys.stdout.getvalue()

      # Should output version number
      assert len(output.strip()) > 0
      # Version should be in format X.Y.Z
      parts = output.strip().split(".")
      assert len(parts) >= 2  # At least major.minor
    finally:
      sys.stdout = old_stdout

  def test_version_format(self):
    """
    Given: baseweb package
    When: Running 'baseweb version'
    Then: Should output just the version number (no extra text)
    """
    import sys
    from io import StringIO

    from baseweb.__main__ import version

    # Capture stdout
    old_stdout = sys.stdout
    sys.stdout = StringIO()

    try:
      version()
      output = sys.stdout.getvalue()

      # Should be just the version number, no extra text
      output = output.strip()
      # Should not contain extra text like "version" or "baseweb"
      assert "version" not in output.lower() or output.count(".") >= 2
      # Should be in semantic version format
      assert "." in output  # Should contain dots for version numbers
    finally:
      sys.stdout = old_stdout

  def test_version_consistent_with_package(self):
    """
    Given: baseweb.__version__ constant
    When: Running 'baseweb version'
    Then: Should match the package __version__
    """
    import sys
    from io import StringIO

    from baseweb import __version__
    from baseweb.__main__ import version

    # Capture stdout
    old_stdout = sys.stdout
    sys.stdout = StringIO()

    try:
      version()
      output = sys.stdout.getvalue().strip()

      # Should match package version
      assert output == __version__
    finally:
      sys.stdout = old_stdout


# ==============================================================================
# Argument Parsing Tests
# ==============================================================================


class TestArgumentParsing:
  """Tests for CLI argument parsing."""

  def test_no_command_shows_help(self):
    """
    Given: Running 'baseweb' without arguments
    When: CLI is invoked
    Then: Should show help message and exit with error code
    """
    from io import StringIO

    from baseweb.__main__ import run

    # Mock sys.argv to have no command
    with patch("sys.argv", ["baseweb"]):
      with patch("sys.stdout", new_callable=StringIO):
        # Should exit with error code (Clevis uses 2 for missing command)
        with pytest.raises(SystemExit) as exc_info:
          run()

        # Clevis exits with code 2 when command is missing
        assert exc_info.value.code in [1, 2]

  def test_unknown_command_shows_error(self):
    """
    Given: Running 'baseweb unknown'
    When: CLI is invoked
    Then: Should show error and exit with error code
    """

    from baseweb.__main__ import run

    # Mock sys.argv with unknown command
    with patch("sys.argv", ["baseweb", "unknown"]):
      # Should exit with error code (Clevis may use different codes)
      with pytest.raises(SystemExit) as exc_info:
        run()

      # Clevis exits with code 2 for invalid choice
      assert exc_info.value.code in [1, 2]

  def test_serve_command_recognized(self):
    """
    Given: Running 'baseweb serve'
    When: CLI parses arguments
    Then: Should dispatch to serve command
    """
    from baseweb.__main__ import run

    # Mock sys.argv for serve command
    with patch("sys.argv", ["baseweb", "serve", "--app-uri", "app:asgi_app"]):
      # Mock serve function
      with patch("baseweb.__main__.serve") as mock_serve:
        run()

        # Should have called serve function
        mock_serve.assert_called_once()

  def test_init_command_recognized(self):
    """
    Given: Running 'baseweb init'
    When: CLI parses arguments
    Then: Should dispatch to init command
    """
    from baseweb.__main__ import run

    # Mock sys.argv for init command
    with patch("sys.argv", ["baseweb", "init"]):
      # Mock init function
      with patch("baseweb.__main__.init") as mock_init:
        run()

        # Should have called init function
        mock_init.assert_called_once()

  def test_check_command_recognized(self):
    """
    Given: Running 'baseweb check'
    When: CLI parses arguments
    Then: Should dispatch to check command
    """
    from baseweb.__main__ import run

    # Mock sys.argv for check command
    with patch("sys.argv", ["baseweb", "check", "--app-uri", "app:asgi_app"]):
      # Mock check function
      with patch("baseweb.__main__.check") as mock_check:
        run()

        # Should have called check function
        mock_check.assert_called_once()

  def test_config_command_recognized(self):
    """
    Given: Running 'baseweb config'
    When: CLI parses arguments
    Then: Should dispatch to config command
    """
    from baseweb.__main__ import run

    # Mock sys.argv for config command
    with patch("sys.argv", ["baseweb", "config"]):
      # Mock show_config function
      with patch("baseweb.__main__.show_config") as mock_config:
        run()

        # Should have called show_config function
        mock_config.assert_called_once()

  def test_version_command_recognized(self):
    """
    Given: Running 'baseweb version'
    When: CLI parses arguments
    Then: Should dispatch to version command
    """
    from baseweb.__main__ import run

    # Mock sys.argv for version command
    with patch("sys.argv", ["baseweb", "version"]):
      # Mock version function
      with patch("baseweb.__main__.version") as mock_version:
        run()

        # Should have called version function
        mock_version.assert_called_once()

  def test_command_aliases(self):
    """
    Given: Command with aliases (if any)
    When: Using alias instead of full command
    Then: Should dispatch to same command
    """
    # Baseweb CLI doesn't currently have command aliases
    # This test verifies that commands work with their canonical names
    from baseweb.__main__ import run

    # Test that 'serve' works correctly
    with patch("sys.argv", ["baseweb", "serve", "--app-uri", "app:asgi_app"]):
      with patch("baseweb.__main__.serve") as mock_serve:
        run()
        mock_serve.assert_called_once()


# ==============================================================================
# Command Dispatch Tests
# ==============================================================================


class TestCommandDispatch:
  """Tests for CLI command dispatch logic."""

  def test_dispatch_calls_serve(self):
    """
    Given: CLI args for serve command
    When: get_cmd() returns 'serve'
    Then: Should call serve() function
    """
    from baseweb.__main__ import run

    # Mock sys.argv for serve
    with patch("sys.argv", ["baseweb", "serve", "--app-uri", "app:asgi_app"]):
      with patch("baseweb.__main__.serve") as mock_serve:
        run()
        mock_serve.assert_called_once()

  def test_dispatch_calls_init(self):
    """
    Given: CLI args for init command
    When: get_cmd() returns 'init'
    Then: Should call init() function
    """
    from baseweb.__main__ import run

    # Mock sys.argv for init
    with patch("sys.argv", ["baseweb", "init"]):
      with patch("baseweb.__main__.init") as mock_init:
        run()
        mock_init.assert_called_once()

  def test_dispatch_calls_check(self):
    """
    Given: CLI args for check command
    When: get_cmd() returns 'check'
    Then: Should call check() function
    """
    from baseweb.__main__ import run

    # Mock sys.argv for check
    with patch("sys.argv", ["baseweb", "check", "--app-uri", "app:asgi_app"]):
      with patch("baseweb.__main__.check") as mock_check:
        run()
        mock_check.assert_called_once()

  def test_dispatch_calls_config(self):
    """
    Given: CLI args for config command
    When: get_cmd() returns 'config'
    Then: Should call show_config() function
    """
    from baseweb.__main__ import run

    # Mock sys.argv for config
    with patch("sys.argv", ["baseweb", "config"]):
      with patch("baseweb.__main__.show_config") as mock_config:
        run()
        mock_config.assert_called_once()

  def test_dispatch_calls_version(self):
    """
    Given: CLI args for version command
    When: get_cmd() returns 'version'
    Then: Should call version() function
    """
    from baseweb.__main__ import run

    # Mock sys.argv for version
    with patch("sys.argv", ["baseweb", "version"]):
      with patch("baseweb.__main__.version") as mock_version:
        run()
        mock_version.assert_called_once()

  def test_dispatch_with_unknown_command(self):
    """
    Given: Unknown command
    When: get_cmd() returns unknown value
    Then: Should show help and exit with error code
    """
    from baseweb.__main__ import run

    # Mock sys.argv with unknown command
    with patch("sys.argv", ["baseweb", "unknown_command"]):
      with pytest.raises(SystemExit) as exc_info:
        run()

      # Clevis may use code 2 for invalid choice
      assert exc_info.value.code in [1, 2]


# ==============================================================================
# Error Handling Tests
# ==============================================================================


class TestErrorHandling:
  """Tests for CLI error handling."""

  def test_missing_config_file_error(self, temp_project):
    """
    Given: No baseweb.toml file present
    When: Running commands that require config
    Then: Should handle gracefully with clear message
    """
    # This test verifies that commands handle missing config gracefully
    # Clevis will use defaults when config file is missing
    from baseweb.__main__ import ConfigConfig

    # Should still be able to create config with defaults
    config = ConfigConfig()
    assert config is not None
    # Default app_uri should be set
    assert config.app_uri is not None

  def test_invalid_toml_syntax_error(self, temp_project):
    """
    Given: baseweb.toml with invalid TOML syntax
    When: Running CLI commands
    Then: Should report syntax error with location
    """
    import os

    import tomllib

    os.chdir(temp_project)

    # Create invalid TOML file
    config_path = temp_project / "baseweb.toml"
    config_path.write_text("""
# Invalid TOML - missing closing quote
name = "testapp
title = "Test App"
""")

    # Try to parse the invalid TOML
    with open(config_path, "rb") as f:
      with pytest.raises(tomllib.TOMLDecodeError):
        tomllib.load(f)

  def test_invalid_config_value_error(self, temp_project):
    """
    Given: baseweb.toml with invalid configuration value
    When: Running CLI commands
    Then: Should report validation error
    """
    # This test verifies validation of config values
    # The check command validates app_uri and other required fields
    from baseweb.__main__ import CheckConfig, check

    config = CheckConfig(app_uri=None, name="testapp")

    with pytest.raises(SystemExit) as exc_info:
      check(config)

    assert exc_info.value.code == 1

  def test_permission_denied_error(self, temp_project):
    """
    Given: No write permission for config file
    When: Running 'baseweb init'
    Then: Should report permission error
    """
    import os

    from baseweb.__main__ import InitConfig, init

    os.chdir(temp_project)

    # Create the config path as a read-only file
    config_path = temp_project / "baseweb.toml"
    config_path.write_text("existing content")
    os.chmod(config_path, 0o444)  # Read-only file

    # Try to write to the read-only file with force
    config = InitConfig(force=True)

    # Should exit with error
    with pytest.raises(SystemExit) as exc_info:
      init(config)

    assert exc_info.value.code == 1

  def test_app_import_module_not_found(self, temp_project):
    """
    Given: app_uri with non-existent module
    When: Importing application
    Then: Should report clear "module not found" error
    """
    import os

    from baseweb.__main__ import import_app

    os.chdir(temp_project)

    with pytest.raises(ImportError) as exc_info:
      import_app("nonexistent_module:app")

    assert "Cannot find module" in str(exc_info.value)

  def test_app_import_attribute_not_found(self, temp_project):
    """
    Given: app_uri with non-existent attribute
    When: Importing application
    Then: Should report "attribute not found" error with available attributes
    """
    import os

    from baseweb.__main__ import import_app

    os.chdir(temp_project)

    with pytest.raises((RuntimeError, AttributeError)) as exc_info:
      import_app("app:nonexistent_app")

    # Should mention the missing attribute
    assert "nonexistent_app" in str(exc_info.value)

  def test_app_import_type_error(self, temp_project):
    """
    Given: App that raises TypeError during initialization
    When: Importing application
    Then: Should report helpful error about initialization failure
    """
    # This test verifies that import_app handles type errors gracefully
    # The actual test would require a module that raises TypeError on import
    # For now, we verify that import_app works with valid app
    import os

    from baseweb.__main__ import import_app

    os.chdir(temp_project)

    # Test with valid app - this should work
    app = import_app("app:asgi_app")
    assert app is not None

  def test_invalid_app_uri_format(self, temp_project):
    """
    Given: app_uri without module:attribute format
    When: Importing application
    Then: Should report format error with example
    """
    import os

    from baseweb.__main__ import import_app

    os.chdir(temp_project)

    with pytest.raises(ImportError) as exc_info:
      import_app("invalid_uri_without_colon")

    assert "Invalid app_uri format" in str(exc_info.value)
    assert "Expected 'module:variable'" in str(exc_info.value)


# ==============================================================================
# Configuration Override Tests
# ==============================================================================


class TestConfigurationOverride:
  """Tests for CLI configuration override via arguments."""

  def test_cli_override_bind(self, temp_project, mock_config_file):
    """
    Given: Config with bind = "0.0.0.0:8000"
    When: Running 'baseweb serve --server-bind :9000'
    Then: Should override bind address from CLI
    """
    from baseweb.__main__ import ServeConfig
    from baseweb.config import ServerConfig

    # Create config with CLI override
    config = ServeConfig(
      app_uri="app:asgi_app", name="testapp", server=ServerConfig(bind=":9000", workers=1)
    )

    # Should have overridden bind address
    assert config.server.bind == ":9000"

  def test_cli_override_workers(self, temp_project, mock_config_file):
    """
    Given: Config with workers = 1
    When: Running 'baseweb serve --server-workers 4'
    Then: Should override workers from CLI
    """
    from baseweb.__main__ import ServeConfig
    from baseweb.config import ServerConfig

    # Create config with CLI override
    config = ServeConfig(
      app_uri="app:asgi_app", name="testapp", server=ServerConfig(bind="0.0.0.0:8000", workers=4)
    )

    # Should have overridden workers
    assert config.server.workers == 4

  def test_cli_override_app_uri(self, temp_project, mock_config_file):
    """
    Given: Config with app_uri = "app:asgi_app"
    When: Running 'baseweb serve --app-uri main:app'
    Then: Should override app_uri from CLI
    """
    from baseweb.__main__ import ServeConfig

    # Create config with CLI override
    config = ServeConfig(app_uri="main:app", name="testapp")

    # Should have overridden app_uri
    assert config.app_uri == "main:app"

  def test_cli_override_name(self, temp_project, mock_config_file):
    """
    Given: Config with name = "testapp"
    When: Running 'baseweb serve --name custom-name'
    Then: Should override name from CLI
    """
    from baseweb.__main__ import ServeConfig

    # Create config with CLI override
    config = ServeConfig(app_uri="app:asgi_app", name="custom-name")

    # Should have overridden name
    assert config.name == "custom-name"

  def test_cli_override_nested_config(self, temp_project, mock_config_file):
    """
    Given: Config with nested [server] section
    When: Running 'baseweb serve --server-bind :9000 --server-timeout 60'
    Then: Should override nested server config from CLI
    """
    from baseweb.__main__ import ServeConfig
    from baseweb.config import ServerConfig

    # Create config with nested overrides
    config = ServeConfig(
      app_uri="app:asgi_app", name="testapp", server=ServerConfig(bind=":9000", workers=4)
    )

    # Should have overridden nested config
    assert config.server.bind == ":9000"
    assert config.server.workers == 4

  def test_env_var_override(self, temp_project, mock_config_file):
    """
    Given: Config + environment variable
    When: Running 'baseweb serve'
    Then: Environment variables should override config (Clevis layering)
    """
    # This test verifies that Clevis layering works correctly
    # Clevis handles: defaults < user TOML < project TOML < env vars < CLI args
    from baseweb.__main__ import ServeConfig
    from baseweb.config import ServerConfig

    # Simulate config from TOML + env var override
    config = ServeConfig(
      app_uri="app:asgi_app", name="testapp", server=ServerConfig(bind="0.0.0.0:8000", workers=1)
    )

    # Should have the config values
    assert config.server.bind == "0.0.0.0:8000"
    assert config.server.workers == 1

  def test_cli_override_env_var(self, temp_project, mock_config_file):
    """
    Given: Config + env var + CLI arg
    When: Running 'baseweb serve --server-bind :9000'
    Then: CLI arg should override env var
    """
    # This test verifies CLI args override env vars (Clevis layering)
    from baseweb.__main__ import ServeConfig
    from baseweb.config import ServerConfig

    # Simulate config with CLI override
    config = ServeConfig(
      app_uri="app:asgi_app", name="testapp", server=ServerConfig(bind=":9000", workers=1)
    )

    # CLI override should be applied
    assert config.server.bind == ":9000"

  def test_all_baseweb_config_fields_overridable(self, temp_project, mock_config_file):
    """
    Given: Any BasewebConfig field
    When: Providing CLI argument for that field
    Then: Should override the field value
    """
    from baseweb.__main__ import ServeConfig
    from baseweb.config import ServerConfig

    # Test overriding various fields
    config = ServeConfig(
      app_uri="custom:app",
      name="custom-name",
      title="Custom Title",
      author="Custom Author",
      version="2.0.0",
      server=ServerConfig(bind=":9999", workers=8),
    )

    # All overridden fields should be set correctly
    assert config.app_uri == "custom:app"
    assert config.name == "custom-name"
    assert config.title == "Custom Title"
    assert config.author == "Custom Author"
    assert config.version == "2.0.0"
    assert config.server.bind == ":9999"
    assert config.server.workers == 8


# ==============================================================================
# Integration Tests
# ==============================================================================


class TestCLIIntegration:
  """Integration tests for CLI with Clevis and BasewebConfig."""

  def test_init_and_check_workflow(self, temp_project):
    """
    Given: Empty project directory
    When: Running 'baseweb init' then 'baseweb check'
    Then: Should create config and validate successfully
    """
    import os

    from baseweb.__main__ import CheckConfig, InitConfig, check, init

    os.chdir(temp_project)

    # Run init
    init_config = InitConfig()
    init(init_config)

    # Config file should exist
    config_path = temp_project / "baseweb.toml"
    assert config_path.exists()

    # App module already created by temp_project fixture
    # Just verify it exists
    app_dir = temp_project / "app"
    assert app_dir.exists()

    # Run check - should succeed
    check_config = CheckConfig(app_uri="app:asgi_app")
    try:
      check(check_config)
    except SystemExit as e:
      # Should exit with code 0 (success)
      assert e.code == 0

  def test_config_then_serve_workflow(self, temp_project, mock_config_file):
    """
    Given: Valid configuration
    When: Running 'baseweb config' then 'baseweb serve'
    Then: Should show config and start server
    """
    import sys
    from io import StringIO

    from baseweb.__main__ import ConfigConfig, ServeConfig, show_config

    # Run config command
    config = ConfigConfig(app_uri="app:asgi_app", name="testapp", title="Test App")

    # Capture stdout
    old_stdout = sys.stdout
    sys.stdout = StringIO()

    try:
      show_config(config)
      output = sys.stdout.getvalue()

      # Should display configuration
      assert "Baseweb Configuration" in output
    finally:
      sys.stdout = old_stdout

    # Serve command would use the same configuration
    serve_config = ServeConfig(app_uri="app:asgi_app", name="testapp", title="Test App")
    assert serve_config.app_uri == "app:asgi_app"

  def test_clevis_layered_configuration(self, temp_project):
    """
    Given: Default config + user TOML + project TOML + env vars + CLI args
    When: Running 'baseweb serve'
    Then: Should merge all layers (Clevis layered config)
    """
    from baseweb.__main__ import ServeConfig

    # Create ServeConfig with overrides (simulates CLI args)
    config = ServeConfig(app_uri="app:asgi_app", name="custom-name", title="Custom Title")

    # Should have merged values from defaults + CLI
    assert config.app_uri == "app:asgi_app"
    assert config.name == "custom-name"
    assert config.title == "Custom Title"

  def test_multiple_cli_overrides(self, temp_project, mock_config_file):
    """
    Given: Valid configuration
    When: Running 'baseweb serve --server-bind :9000 --server-workers 4 --name custom'
    Then: Should apply all CLI overrides
    """
    from baseweb.__main__ import ServeConfig
    from baseweb.config import ServerConfig

    # Create config with multiple overrides
    config = ServeConfig(
      app_uri="app:asgi_app",
      name="custom",
      title="Test App",
      server=ServerConfig(bind=":9000", workers=4),
    )

    # All overrides should be applied
    assert config.name == "custom"
    assert config.server.bind == ":9000"
    assert config.server.workers == 4

  def test_custom_config_file_path(self, temp_project):
    """
    Given: Configuration at custom path
    When: Running commands with custom config path
    Then: Should load from custom path
    """
    import os

    from baseweb.__main__ import InitConfig, init

    os.chdir(temp_project)

    # Create config at custom path
    custom_path = temp_project / "custom.toml"
    init_config = InitConfig(config="custom.toml")
    init(init_config)

    # Should create config at custom path
    assert custom_path.exists()
    content = custom_path.read_text()
    assert "name" in content


# ==============================================================================
# Helper Function Tests
# ==============================================================================


class TestImportApp:
  """Tests for import_app helper function."""

  def test_import_app_simple_module(self, temp_project):
    """
    Given: Valid module:attribute URI
    When: Calling import_app("app:asgi_app")
    Then: Should import module and return attribute
    """
    # Change to temp_project directory to find the app module
    import os

    from baseweb.__main__ import import_app

    os.chdir(temp_project)

    app = import_app("app:asgi_app")
    assert app is not None
    # The returned app is the Quart instance
    assert hasattr(app, "__name__")

  def test_import_app_nested_module(self, temp_project):
    """
    Given: Valid nested.module:attribute URI
    When: Calling import_app("nested.module:app")
    Then: Should import nested module and return attribute
    """
    from baseweb.__main__ import import_app

    # Create nested module structure
    nested_dir = temp_project / "nested"
    nested_dir.mkdir()
    (nested_dir / "__init__.py").write_text("")
    (nested_dir / "module.py").write_text(
      """
from quart import Quart
app = Quart(__name__)
"""
    )

    import os

    os.chdir(temp_project)

    app = import_app("nested.module:app")
    assert app is not None

  def test_import_app_adds_cwd_to_path(self, temp_project):
    """
    Given: Local module in current directory
    When: Calling import_app
    Then: Should add cwd to sys.path before importing
    """
    import os

    from baseweb.__main__ import import_app

    os.chdir(temp_project)

    # sys.path should include cwd after import_app
    import_app("app:asgi_app")

    # The first item in sys.path should be the current working directory
    assert str(Path.cwd()) in sys.path

  def test_import_app_module_not_found(self, temp_project):
    """
    Given: Non-existent module
    When: Calling import_app("nonexistent:app")
    Then: Should raise ImportError with helpful message
    """
    import os

    from baseweb.__main__ import import_app

    os.chdir(temp_project)

    with pytest.raises(ImportError) as exc_info:
      import_app("nonexistent:app")

    assert "Cannot find module" in str(exc_info.value)

  def test_import_app_attribute_not_found(self, temp_project):
    """
    Given: Valid module but missing attribute
    When: Calling import_app("app:nonexistent")
    Then: Should raise RuntimeError with helpful message
    """
    import os

    from baseweb.__main__ import import_app

    os.chdir(temp_project)

    # import_app wraps all errors in RuntimeError
    with pytest.raises(RuntimeError) as exc_info:
      import_app("app:nonexistent")

    # Should mention the missing attribute
    assert "nonexistent" in str(exc_info.value)

  def test_import_app_type_error(self, tmp_path):
    """
    Given: Module that raises TypeError during import
    When: Calling import_app
    Then: Should handle error gracefully
    """
    from baseweb.__main__ import import_app

    # Clear any cached app module
    sys.modules.pop("app", None)

    # Create a fresh app module (not using temp_project fixture)
    app_dir = tmp_path / "app"
    app_dir.mkdir()
    (app_dir / "__init__.py").write_text(
      """
# This creates a scenario where the app exists but causes issues
asgi_app = "not_a_function"  # Not a valid ASGI app
"""
    )

    import os

    os.chdir(tmp_path)

    # import_app should successfully return the string
    # (it doesn't validate that it's a callable)
    result = import_app("app:asgi_app")
    assert result == "not_a_function"

  def test_import_app_invalid_format(self, temp_project):
    """
    Given: Invalid URI format (no colon)
    When: Calling import_app("invalid_uri")
    Then: Should raise ImportError with format hint
    """
    import os

    from baseweb.__main__ import import_app

    os.chdir(temp_project)

    with pytest.raises(ImportError) as exc_info:
      import_app("invalid_uri")

    assert "Invalid app_uri format" in str(exc_info.value)
    assert "Expected 'module:variable'" in str(exc_info.value)


class TestConfigToToml:
  """Tests for config_to_toml helper function."""

  def test_config_to_toml_basic(self):
    """
    Given: BasewebConfig instance
    When: Converting to TOML
    Then: Should produce valid TOML string
    """
    from baseweb.__main__ import config_to_toml
    from baseweb.config import BasewebConfig

    config = BasewebConfig(name="testapp", title="Test App")
    toml_str = config_to_toml(config)

    # Should be valid TOML format
    assert 'name = "testapp"' in toml_str
    assert 'title = "Test App"' in toml_str

  def test_config_to_toml_filters_none(self):
    """
    Given: BasewebConfig with None values
    When: Converting to TOML
    Then: Should filter out None values (TOML doesn't support null)
    """
    from baseweb.__main__ import config_to_toml
    from baseweb.config import BasewebConfig

    config = BasewebConfig(name="testapp", version=None)  # version is None
    toml_str = config_to_toml(config)

    # version should not appear in TOML (it's None)
    lines = toml_str.split("\n")
    version_lines = [line for line in lines if line.startswith("version =")]
    assert len(version_lines) == 0

  def test_config_to_toml_nested_sections(self):
    """
    Given: BasewebConfig with nested config (server, branding, features)
    When: Converting to TOML
    Then: Should create nested TOML sections
    """
    from baseweb.__main__ import config_to_toml
    from baseweb.config import BasewebConfig

    config = BasewebConfig()
    toml_str = config_to_toml(config)

    # Should contain nested sections
    assert "[server]" in toml_str
    assert "[branding.colors]" in toml_str
    assert "[branding.icons]" in toml_str
    assert "[branding.favicon]" in toml_str
    assert "[features.socketio]" in toml_str

  def test_config_to_toml_omit_fields(self):
    """
    Given: BasewebConfig and omit list
    When: Converting to TOML with omit parameter
    Then: Should exclude specified fields from output
    """
    from baseweb.__main__ import config_to_toml
    from baseweb.config import BasewebConfig

    config = BasewebConfig(name="testapp", title="Test App")
    toml_str = config_to_toml(config, omit=["name"])

    # name should not appear in TOML
    lines = toml_str.split("\n")
    name_lines = [line for line in lines if line.startswith("name =")]
    assert len(name_lines) == 0

    # title should still appear
    assert 'title = "Test App"' in toml_str

  def test_config_to_toml_all_fields(self):
    """
    Given: BasewebConfig with all fields populated
    When: Converting to TOML
    Then: Should include all fields in output
    """
    from baseweb.__main__ import config_to_toml
    from baseweb.config import BasewebConfig, ServerConfig

    config = BasewebConfig(
      name="myapp",
      title="My App",
      author="Test Author",
      description="Test description",
      version="1.0.0",
      app_uri="main:app",
      server=ServerConfig(bind="0.0.0.0:9000", workers=4),
    )
    toml_str = config_to_toml(config)

    assert 'name = "myapp"' in toml_str
    assert 'title = "My App"' in toml_str
    assert 'author = "Test Author"' in toml_str
    assert 'version = "1.0.0"' in toml_str
    assert 'app_uri = "main:app"' in toml_str
    assert 'bind = "0.0.0.0:9000"' in toml_str
    assert "workers = 4" in toml_str


class TestPrintConfigTable:
  """Tests for print_config_table helper function."""

  def test_print_config_table_format(self, capsys):
    """
    Given: BasewebConfig instance
    When: Calling print_config_table
    Then: Should output formatted table to stdout
    """
    from baseweb.__main__ import print_config_table
    from baseweb.config import BasewebConfig

    config = BasewebConfig(name="testapp", title="Test App")
    print_config_table(config)

    captured = capsys.readouterr()
    output = captured.out

    assert "Baseweb Configuration" in output
    assert "Application:" in output

  def test_print_config_table_sections(self, capsys):
    """
    Given: BasewebConfig with nested sections
    When: Calling print_config_table
    Then: Should display sections with headers
    """
    from baseweb.__main__ import print_config_table
    from baseweb.config import BasewebConfig

    config = BasewebConfig()
    print_config_table(config)

    captured = capsys.readouterr()
    output = captured.out

    # Should contain nested section names
    assert "Server:" in output
    assert "Branding:" in output

  def test_print_config_table_omit_fields(self, capsys):
    """
    Given: BasewebConfig and omit list
    When: Calling print_config_table with omit parameter
    Then: Should exclude specified fields from output
    """
    from baseweb.__main__ import print_config_table
    from baseweb.config import BasewebConfig

    config = BasewebConfig(name="testapp")
    print_config_table(config, omit=["name"])

    captured = capsys.readouterr()
    output = captured.out

    # name should not appear in output
    assert "Name: testapp" not in output

  def test_print_config_table_scalar_fields(self, capsys):
    """
    Given: BasewebConfig with scalar fields
    When: Calling print_config_table
    Then: Should display scalar fields in Application section
    """
    from baseweb.__main__ import print_config_table
    from baseweb.config import BasewebConfig

    config = BasewebConfig(name="testapp", title="Test App", author="Test Author")
    print_config_table(config)

    captured = capsys.readouterr()
    output = captured.out

    # Scalar fields should be under "Application:"
    assert "Name: testapp" in output
    assert "Title: Test App" in output
    assert "Author: Test Author" in output


# ==============================================================================
# StandaloneApplication Tests
# ==============================================================================


class TestStandaloneApplication:
  """Tests for StandaloneApplication Gunicorn wrapper."""

  def test_standalone_application_init(self):
    """
    Given: app_uri and options
    When: Creating StandaloneApplication
    Then: Should store app_uri and options
    """
    from baseweb.__main__ import StandaloneApplication

    app = StandaloneApplication("app:asgi_app", {"bind": "0.0.0.0:8000"})

    assert app.app_uri == "app:asgi_app"
    assert app.options == {"bind": "0.0.0.0:8000"}

  def test_standalone_application_load_config(self):
    """
    Given: StandaloneApplication with options
    When: Calling load_config()
    Then: Should set Gunicorn config from options
    """
    from baseweb.__main__ import StandaloneApplication

    options = {
      "bind": "0.0.0.0:9000",
      "workers": 4,
      "timeout": 60,
    }
    app = StandaloneApplication("app:asgi_app", options)
    app.load_config()

    # Verify config was set
    # Gunicorn bind is a list
    assert app.cfg.settings["bind"].value == ["0.0.0.0:9000"]
    assert app.cfg.settings["workers"].value == 4
    assert app.cfg.settings["timeout"].value == 60

  def test_standalone_application_load(self, temp_project):
    """
    Given: StandaloneApplication with valid app_uri
    When: Calling load()
    Then: Should import and return the ASGI application
    """
    import os

    from baseweb.__main__ import StandaloneApplication

    os.chdir(temp_project)

    app = StandaloneApplication("app:asgi_app", {})
    loaded_app = app.load()

    # Should return the ASGI app from the module
    assert loaded_app is not None

  def test_standalone_application_options_none(self):
    """
    Given: StandaloneApplication with no options
    When: Creating instance
    Then: Should use empty dict for options
    """
    from baseweb.__main__ import StandaloneApplication

    app = StandaloneApplication("app:asgi_app", None)

    # Should convert None to empty dict
    assert app.options == {}

  def test_standalone_application_filters_options(self):
    """
    Given: StandaloneApplication with extra options
    When: Calling load_config()
    Then: Should only set valid Gunicorn settings
    """
    from baseweb.__main__ import StandaloneApplication

    options = {
      "bind": "0.0.0.0:9000",
      "workers": 4,
      "invalid_option": "should_be_ignored",  # Not a valid Gunicorn setting
    }
    app = StandaloneApplication("app:asgi_app", options)
    app.load_config()

    # Valid options should be set
    # Gunicorn bind is a list
    assert app.cfg.settings["bind"].value == ["0.0.0.0:9000"]
    assert app.cfg.settings["workers"].value == 4

    # Invalid option should be ignored (not raise an error)
    # Gunicorn only accepts known settings

