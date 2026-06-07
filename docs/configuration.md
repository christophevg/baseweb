# Configuration Reference

Baseweb uses a unified configuration system based on TOML files and environment variables, powered by the Clevis library. This document provides a complete reference for all configuration options.

## Overview

Configuration in Baseweb follows a **layered approach** where values from different sources are merged according to priority. This allows you to:

- Store default configuration in TOML files
- Override specific values with environment variables
- Further customize via command-line arguments
- Maintain separate configurations for different environments

## Configuration Priority

Baseweb loads configuration from multiple sources in the following order (highest priority wins):

1. **CLI arguments** - Command-line flags (e.g., `--server-bind :8080`)
2. **Environment variables** - `APP_*` and `GUNICORN_*` variables
3. **Project-level TOML** - `./baseweb.toml` in current directory
4. **User-level TOML** - `~/.baseweb.toml` in home directory
5. **Dataclass defaults** - Built-in default values

**Example:**

```toml
# ./baseweb.toml (priority 3)
name = "myapp"
server.workers = 2
```

```bash
# Environment variable (priority 2 - higher)
export APP_NAME="production-app"
export GUNICORN_WORKERS=4

# CLI argument (priority 1 - highest)
baseweb serve --name "cli-app" --server-workers 8
# Result: name="cli-app", workers=8
```

## TOML Configuration File

### File Location

By default, Baseweb looks for configuration in:

1. **Project-level**: `./baseweb.toml` (current directory)
2. **User-level**: `~/.baseweb.toml` (home directory)

You can specify a custom configuration file using the `BASEWEB_CONFIG` environment variable:

```bash
export BASEWEB_CONFIG=/path/to/custom.toml
baseweb serve
```

### Creating a Configuration File

Use the `init` command to create a default configuration file:

```bash
baseweb init
# Creates: baseweb.toml

# Custom location
baseweb init --config myapp.toml

# Overwrite existing
baseweb init --force
```

### TOML Structure Overview

Baseweb uses nested TOML sections for logical grouping of related settings:

```toml
# Root level - Application metadata
app_uri = "app:asgi_app"
name = "myapp"
title = "My Application"
style = "web"

# Nested sections for organized configuration
[branding.colors]
scheme = "dark"
primary = "rgb(21, 101, 192)"

[features.socketio]
enabled = true

[server]
bind = "0.0.0.0:8000"
workers = 1
```

## Configuration Sections

### Root Level Fields

These fields configure the application's identity and basic behavior:

```toml
# Application entry point (required)
app_uri = "app:asgi_app"

# Application metadata
name = "myapp"
title = "My Application"
short_name = "MyApp"
description = "A Progressive Web App built with baseweb"
author = "Your Name"
version = "1.0.0"  # Optional, not currently used by baseweb

# URLs and paths
url = "https://myapp.example.com"
main_template = "main.html"

# Application style
style = "web"  # or "pwa" for Progressive Web App

# Connection management
keep_alive = false
```

#### Field Reference

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `app_uri` | string | `"app:asgi_app"` | Application entry point in `module:variable` format |
| `name` | string | *directory name* | Application name (used as Quart app name) |
| `title` | string | *directory name* | Application title (displayed in UI) |
| `short_name` | string | None | Short name for PWA (defaults to camelCase of name) |
| `author` | string | `"Unknown Author"` | Application author |
| `description` | string | `"A baseweb app"` | Application description |
| `version` | string | None | Application version (optional, not used by baseweb) |
| `url` | string | None | Application URL (optional) |
| `main_template` | string | None | Path to main template file |
| `style` | string | `"web"` | Application style: `"web"` or `"pwa"` |
| `keep_alive` | boolean | `false` | Enable keep-alive connections |

### Branding Configuration

The `[branding]` section contains nested configuration for colors, icons, and favicon.

#### Branding Colors

```toml
[branding.colors]
scheme = "dark"
primary = "rgb(21, 101, 192)"
primary_name = "blue"
background = "rgb(30, 30, 30)"
```

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `scheme` | string | `"dark"` | Color scheme: `"dark"` or `"light"` |
| `primary` | string | `"rgb(21, 101, 192)"` | Primary color as CSS color value |
| `primary_name` | string | `"blue"` | Color name for Vuetify theme (e.g., `"blue"`, `"red"`) |
| `background` | string | `"rgb(21, 101, 192)"` | Background color for the application |

#### Branding Icons

```toml
[branding.icons]
app = "static/icons/app.png"
social = "static/icons/social.png"
```

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `app` | string | None | Path to application icon |
| `social` | string | None | Path to social media preview image |

#### Branding Favicon

```toml
[branding.favicon]
enabled = true
safari_mask_color = "rgb(21, 101, 192)"
windows_tile_color = "rgb(21, 101, 192)"
```

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `enabled` | boolean | `false` | Enable favicon generation |
| `safari_mask_color` | string | None | Safari pinned tab mask color |
| `windows_tile_color` | string | None | Windows tile color |

### Features Configuration

The `[features]` section contains nested configuration for SocketIO and PWA features.

#### SocketIO Feature

```toml
[features.socketio]
enabled = true
```

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `enabled` | boolean | `true` | Enable WebSocket support via SocketIO |

#### PWA Feature

```toml
[features.pwa]
display = "standalone"
orientation = "portrait"
start_url = "/"
theme_color = "rgb(21, 101, 192)"
background_color = "rgb(21, 101, 192)"
icons_dir = "static/icons"  # Required when style = "pwa"
```

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `display` | string | `"standalone"` | Display mode: `"standalone"`, `"fullscreen"`, `"minimal-ui"`, `"browser"` |
| `orientation` | string | `"portrait"` | Preferred orientation: `"portrait"`, `"landscape"`, `"any"` |
| `start_url` | string | `"/"` | Start URL for PWA |
| `theme_color` | string | `"rgb(21, 101, 192)"` | Theme color for browser UI |
| `background_color` | string | `"rgb(21, 101, 192)"` | Background color for splash screen |
| `icons_dir` | string | None | **Required when `style = "pwa"`**: Directory containing PWA icons |

**Important**: When `style = "pwa"`, the `icons_dir` field is **required**. Baseweb will validate this during the `check` command.

### Server Configuration

The `[server]` section configures the Gunicorn server (replacing the old `[gunicorn]` section with a more generic name):

```toml
[server]
bind = "0.0.0.0:8000"
workers = 1
worker_class = "uvicorn.workers.UvicornWorker"
timeout = 120
keepalive = 5
```

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `bind` | string | `"0.0.0.0:8000"` | Socket to bind: `"host:port"` or `"unix:/path"` |
| `workers` | integer | `1` | Number of worker processes |
| `worker_class` | string | `"uvicorn.workers.UvicornWorker"` | Worker class type |
| `timeout` | integer | `120` | Worker timeout in seconds |
| `keepalive` | integer | `5` | Keep-alive connection timeout |

### Application-Specific Configuration

Applications can register custom configuration sections using the `register_app_config()` pattern:

```python
from dataclasses import dataclass
from baseweb.config import register_app_config

@dataclass
class MyAppConfig:
    """Application-specific configuration."""
    debug: bool = False
    custom_setting: str = "default"

# Register the configuration
register_app_config("myapp", MyAppConfig)
```

Then use in your TOML file:

```toml
[app.myapp]
debug = false
custom_setting = "custom value"
```

**Note**: Configuration registered this way will be available as:
- TOML: `[app.{name}]` section
- Environment: `APP_{NAME}_*` variables
- Config object: `config.app.{name}`

## Environment Variables

Baseweb automatically maps environment variables to configuration fields based on naming conventions.

### Application Variables

Environment variables with the `APP_` prefix map to root-level configuration fields:

| Environment Variable | TOML Path | Description |
|---------------------|-----------|-------------|
| `APP_NAME` | `name` | Application name |
| `APP_TITLE` | `title` | Application title |
| `APP_SHORT_NAME` | `short_name` | PWA short name |
| `APP_AUTHOR` | `author` | Application author |
| `APP_DESCRIPTION` | `description` | Application description |
| `APP_VERSION` | `version` | Application version |
| `APP_URL` | `url` | Application URL |
| `APP_STYLE` | `style` | Application style (`web`/`pwa`) |
| `APP_URI` | `app_uri` | Application entry point |

### Server Variables

Environment variables with the `GUNICORN_` prefix map to server configuration:

| Environment Variable | TOML Path | Description |
|---------------------|-----------|-------------|
| `GUNICORN_BIND` | `server.bind` | Server bind address |
| `GUNICORN_WORKERS` | `server.workers` | Number of workers |
| `GUNICORN_WORKER_CLASS` | `server.worker_class` | Worker class type |
| `GUNICORN_TIMEOUT` | `server.timeout` | Worker timeout |
| `GUNICORN_KEEPALIVE` | `server.keepalive` | Keep-alive timeout |

### Nested Configuration

For nested configuration sections, use double underscores (`__`) to separate levels:

```bash
# [branding.colors]
export APP_BRANDING_COLORS_SCHEME="light"
export APP_BRANDING_COLORS_PRIMARY="rgb(255, 255, 255)"

# [features.pwa]
export APP_FEATURES_PWA_DISPLAY="fullscreen"
export APP_FEATURES_PWA_ICONS_DIR="static/pwa-icons"

# [server]
export GUNICORN_BIND="0.0.0.0:3000"
export GUNICORN_WORKERS=4
```

### Custom Config File Path

Use `BASEWEB_CONFIG` to specify a custom configuration file:

```bash
export BASEWEB_CONFIG=/path/to/config.toml
baseweb serve
```

## Environment Variable Interpolation

TOML configuration files support environment variable interpolation using the `${VAR:-default}` syntax:

### Basic Interpolation

```toml
# Use environment variable value
name = "${APP_NAME}"
url = "${APP_URL}"

# With default value (if variable not set)
name = "${APP_NAME:-myapp}"
url = "${APP_URL:-http://localhost:8000}"
```

### Nested Values

Combine multiple environment variables:

```toml
[server]
bind = "${HOST:-0.0.0.0}:${PORT:-8000}"
```

### Configuration Priority Example

```toml
# baseweb.toml
name = "${APP_NAME:-myapp}"
title = "${APP_TITLE:-My Application}"

[server]
bind = "${GUNICORN_BIND:-0.0.0.0:8000}"
workers = "${GUNICORN_WORKERS:-1}"
```

**Priority order:**

1. CLI arguments: `--name "cli-app"`
2. Environment variables: `APP_NAME="env-app"`
3. TOML with interpolation: `name = "${APP_NAME:-myapp}"`
4. Default in TOML: `name = "myapp"`
5. Dataclass default: `name = "app"`

## register_app_config() Pattern

For applications that need custom configuration beyond the built-in fields:

### 1. Define Your Configuration

```python
from dataclasses import dataclass, field

@dataclass
class DatabaseConfig:
    """Database configuration."""
    host: str = "localhost"
    port: int = 5432
    database: str = "myapp"
    user: str = "postgres"
    password: str = ""

@dataclass
class AuthConfig:
    """Authentication configuration."""
    enabled: bool = True
    provider: str = "oauth2"
    client_id: str = ""
    client_secret: str = ""

@dataclass
class MyAppConfig:
    """Application-specific configuration."""
    debug: bool = False
    
    # Nested configuration
    database: DatabaseConfig = field(default_factory=DatabaseConfig)
    auth: AuthConfig = field(default_factory=AuthConfig)
```

### 2. Register the Configuration

```python
from baseweb.config import register_app_config

# Register before loading configuration
register_app_config("myapp", MyAppConfig)
```

### 3. Use in TOML

```toml
# Application-specific configuration
[app.myapp]
debug = true

[app.myapp.database]
host = "${DB_HOST:-localhost}"
port = "${DB_PORT:-5432}"
database = "production_db"

[app.myapp.auth]
enabled = true
provider = "oauth2"
client_id = "${OAUTH_CLIENT_ID}"
client_secret = "${OAUTH_CLIENT_SECRET}"
```

### 4. Access in Your Application

```python
from baseweb import Baseweb
from baseweb.config import BasewebConfig
from clevis import get_config

# Load configuration (includes app.myapp section)
config = get_config(BasewebConfig, name="baseweb")

# Access custom configuration
db_host = config.app.myapp.database.host
auth_enabled = config.app.myapp.auth.enabled
```

## Migration Guide: Environment Variables to TOML

If you're migrating from the old environment-variable-only approach:

### Before (Environment Variables Only)

```bash
# Old approach - environment variables only
export APP_NAME="myapp"
export APP_TITLE="My Application"
export APP_STYLE="pwa"
export GUNICORN_BIND="0.0.0.0:8080"
export GUNICORN_WORKERS=4

# Run with environment variables
gunicorn -k uvicorn.workers.UvicornWorker "app:asgi_app"
```

### After (TOML Configuration)

```bash
# Create TOML configuration file
baseweb init
# Edit baseweb.toml with your settings
```

```toml
# baseweb.toml
app_uri = "app:asgi_app"
name = "myapp"
title = "My Application"
style = "pwa"

[server]
bind = "0.0.0.0:8080"
workers = 4
```

```bash
# Run with configuration file
baseweb serve

# Environment variables still work for overrides
APP_TITLE="Production" baseweb serve
```

### Migration Steps

1. **Generate default configuration:**
   ```bash
   baseweb init
   ```

2. **Convert environment variables to TOML:**
   - Move `APP_*` values to TOML fields
   - Move `GUNICORN_*` values to `[server]` section
   - Use environment variable interpolation for secrets

3. **Update application code:**
   ```python
   # OLD - Environment variables (no longer supported)
   import os
   from baseweb import Baseweb
   
   os.environ["APP_NAME"] = "myapp"
   server = Baseweb()  # Error: no longer supported
   
   # NEW - BasewebConfig
   from baseweb import Baseweb
   from baseweb.config import BasewebConfig
   from clevis import get_config
   
   # From config object (for programmatic use)
   config = BasewebConfig(name="myapp", title="My App")
   app = Baseweb(config)
   
   # From TOML file (recommended)
   config = get_config(BasewebConfig, name="baseweb")
   app = Baseweb(config)
   ```

4. **Test configuration:**
   ```bash
   # Validate configuration
   baseweb check
   
   # View current configuration
   baseweb config
   ```

## Common Use Cases

### Development Environment

```toml
# baseweb.toml (development)
app_uri = "app:asgi_app"
name = "myapp-dev"
title = "My App (Development)"
style = "web"

[branding.colors]
scheme = "light"

[features.socketio]
enabled = true

[server]
bind = "127.0.0.1:8000"
workers = 1
```

### Production Environment

```toml
# baseweb.toml (production)
app_uri = "app:asgi_app"
name = "${APP_NAME:-myapp}"
title = "${APP_TITLE:-My Application}"
style = "pwa"

[branding.colors]
scheme = "dark"
primary = "${BRANDING_PRIMARY:-rgb(21, 101, 192)}"

[features.socketio]
enabled = true

[features.pwa]
display = "standalone"
orientation = "portrait"
start_url = "/"
theme_color = "${BRANDING_PRIMARY:-rgb(21, 101, 192)}"
icons_dir = "static/pwa-icons"

[server]
bind = "${GUNICORN_BIND:-0.0.0.0:8000}"
workers = "${GUNICORN_WORKERS:-4}"
worker_class = "uvicorn.workers.UvicornWorker"
timeout = 120
keepalive = 5
```

### Progressive Web App (PWA)

```toml
# baseweb.toml (PWA)
app_uri = "app:asgi_app"
name = "my-pwa"
title = "My Progressive Web App"
short_name = "MyPWA"
style = "pwa"

[branding.colors]
scheme = "dark"
primary = "rgb(21, 101, 192)"
background = "rgb(30, 30, 30)"

[branding.icons]
app = "static/icons/icon-512x512.png"
social = "static/icons/social.png"

[branding.favicon]
enabled = true
safari_mask_color = "rgb(21, 101, 192)"
windows_tile_color = "rgb(21, 101, 192)"

[features.socketio]
enabled = true

[features.pwa]
display = "standalone"
orientation = "portrait"
start_url = "/"
theme_color = "rgb(21, 101, 192)"
background_color = "rgb(30, 30, 30)"
icons_dir = "static/pwa-icons"  # REQUIRED for PWA

[server]
bind = "0.0.0.0:8000"
workers = 2
```

### Docker/Kubernetes Deployment

```toml
# baseweb.toml (containerized)
app_uri = "app:asgi_app"
name = "${APP_NAME:-myapp}"
title = "${APP_TITLE:-My Application}"
style = "${APP_STYLE:-web}"

[branding.colors]
scheme = "${BRANDING_SCHEME:-dark}"
primary = "${BRANDING_PRIMARY:-rgb(21, 101, 192)}"

[features.socketio]
enabled = true

[server]
bind = "0.0.0.0:${PORT:-8000}"
workers = "${GUNICORN_WORKERS:-2}"
worker_class = "uvicorn.workers.UvicornWorker"
timeout = "${GUNICORN_TIMEOUT:-120}"
keepalive = "${GUNICORN_KEEPALIVE:-5}"
```

**Container environment:**

```bash
# Kubernetes ConfigMap or Docker Compose
export APP_NAME="production-app"
export APP_TITLE="Production Application"
export APP_STYLE="pwa"
export PORT="8080"
export GUNICORN_WORKERS="4"
export BRANDING_SCHEME="dark"
export BRANDING_PRIMARY="rgb(0, 150, 136)"
```

### Multi-Environment Configuration

Use different configuration files for different environments:

```bash
# Directory structure
config/
  ├── development.toml
  ├── staging.toml
  └── production.toml

# Run with specific configuration
BASEWEB_CONFIG=config/production.toml baseweb serve

# Or with environment variable
export BASEWEB_CONFIG=config/staging.toml
baseweb serve
```

## CLI Commands

### View Current Configuration

```bash
# Display configuration as formatted table
baseweb config

# Display configuration as TOML
baseweb config --format toml
```

### Validate Configuration

```bash
# Validate configuration file
baseweb check

# Validate with specific app-uri
baseweb check --app-uri app:asgi_app
```

### Initialize Configuration

```bash
# Create default configuration file
baseweb init

# Custom location
baseweb init --config myapp.toml

# Overwrite existing
baseweb init --force
```

### Run Application

```bash
# Run with configuration file
baseweb serve

# Override specific settings
baseweb serve --name "custom-app" --server-bind :8080 --server-workers 4
```

## Troubleshooting

### Configuration Not Loading

**Symptom:** Configuration values not being applied.

**Possible causes:**

1. **File not found:** Ensure `baseweb.toml` exists in current directory
   ```bash
   ls -la baseweb.toml
   baseweb init  # Create if missing
   ```

2. **Invalid TOML syntax:** Validate TOML syntax
   ```bash
   baseweb check
   ```

3. **Wrong configuration file:** Specify custom file
   ```bash
   BASEWEB_CONFIG=/path/to/config.toml baseweb serve
   ```

4. **Environment variable override:** Check if environment variables are overriding
   ```bash
   # View current configuration
   baseweb config
   
   # Check environment
   env | grep -E '^(APP_|GUNICORN_)'
   ```

### Environment Variables Not Working

**Symptom:** Environment variables not overriding TOML values.

**Possible causes:**

1. **Wrong variable name:** Use correct prefix
   ```bash
   # Correct
   export APP_NAME="myapp"
   export GUNICORN_WORKERS=4
   
   # Wrong
   export NAME="myapp"  # Missing APP_ prefix
   export WORKERS=4     # Missing GUNICORN_ prefix
   ```

2. **Nested field naming:** Use double underscores for nested fields
   ```bash
   # Correct
   export APP_BRANDING_COLORS_SCHEME="light"
   
   # Wrong
   export APP_BRANDING_COLORS_SCHEME="light"  # Single underscore
   ```

3. **TOML interpolation syntax:** Use `${VAR:-default}` syntax
   ```toml
   # Correct
   name = "${APP_NAME:-myapp}"
   
   # Wrong
   name = "$APP_NAME"  # Missing braces
   ```

### PWA Icons Directory Required

**Symptom:** Error when running PWA application.

**Error message:**
```
ERROR: icons_dir is required when style='pwa'
```

**Solution:** Add `icons_dir` to `[features.pwa]` section:

```toml
style = "pwa"

[features.pwa]
display = "standalone"
icons_dir = "static/pwa-icons"  # Required for PWA
```

### Cannot Import Application

**Symptom:** Error when importing `app_uri`.

**Error message:**
```
ERROR: Cannot import app_uri 'app:asgi_app': Module 'app' not found
```

**Possible causes:**

1. **Wrong directory:** Run from project root
   ```bash
   cd /path/to/project
   baseweb serve
   ```

2. **Wrong app_uri format:** Use `module:variable` format
   ```toml
   # Correct
   app_uri = "app:asgi_app"
   
   # Wrong
   app_uri = "app"  # Missing variable
   app_uri = "app.asgi_app"  # Wrong separator
   ```

3. **Module doesn't exist:** Check module file
   ```bash
   ls -la app.py
   python -c "import app; print(dir(app))"
   ```

### Configuration Priority Confusion

**Symptom:** Unexpected configuration values.

**Debug approach:**

1. **Check current configuration:**
   ```bash
   baseweb config
   ```

2. **Check configuration priority:**
   ```bash
   # CLI args (highest priority)
   baseweb serve --name "cli-override"
   
   # Environment variables (medium priority)
   APP_NAME="env-override" baseweb serve
   
   # TOML file (low priority)
   # baseweb.toml: name = "toml-default"
   ```

3. **Check environment variables:**
   ```bash
   env | grep -E '^(APP_|GUNICORN_|BASEWEB_)'
   ```

4. **Check TOML interpolation:**
   ```bash
   # TOML: name = "${APP_NAME:-default}"
   # Priority: APP_NAME env var > TOML default value
   ```

### Validation Errors

**Symptom:** `baseweb check` fails.

**Common validation errors:**

1. **Missing required field:**
   ```
   ERROR: app_uri is required
   ```
   **Solution:** Add `app_uri` to configuration:
   ```toml
   app_uri = "app:asgi_app"
   ```

2. **PWA icons_dir required:**
   ```
   ERROR: icons_dir is required when style='pwa'
   ```
   **Solution:** Add icons directory:
   ```toml
   style = "pwa"
   [features.pwa]
   icons_dir = "static/pwa-icons"
   ```

3. **Cannot import module:**
   ```
   ERROR: Cannot import app_uri 'app:asgi_app': Module 'app' not found
   ```
   **Solution:** Check module exists and app_uri format is correct.

### Debugging Configuration

**View merged configuration:**

```bash
# View as table
baseweb config

# View as TOML
baseweb config --format toml

# Validate and show details
baseweb check
```

**Test configuration:**

```bash
# Test specific configuration file
BASEWEB_CONFIG=test.toml baseweb check

# Test with environment overrides
APP_NAME="test" baseweb check

# Test with CLI overrides
baseweb check --name "test" --server-bind :8080
```

## Complete Configuration Example

Here's a complete example showing all available configuration options:

```toml
# baseweb.toml - Complete configuration example

# Application entry point (required)
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

# Connection management
keep_alive = false

# Branding configuration
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

# Features configuration
[features.socketio]
enabled = true

[features.pwa]
display = "standalone"
orientation = "portrait"
start_url = "/"
theme_color = "rgb(21, 101, 192)"
background_color = "rgb(30, 30, 30)"
icons_dir = "static/pwa-icons"  # Required when style = "pwa"

# Server configuration
[server]
bind = "0.0.0.0:8000"
workers = 1
worker_class = "uvicorn.workers.UvicornWorker"
timeout = 120
keepalive = 5

# Application-specific configuration (example)
[app.myapp]
debug = false
custom_setting = "value"

[app.myapp.database]
host = "${DB_HOST:-localhost}"
port = 5432
database = "myapp_db"
```

## See Also

- **CLI Reference**: `docs/cli.md` (if available)
- **Migration Guide**: `docs/migration-guide.md`
- **Getting Started**: `docs/getting-started.md`
- **Design Documentation**: `analysis/cli-design.md`, `analysis/cli-design-decisions.md`

## Further Reading

- [Clevis Documentation](https://github.com/christophevg/clevis) - Configuration loading library
- [TOML Specification](https://toml.io) - TOML file format
- [Gunicorn Configuration](https://docs.gunicorn.org/en/stable/settings.html) - Server configuration reference