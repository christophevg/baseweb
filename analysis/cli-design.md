# Baseweb CLI and Configuration Design

**Created:** 2026-06-05
**Status:** Design
**Version:** 1.0.0

---

## Executive Summary

This document describes the design for baseweb's CLI and configuration system, replacing the current environment-variable-only approach with a unified configuration system using **Clevis** for configuration loading.

---

## Problem Statement

### Current State

The Baseweb class uses environment variables for all configuration:

```python
self.settings = DotMap({
  k: os.environ.get(f"APP_{k.upper()}", v)
  for k, v in {
    "version": __version__,
    "url": None,
    "name": os.path.basename(os.getcwd()),
    ...
  }.items()
})
```

### Key Gap

**No unified configuration system exists.** Configuration is scattered across environment variables, hardcoded defaults, and ad-hoc settings dictionaries. A structured approach is needed.

### Solution Approach

Use **Clevis** as the configuration loading mechanism. Clevis provides:
- Layered configuration (defaults < user-level < project-level < CLI args)
- TOML file support
- Environment variable interpolation
- Type-safe dataclass population
- CLI argument generation from config schema

---

## Design Goals

1. **Clevis-Powered Configuration**: All configuration loaded via Clevis
2. **Single Source of Truth**: BasewebConfig dataclass defines all settings
3. **Clean Architecture**: Baseweb.__init__ accepts BasewebConfig directly
4. **Developer Friendly**: Clear error messages, validation, sensible defaults
5. **Well Tested**: Comprehensive test coverage for all configuration paths

---

## Architecture Decision: Unified Configuration via Clevis

### Configuration Hierarchy

**Clevis** provides a layered configuration system with the following priority (highest wins):

1. CLI arguments (command-line flags)
2. Environment variables (APP_*, GUNICORN_*)
3. Project-level TOML (`./baseweb.toml`)
4. User-level TOML (`~/.baseweb.toml`)
5. Dataclass defaults

### BasewebConfig Dataclass

**All application and server configuration** is defined in a single dataclass, populated by Clevis:

```python
from dataclasses import dataclass, field
from typing import Optional

@dataclass
class GunicornConfig:
    """Gunicorn server configuration."""
    bind: str = "0.0.0.0:8000"
    workers: int = 1
    worker_class: str = "uvicorn.workers.UvicornWorker"
    timeout: int = 120
    keepalive: int = 5

@dataclass
class BasewebConfig:
    """Baseweb application configuration."""
    # Application identification
    name: str = "app"
    title: str = "A baseweb app"
    author: str = "Unknown Author"
    description: str = "A baseweb app"
    version: Optional[str] = None

    # URLs and paths
    url: Optional[str] = None
    main_template: Optional[str] = None

    # Visual settings
    short_name: Optional[str] = None
    color_scheme: str = "dark"
    color: str = "rgb(21, 101, 192)"
    color_name: str = "blue"
    background_color: str = "rgb(21, 101, 192)"
    icon: Optional[str] = None
    social_image: Optional[str] = None

    # Application type
    style: str = "web"  # "web" or "pwa"

    # Features
    socketio: bool = True
    favicon_support: bool = False
    keep_alive: bool = False

    # Server configuration
    gunicorn: GunicornConfig = field(default_factory=GunicornConfig)

    # Entry point (for CLI mode)
    app_uri: str = "app:asgi_app"
```

### Baseweb Class Integration

**Clean Architecture**: Baseweb.__init__ accepts BasewebConfig directly:

```python
from baseweb import Baseweb
from baseweb.config import BasewebConfig
from clevis import get_config

# Create from config object (for programmatic use)
config = BasewebConfig(name="myapp", title="My App")
app = Baseweb(config)

# Load from TOML file (Clevis-powered, recommended)
app = Baseweb(get_config(BasewebConfig, name="baseweb"))
```

### Configuration Loading

**Clevis handles all configuration loading:**

```python
from clevis import get_config
from baseweb.config import BasewebConfig

# Load configuration (recommended pattern)
config = get_config(BasewebConfig, name="baseweb")

# Clevis automatically:
# - Loads defaults from BasewebConfig dataclass
# - Loads user-level ~/.baseweb.toml
# - Loads project-level ./baseweb.toml
# - Applies environment variable overrides
# - Validates and returns typed BasewebConfig
```

---

## Detailed Design

### 1. Configuration Loading via Clevis

**File:** `src/baseweb/config.py`

```python
from dataclasses import dataclass, field
from typing import Optional

# Configuration schema (dataclasses)
@dataclass
class GunicornConfig:
  """Gunicorn server configuration."""
  bind: str = "0.0.0.0:8000"
  workers: int = 1
  worker_class: str = "uvicorn.workers.UvicornWorker"
  timeout: int = 120
  keepalive: int = 5

@dataclass
class BasewebConfig:
  """Baseweb application configuration."""
  # Application identification
  name: str = "app"
  title: str = "A baseweb app"
  author: str = "Unknown Author"
  description: str = "A baseweb app"
  version: Optional[str] = None

  # URLs and paths
  url: Optional[str] = None
  main_template: Optional[str] = None

  # Visual settings
  short_name: Optional[str] = None
  color_scheme: str = "dark"
  color: str = "rgb(21, 101, 192)"
  color_name: str = "blue"
  background_color: str = "rgb(21, 101, 192)"
  icon: Optional[str] = None
  social_image: Optional[str] = None

  # Application type
  style: str = "web"  # "web" or "pwa"

  # Features
  socketio: bool = True
  favicon_support: bool = False
  keep_alive: bool = False

  # Server configuration
  gunicorn: GunicornConfig = field(default_factory=GunicornConfig)

  # Entry point (for CLI mode)
  app_uri: str = "app:asgi_app"
```

**Usage:**

```python
from clevis import get_config
from baseweb.config import BasewebConfig

# Load configuration
config = get_config(BasewebConfig, name="baseweb")
```

### 2. Baseweb Class Integration

**File:** `src/baseweb/__init__.py`

```python
from baseweb.config import BasewebConfig

class Baseweb(Quart):
  def __init__(self, config: BasewebConfig, *args, **kwargs):
    """
    Initialize Baseweb application from configuration.

    Args:
      config: BasewebConfig instance with all settings
    """
    # Store config internally
    self.config = config

    # Initialize Quart with app name
    super().__init__(config.name, *args, **kwargs)

    # Apply configuration to application
    self._apply_config()
    ...

  def _apply_config(self):
    """Apply configuration to application."""
    # Set title, author, description for templates
    # Configure socketio if enabled
    # Set up routes, etc.
    ...
```

**Usage:**

```python
from baseweb import Baseweb
from baseweb.config import BasewebConfig
from clevis import get_config

# Create from config object (for programmatic use)
config = BasewebConfig(name="myapp", title="My App")
app = Baseweb(config)

# Create from TOML (recommended)
app = Baseweb(get_config(BasewebConfig, name="baseweb"))
```

### 3. CLI Commands

**File:** `src/baseweb/__main__.py`

```python
#!/usr/bin/env python3
"""
Baseweb CLI - Run and manage baseweb applications.

Usage:
    baseweb serve [options]
    baseweb init [options]
    baseweb config
    baseweb version
    baseweb check
"""

import argparse
import sys
from pathlib import Path

def cmd_serve(args):
    """Run baseweb application with Gunicorn."""
    from baseweb.config import BasewebConfig
    from clevis import get_config
    from gunicorn.app.wsgiapp import WSGIApplication

    # Load configuration using Clevis
    config = get_config(BasewebConfig, name="baseweb")

    # Add current directory to path for finding modules
    sys.path.insert(0, str(Path().resolve()))

    # Override with CLI arguments
    if args.app_uri:
        config.app_uri = args.app_uri
    if args.bind:
        config.gunicorn.bind = args.bind
    if args.workers:
        config.gunicorn.workers = args.workers

    # Import and run
    app = import_app(config.app_uri)
    WSGIApplication(app, config.gunicorn).run()

def cmd_init(args):
    """Create initial baseweb.toml configuration file."""
    config_path = Path(args.config)

    if config_path.exists() and not args.force:
        print(f"Configuration file already exists: {config_path}")
        print("Use --force to overwrite")
        sys.exit(1)

    # Write default configuration
    config_path.write_text(DEFAULT_CONFIG)
    print(f"Created {config_path}")
    print("Edit this file to customize your baseweb application")

def cmd_config(args):
    """Display current configuration."""
    from baseweb.config import BasewebConfig
    from clevis import get_config

    config = get_config(BasewebConfig, name="baseweb")

    if args.format == "toml":
        # Output as TOML
        print(config_to_toml(config))
    else:
        # Output as table
        print_config_table(config)

def cmd_version(args):
    """Display baseweb version."""
    from baseweb import __version__
    print(f"baseweb {__version__}")

def cmd_check(args):
    """Validate configuration without running."""
    from baseweb.config import BasewebConfig
    from clevis import get_config, ConfigError

    try:
        config = get_config(BasewebConfig, name="baseweb")
        print("Configuration is valid")
        print(f"  App: {config.name}")
        print(f"  Entry: {config.app_uri}")
        print(f"  Bind: {config.gunicorn.bind}")
        print(f"  Workers: {config.gunicorn.workers}")

        # Verify app_uri can be imported
        try:
            import_app(config.app_uri)
            print(f"  Import: OK")
        except ImportError as e:
            print(f"  Import: FAILED - {e}")
            sys.exit(1)

    except ConfigError as e:
        print(f"Configuration error: {e.message}")
        print(f"  Field: {e.field_path}")
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(
        description="Baseweb CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  baseweb init                    Create default baseweb.toml
  baseweb check                   Validate configuration
  baseweb serve                   Run app from baseweb.toml
  baseweb serve --port 8080       Override port
  baseweb config                  Show current configuration
        """
    )

    subparsers = parser.add_subparsers(dest="command")

    # serve command
    serve_parser = subparsers.add_parser("serve", help="Run baseweb application")
    serve_parser.add_argument("--app-uri", help="Application entry point (default: app:asgi_app)")
    serve_parser.add_argument("--bind", "-b", help="Bind address (default: 0.0.0.0:8000)")
    serve_parser.add_argument("--workers", "-w", type=int, help="Number of workers")
    serve_parser.set_defaults(func=cmd_serve)

    # init command
    init_parser = subparsers.add_parser("init", help="Create configuration file")
    init_parser.add_argument("--config", "-c", default="baseweb.toml", help="Configuration file path")
    init_parser.add_argument("--force", "-f", action="store_true", help="Overwrite existing file")
    init_parser.set_defaults(func=cmd_init)

    # config command
    config_parser = subparsers.add_parser("config", help="Show configuration")
    config_parser.add_argument("--format", choices=["toml", "table"], default="table")
    config_parser.set_defaults(func=cmd_config)

    # version command
    version_parser = subparsers.add_parser("version", help="Show version")
    version_parser.set_defaults(func=cmd_version)

    # check command
    check_parser = subparsers.add_parser("check", help="Validate configuration")
    check_parser.set_defaults(func=cmd_check)

    args = parser.parse_args()

    if args.command is None:
        parser.print_help()
        sys.exit(1)

    args.func(args)

if __name__ == "__main__":
    main()
```

### 4. Configuration Discovery

**Strategy:**

1. **Project-level**: `./baseweb.toml` (current directory)
2. **User-level**: `~/.baseweb.toml` (user home)
3. **Environment variable**: `BASEWEB_CONFIG` can specify custom path

**Priority:**
- Environment variables > Project TOML > User TOML > Defaults

**Example:**
```bash
# Use project-level config
cd myapp && baseweb serve

# Use custom config file
baseweb serve --config /path/to/config.toml

# Override via environment
APP_NAME="custom" baseweb serve
```

### 4. Configuration Discovery

**Strategy (Clevis handles this automatically):**

1. **User-level**: `~/.baseweb.toml` (user home)
2. **Project-level**: `./baseweb.toml` (current directory)
3. **Environment variable**: `BASEWEB_CONFIG` can specify custom path

**Priority (Clevis layered configuration):**
- Environment variables > Project TOML > User TOML > Defaults

**Example:**
```bash
# Use project-level config
cd myapp && baseweb serve

# Use custom config file
BASEWEB_CONFIG=/path/to/config.toml baseweb serve

# Override via environment
APP_NAME="custom" baseweb serve
```

### 5. Environment Variable Integration

**Clevis automatically handles environment variable overrides:**

| Environment Variable | TOML Path | Description |
|---------------------|-----------|-------------|
| `APP_NAME` | `name` | Application name |
| `APP_TITLE` | `title` | Application title |
| `APP_STYLE` | `style` | Application style (web/pwa) |
| `APP_SOCKETIO` | `socketio` | WebSocket support |
| `BASEWEB_CONFIG` | - | Custom config file path |
| `GUNICORN_BIND` | `gunicorn.bind` | Bind address |
| `GUNICORN_WORKERS` | `gunicorn.workers` | Number of workers |

**No manual code needed** - Clevis automatically maps environment variables to config fields based on naming convention (prefix + field name).

#### Environment Variable Interpolation in TOML

TOML files support environment variable interpolation using either `envtoml` or `tomlev` parser:

```toml
# Basic interpolation
name = "${APP_NAME}"
url = "${APP_URL:-http://localhost:8000}"

# With defaults
[server]
bind = "${GUNICORN_BIND:-0.0.0.0:8000}"
workers = "${GUNICORN_WORKERS:-1}"
```

**Supported Syntax:**
- `${VAR}` - Use environment variable value
- `${VAR:-default}` - Use default if VAR is not set
- Nested values: `${DB_HOST}:${DB_PORT}`

### 6. TOML Configuration Structure

The finalized TOML configuration uses a clean, organized structure with nested sections for logical grouping:

#### Root Level Fields

```toml
# Application entry point (required)
app_uri = "app:asgi_app"

# Application metadata (optional, with defaults)
name = "myapp"
title = "My Application"
short_name = "MyApp"
description = "A baseweb application"
author = "Your Name"
version = "1.0.0"  # Optional, not currently used

# URLs and paths
url = "https://myapp.example.com"
main_template = "main.html"

# Application style
style = "web"  # or "pwa" for Progressive Web App
```

#### Nested Configuration Sections

**Branding Colors:**

```toml
[branding.colors]
scheme = "dark"
primary = "rgb(21, 101, 192)"
primary_name = "blue"
background = "rgb(30, 30, 30)"
```

**Branding Icons:**

```toml
[branding.icons]
app = "static/icons/app.png"
social = "static/icons/social.png"
```

**Favicon Support:**

```toml
[branding.favicon]
enabled = true
safari_mask_color = "#rgb(21, 101, 192)"
windows_tile_color = "#rgb(21, 101, 192)"
```

**SocketIO Feature:**

```toml
[features.socketio]
enabled = true
```

**PWA Feature (with validation):**

```toml
[features.pwa]
display = "standalone"
orientation = "portrait"
start_url = "/"
theme_color = "rgb(21, 101, 192)"
background_color = "rgb(30, 30, 30)"
icons_dir = "static/icons"  # REQUIRED when style = "pwa"
```

**Server Configuration:**

```toml
[server]
bind = "0.0.0.0:8000"
workers = 1
worker_class = "uvicorn.workers.UvicornWorker"
timeout = 120
keepalive = 5
```

#### Application-Specific Configuration

Applications can register custom configuration sections using the `register_app_config()` pattern:

```toml
[app.myapp]
debug = false
custom_setting = "value"

[app.myapp.database]
host = "localhost"
port = 5432
```

**Registration Pattern:**

```python
from baseweb.config import register_app_config, BasewebConfig
from clevis import get_config

@dataclass
class MyAppConfig:
  """Application-specific configuration."""
  debug: bool = False
  custom_setting: str = "default"

  @dataclass
  class Database:
    host: str = "localhost"
    port: int = 5432

  database: Database = field(default_factory=Database)

# Register the custom config
register_app_config("myapp", MyAppConfig)

# Access in application
config = get_config(BasewebConfig, name="baseweb")
# Returns BasewebConfig with app.myapp section populated
```

**Implementation:**

```python
# src/baseweb/config.py

_app_configs: dict[str, type] = {}

def register_app_config(name: str, config_class: type) -> None:
    """
    Register application-specific configuration.

    Args:
        name: Configuration section name (will be accessible as app.{name})
        config_class: Dataclass type for the configuration

    Example:
        @dataclass
        class MyAppConfig:
            debug: bool = False

        register_app_config("myapp", MyAppConfig)

    The configuration will be available in:
        - TOML: [app.myapp] section
        - Environment: APP_MYAPP_* variables
        - Config object: config.app.myapp
    """
    _app_configs[name] = config_class
```

#### Plugin Configuration (Future)

Plugin configurations follow the same pattern:

```toml
[plugin.auth]
enabled = true
provider = "oauth2"

[plugin.analytics]
enabled = false
tracking_id = ""
```

#### Validation Rules

**PWA Style Validation:**

When `style = "pwa"`, the `icons_dir` field in `[features.pwa]` is **required**:

```python
def validate_config(config: BasewebConfig) -> None:
    """Validate configuration constraints."""
    if config.style == "pwa":
        if not config.pwa.icons_dir:
            raise ConfigError(
                "Configuration error: icons_dir is required when style = 'pwa'. "
                "Add [features.pwa] section with icons_dir = \"path/to/icons\""
            )
```

**Example Error Message:**

```
Configuration error: icons_dir is required when style = 'pwa'
  Field: features.pwa.icons_dir
  Add [features.pwa] section with icons_dir = "static/icons"
```

#### Complete Example

```toml
# baseweb.toml - Complete configuration example

# Application entry point
app_uri = "app:asgi_app"

# Application metadata
name = "myapp"
title = "My Application"
short_name = "MyApp"
description = "A Progressive Web App built with baseweb"
author = "Your Name"
version = "1.0.0"

# URLs and paths
url = "https://myapp.example.com"
main_template = "main.html"

# Application style (web or pwa)
style = "pwa"

# Branding
[branding.colors]
scheme = "dark"
primary = "rgb(21, 101, 192)"
primary_name = "blue"
background = "rgb(30, 30, 30)"

[branding.icons]
app = "static/icons/app.png"
social = "static/icons/social.png"

[branding.favicon]
enabled = true
safari_mask_color = "rgb(21, 101, 192)"
windows_tile_color = "rgb(21, 101, 192)"

# Features
[features.socketio]
enabled = true

[features.pwa]
display = "standalone"
orientation = "portrait"
start_url = "/"
theme_color = "rgb(21, 101, 192)"
background_color = "rgb(30, 30, 30)"
icons_dir = "static/icons"

# Server configuration
[server]
bind = "0.0.0.0:8000"
workers = 1
worker_class = "uvicorn.workers.UvicornWorker"
timeout = 120
keepalive = 5

# Application-specific configuration
[app.myapp]
debug = false
custom_setting = "value"

[app.myapp.database]
host = "${DB_HOST:-localhost}"
port = "${DB_PORT:-5432}"
```

### 6. Error Handling

**Validation Points:**

1. **Config File Not Found**: Gracefully fall back to defaults
2. **Invalid TOML**: Clear error message with location
3. **Missing Required Field**: Helpful error with field name
4. **Invalid app_uri**: Clear error when trying to import
5. **Port Already in Use**: Clear error from Gunicorn

**Example Error Messages:**

```python
# Config file not found
"Configuration file not found: ./baseweb.toml"
"Run 'baseweb init' to create a default configuration"

# Invalid TOML
"Failed to parse baseweb.toml: line 15: invalid syntax"
"Check TOML syntax at https://toml.io"

# Missing required field
"Required field 'app_uri' is missing"
"Add 'app_uri = \"app:asgi_app\"' to your configuration"

# Invalid app_uri
"Failed to import 'app:asgi_app'"
"Module 'app' not found. Make sure you're in the correct directory."
"Did you mean 'app:asgi_app'?"
```

### 6. Testing Strategy

**Test Categories:**

1. **Unit Tests** (`tests/test_config.py`):
   - Configuration loading via Clevis
   - Environment variable override
   - Configuration validation
   - Error handling for invalid configs

2. **Unit Tests** (`tests/test_cli.py`):
   - CLI argument parsing
   - Command dispatch
   - Error messages

3. **Integration Tests** (`tests/test_integration.py`):
   - End-to-end configuration loading
   - Baseweb with BasewebConfig
   - CLI serve command

**Test Cases:**

```python
# tests/test_config.py

def test_load_config_default():
    """Test loading configuration with defaults."""
    from baseweb.config import BasewebConfig
    from clevis import get_config

    config = get_config(BasewebConfig, name="baseweb")
    assert config.name == "app"
    assert config.socketio is True
    assert config.gunicorn.workers == 1

def test_load_config_from_file(tmp_path):
    """Test loading configuration from TOML file."""
    from baseweb.config import BasewebConfig
    from clevis import get_config

    config_file = tmp_path / "baseweb.toml"
    config_file.write_text('name = "myapp"\\ntitle = "My App"')

    # Set environment to use custom config
    os.environ["BASEWEB_CONFIG"] = str(config_file)
    config = get_config(BasewebConfig, name="baseweb")
    assert config.name == "myapp"
    assert config.title == "My App"

def test_config_env_override(monkeypatch):
    """Test environment variable override."""
    from baseweb.config import BasewebConfig
    from clevis import get_config

    monkeypatch.setenv("APP_NAME", "env-app")

    config = get_config(BasewebConfig, name="baseweb")
    assert config.name == "env-app"

def test_invalid_toml(tmp_path):
    """Test error handling for invalid TOML."""
    from baseweb.config import BasewebConfig
    from clevis import get_config, ConfigError

    config_file = tmp_path / "baseweb.toml"
    config_file.write_text('name = "unclosed')

    os.environ["BASEWEB_CONFIG"] = str(config_file)
    with pytest.raises(ConfigError):
        get_config(BasewebConfig, name="baseweb")

def test_baseweb_with_config():
    """Test Baseweb with BasewebConfig."""
    from baseweb import Baseweb
    from baseweb.config import BasewebConfig

    config = BasewebConfig(name="test-app")
    app = Baseweb(config)
    assert app.config.name == "test-app"
```

### 7. Documentation

**Files to Create/Update:**

1. **`docs/configuration.md`** - Configuration reference
2. **`docs/cli.md`** - CLI command reference
3. **`README.md`** - Quick start section
4. **`CHANGELOG.md`** - Configuration feature entry

**Configuration Reference Sections:**

```markdown
# Configuration Reference

## Configuration File

Baseweb uses TOML configuration files with the following structure:

```toml
# Application entry point (required)
app_uri = "app:asgi_app"

# Application metadata (optional)
name = "myapp"
title = "My Application"
description = "A baseweb application"
author = "Your Name"

# Application style
style = "web"  # or "pwa" for Progressive Web App

# WebSocket support
socketio = true

# Gunicorn server configuration
[gunicorn]
bind = "0.0.0.0:8000"
workers = 1
worker_class = "uvicorn.workers.UvicornWorker"
```

## Configuration Priority

Configuration is loaded in the following order (later sources override earlier):

1. **Defaults**: Built-in default values
2. **User-level**: `~/.baseweb.toml`
3. **Project-level**: `./baseweb.toml`
4. **Environment variables**: `APP_*` and `GUNICORN_*`
5. **CLI arguments**: `--name`, `--port`, etc.

## Environment Variables

| Variable | TOML Path | Description |
|----------|-----------|-------------|
| `APP_NAME` | `name` | Application name |
| `APP_TITLE` | `title` | Application title |
| `APP_STYLE` | `style` | Application style (web/pwa) |
| `APP_SOCKETIO` | `socketio` | WebSocket support (true/false) |
| `BASEWEB_CONFIG` | - | Custom config file path |
| `GUNICORN_BIND` | `gunicorn.bind` | Server bind address |
| `GUNICORN_WORKERS` | `gunicorn.workers` | Number of workers |
```

---

## Implementation Plan

### Phase 1: Core Configuration System

**Task 1.1: Create Configuration Module**
- Create `src/baseweb/config.py`
- Define `BasewebConfig` and `GunicornConfig` dataclasses
- Add configuration validation with clear error messages
- Document use of `get_config(BasewebConfig, name="baseweb")`

**Task 1.2: Integrate with Baseweb Class**
- Update `__init__` to accept BasewebConfig directly
- Remove environment variable loading from `__init__`
- Users call `Baseweb(get_config(BasewebConfig, name="baseweb"))` directly

**Task 1.3: Add Tests**
- Create `tests/test_config.py`
- Add tests for all configuration loading paths
- Add tests for environment variable override
- Add tests for error handling

### Phase 2: CLI Commands

**Task 2.1: Refactor CLI Module**
- Update `src/baseweb/__main__.py`
- Add `init` command
- Add `config` command
- Add `version` command
- Add `check` command (NEW)
- Improve `serve` command

**Task 2.2: Add CLI Tests**
- Create `tests/test_cli.py`
- Add tests for all CLI commands
- Add tests for argument parsing
- Add tests for error messages

### Phase 3: Documentation

**Task 3.1: Configuration Documentation**
- Create `docs/configuration.md`
- Document all configuration options
- Document priority order
- Document environment variables

**Task 3.2: CLI Documentation**
- Create `docs/cli.md`
- Document all CLI commands
- Add usage examples
- Add troubleshooting guide

**Task 3.3: Update README**
- Add quick start section
- Add configuration example
- Add CLI usage example

---

## Acceptance Criteria

### Functional Requirements

- [ ] **FR1**: Configuration loaded from TOML files via Clevis
- [ ] **FR2**: Environment variables override TOML configuration
- [ ] **FR3**: CLI arguments override environment variables
- [ ] **FR4**: `Baseweb(get_config(BasewebConfig, name="baseweb"))` creates app from TOML
- [ ] **FR5**: `baseweb init` creates default configuration file
- [ ] **FR6**: `baseweb serve` runs application from TOML
- [ ] **FR7**: `baseweb config` displays current configuration
- [ ] **FR8**: `baseweb version` displays version
- [ ] **FR9**: `baseweb check` validates configuration without running
- [ ] **FR10**: Clear error messages for all failure cases
- [ ] **FR11**: Baseweb.__init__ accepts BasewebConfig directly

### Non-Functional Requirements

- [ ] **NFR1**: All code passes `ruff` linting
- [ ] **NFR2**: Type hints on all public functions
- [ ] **NFR3**: Docstrings on all public modules/classes
- [ ] **NFR4**: Test coverage >= 80%
- [ ] **NFR5**: Configuration validation errors are user-friendly
- [ ] **NFR6**: Documentation covers all configuration options

---

## Migration Guide

### Clean Break from Environment Variables

**This is a breaking change.** The new configuration system uses BasewebConfig dataclasses populated by Clevis. The old environment variable and settings dict approach is no longer supported.

### For Users Running `gunicorn` Directly

**Before:**
```bash
gunicorn -k uvicorn.workers.UvicornWorker "app:asgi_app"
```

**After:**
```bash
# Create config file
baseweb init

# Edit baseweb.toml
app_uri = "app:asgi_app"

# Run
baseweb serve
```

### For Users Using Environment Variables

**Before:**
```bash
APP_NAME="myapp" APP_TITLE="My App" gunicorn -k uvicorn.workers.UvicornWorker "app:asgi_app"
```

**After:**
```bash
# Create baseweb.toml
name = "myapp"
title = "My App"

# Environment variables still work for overrides (via Clevis)
APP_NAME="custom" baseweb serve
```

### For Users Creating Baseweb Programmatically

**Before (no longer supported):**
```python
from baseweb import Baseweb

# OLD: Environment variables (removed)
os.environ["APP_NAME"] = "myapp"
server = Baseweb()

# OLD: Settings dict (removed)
server = Baseweb(settings={"name": "myapp"})
```

**After (NEW):**
```python
from baseweb import Baseweb
from baseweb.config import BasewebConfig
from clevis import get_config

# From config object (for programmatic use)
config = BasewebConfig(name="myapp", title="My App")
app = Baseweb(config)

# From TOML file (recommended)
app = Baseweb(get_config(BasewebConfig, name="baseweb"))
```

---

## Design Decisions

### Decision 1: Clevis as Configuration Loading Mechanism

**Rationale:**
- Clevis provides a mature, tested configuration system
- Built-in support for layered configuration
- Automatic environment variable handling
- Type-safe dataclass population
- CLI argument generation from config schema

**Trade-offs:**
- Adds Clevis as a dependency
- Less control over configuration loading
- Must conform to Clevis conventions

**Alternatives Considered:**
- Manual TOML parsing + environment variable handling (more code, more bugs)
- dynaconf (heavier, more complex)
- python-dotenv (only handles .env files, not layered config)

### Decision 2: BasewebConfig as Single Source of Truth

**Rationale:**
- All configuration in one place
- Type-safe with dataclasses
- IDE support for autocomplete
- Documentation can reference single schema

**Trade-offs:**
- Larger dataclass with all fields
- Must import dataclass to create programmatically

### Decision 3: No Backward Compatibility

**Rationale:**
- Clean architecture without legacy code
- Avoids confusion between old and new approaches
- Simpler implementation and testing
- Clear migration path for users

**Trade-offs:**
- Breaking change for existing users
- Requires migration effort
- May frustrate users with working setups

**Mitigation:**
- Clear migration guide
- Version bump to indicate breaking change
- Release notes highlighting breaking changes

### Decision 4: `check` Command for Configuration Validation

**Rationale:**
- Fail fast before trying to run
- Clear error messages for configuration issues
- Useful for CI/CD pipelines
- Helps users debug configuration problems

**Trade-offs:**
- Additional command to maintain
- Duplicates some validation logic

---

## References

- [Clevis Documentation](https://github.com/christophevg/clevis)
- [Gunicorn Configuration](https://docs.gunicorn.org/en/stable/settings.html)
- [TOML Specification](https://toml.io)
- [Quart Configuration](https://pgjones.gitlab.io/quart/configuration.html)