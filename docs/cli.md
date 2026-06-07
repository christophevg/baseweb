# Baseweb CLI Reference

The Baseweb CLI provides a command-line interface for managing and running baseweb applications. This document covers all available commands, options, and common workflows.

## Installation

```bash
pip install baseweb
```

The CLI is automatically installed with the `baseweb` package. You can verify the installation:

```bash
baseweb version
```

## Overview

The Baseweb CLI offers five commands for managing your application:

| Command | Description |
|---------|-------------|
| `baseweb init` | Create default `baseweb.toml` configuration file |
| `baseweb check` | Validate configuration without running |
| `baseweb config` | Display current configuration |
| `baseweb serve` | Run application from TOML config |
| `baseweb version` | Display baseweb version |

## Command Reference

### baseweb init

Create a default `baseweb.toml` configuration file in the current directory.

#### Usage

```bash
baseweb init [OPTIONS]
```

#### Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `--config`, `-c` | string | `baseweb.toml` | Path to configuration file |
| `--force`, `-f` | flag | - | Overwrite existing file |

#### Description

The `init` command creates a new `baseweb.toml` file with default settings. This file contains all configuration options with sensible defaults that you can customize for your application.

#### Examples

```bash
# Create default configuration file
baseweb init
# Creates: baseweb.toml

# Create configuration in custom location
baseweb init --config myapp.toml
# Creates: myapp.toml

# Overwrite existing configuration
baseweb init --force
# Overwrites: baseweb.toml
```

#### Output

```
Created baseweb.toml (permissions: 600)
Edit this file to customize your baseweb application
```

#### What Gets Created

The generated file includes:

```toml
# Application entry point
app_uri = "app:asgi_app"

# Application metadata
name = "myapp"
title = "A baseweb app"
author = "Unknown Author"
description = "A baseweb app"

# Server configuration
[server]
bind = "0.0.0.0:8000"
workers = 1
worker_class = "uvicorn.workers.UvicornWorker"
timeout = 120
keepalive = 5

# Features
[features.socketio]
enabled = true

# Branding
[branding.colors]
scheme = "dark"
primary = "rgb(21, 101, 192)"
primary_name = "blue"
background = "rgb(21, 101, 192)"
```

#### Security

The generated file is created with restricted permissions (600 - owner read/write only) to protect sensitive configuration values.

---

### baseweb check

Validate configuration without running the application.

#### Usage

```bash
baseweb check [OPTIONS]
```

#### Options

The `check` command accepts all configuration options that `serve` accepts, allowing you to test specific configurations:

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `--config`, `-c` | string | `baseweb.toml` | Path to configuration file |
| `--app-uri` | string | `app:asgi_app` | Application entry point |
| `--name` | string | - | Application name |
| `--title` | string | - | Application title |
| `--server-bind` | string | `0.0.0.0:8000` | Server bind address |
| `--server-workers` | integer | `1` | Number of workers |

#### Description

The `check` command validates your configuration before attempting to run the application. It performs several checks:

1. **Configuration Loading**: Verifies TOML file can be parsed
2. **Required Fields**: Ensures `app_uri` is specified
3. **PWA Validation**: Checks `icons_dir` is present when `style = "pwa"`
4. **Application Import**: Tests that the application can be imported

#### Examples

```bash
# Validate default configuration file
baseweb check

# Validate with specific app-uri
baseweb check --app-uri app:asgi_app

# Validate with custom config file
BASEWEB_CONFIG=production.toml baseweb check

# Check specific configuration
baseweb check --name "myapp" --server-workers 4
```

#### Output (Success)

```
Configuration is valid
  App: myapp
  Title: My Application
  Entry: app:asgi_app
  Style: web
  Bind: 0.0.0.0:8000
  Workers: 1
```

#### Output (Failure)

```
ERROR: icons_dir is required when style='pwa'
  Field: features.pwa.icons_dir
  Add [features.pwa] section with icons_dir = "static/icons"
```

#### Use Cases

- **Pre-deployment validation**: Check configuration before deploying
- **CI/CD pipelines**: Fail fast on configuration errors
- **Debugging**: Identify configuration issues without running
- **Migration**: Validate configuration after updates

---

### baseweb config

Display current configuration values.

#### Usage

```bash
baseweb config [OPTIONS]
```

#### Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `--format` | string | `table` | Output format: `table` or `toml` |
| `--config`, `-c` | string | `baseweb.toml` | Path to configuration file |

#### Description

The `config` command shows the effective configuration after merging all sources (defaults, user-level TOML, project-level TOML, environment variables, CLI arguments). This is useful for debugging configuration issues.

#### Examples

```bash
# Display configuration as formatted table
baseweb config

# Display configuration as TOML
baseweb config --format toml

# Show configuration from specific file
BASEWEB_CONFIG=production.toml baseweb config
```

#### Output (Table Format)

```
Baseweb Configuration
============================================================

Application:
  App Uri: app:asgi_app
  Name: myapp
  Title: My Application
  Author: Your Name
  Description: A baseweb app
  Style: web

Branding Colors:
  Scheme: dark
  Primary: rgb(21, 101, 192)
  Primary Name: blue
  Background: rgb(21, 101, 192)

Features Socketio:
  Enabled: true

Server:
  Bind: 0.0.0.0:8000
  Workers: 1
  Worker Class: uvicorn.workers.UvicornWorker
  Timeout: 120
  Keepalive: 5
```

#### Output (TOML Format)

```toml
app_uri = "app:asgi_app"
name = "myapp"
title = "My Application"
author = "Your Name"
description = "A baseweb app"
style = "web"

[branding.colors]
scheme = "dark"
primary = "rgb(21, 101, 192)"
primary_name = "blue"
background = "rgb(21, 101, 192)"

[features.socketio]
enabled = true

[server]
bind = "0.0.0.0:8000"
workers = 1
worker_class = "uvicorn.workers.UvicornWorker"
timeout = 120
keepalive = 5
```

#### Use Cases

- **Debugging**: See the effective configuration after all merges
- **Export**: Generate TOML configuration from current settings
- **Documentation**: Document the active configuration
- **Comparison**: Compare configurations across environments

---

### baseweb serve

Run the baseweb application with Gunicorn.

#### Usage

```bash
baseweb serve [OPTIONS]
```

#### Options

The `serve` command accepts all configuration options:

**Application Options:**

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `--config`, `-c` | string | `baseweb.toml` | Path to configuration file |
| `--app-uri` | string | `app:asgi_app` | Application entry point (`module:variable`) |
| `--name` | string | - | Application name |
| `--title` | string | - | Application title |
| `--style` | string | `web` | Application style (`web` or `pwa`) |

**Server Options:**

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `--server-bind` | string | `0.0.0.0:8000` | Bind address (host:port) |
| `--server-workers` | integer | `1` | Number of worker processes |
| `--server-timeout` | integer | `120` | Worker timeout in seconds |
| `--server-keepalive` | integer | `5` | Keep-alive timeout |

**Note:** All nested configuration options use double-dash format (e.g., `--server-workers`, `--branding-colors-scheme`).

#### Description

The `serve` command runs your application using Gunicorn with Uvicorn workers. It loads configuration from TOML files, environment variables, and CLI arguments.

#### Configuration Priority

Values are loaded in this order (highest priority wins):

1. CLI arguments (e.g., `--server-workers 4`)
2. Environment variables (e.g., `GUNICORN_WORKERS=4`)
3. Project-level TOML (`./baseweb.toml`)
4. User-level TOML (`~/.baseweb.toml`)
5. Built-in defaults

#### Examples

```bash
# Run with configuration file
baseweb serve

# Run with custom app-uri
baseweb serve --app-uri myapp:asgi_app

# Run with custom server settings
baseweb serve --server-bind :8080 --server-workers 4

# Run with environment overrides
APP_NAME="production" baseweb serve

# Run with custom configuration file
BASEWEB_CONFIG=production.toml baseweb serve
```

#### Binding Options

The `--server-bind` option supports multiple formats:

```bash
# Bind to all interfaces, default port
--server-bind 0.0.0.0:8000

# Bind to localhost only
--server-bind 127.0.0.1:8000

# Bind to specific port (all interfaces)
--server-bind :8080

# Bind to Unix socket
--server-bind unix:/tmp/baseweb.sock
```

#### Worker Configuration

For production deployments, configure workers based on CPU cores:

```bash
# Development (1 worker)
baseweb serve --server-workers 1

# Production (2-4 workers per CPU core)
baseweb serve --server-workers 4 --server-workers 8
```

#### Background Execution

For running in background:

```bash
# Using nohup
nohup baseweb serve --server-bind :8000 &

# Using screen
screen -S baseweb
baseweb serve

# Using systemd (recommended for production)
# See deployment documentation
```

---

### baseweb version

Display the baseweb version.

#### Usage

```bash
baseweb version
```

#### Description

Prints the currently installed baseweb version number.

#### Examples

```bash
# Display version
baseweb version
# Output: 0.5.0
```

#### Use Cases

- **Version checking**: Verify installed version
- **CI/CD**: Version number in build pipelines
- **Debugging**: Report version when filing issues

---

## Common Workflows

### Starting a New Project

Create a new baseweb application from scratch:

```bash
# 1. Install baseweb
pip install baseweb gunicorn uvicorn

# 2. Create project directory
mkdir myapp
cd myapp

# 3. Create application file
cat > app.py << 'EOF'
from baseweb import Baseweb
from baseweb.config import BasewebConfig

# Create configuration
config = BasewebConfig(
    name="myapp",
    title="My Application"
)

# Create application
app = Baseweb(config)
asgi_app = app._asgi_app
EOF

# 4. Initialize configuration
baseweb init

# 5. Validate configuration
baseweb check

# 6. Run application
baseweb serve
```

Visit [http://localhost:8000](http://localhost:8000) to see your application.

### Running in Development

For local development with debugging:

```bash
# Initialize configuration
baseweb init

# Edit baseweb.toml for development
# name = "myapp-dev"
# title = "My App (Development)"
# style = "web"

# Run with single worker and verbose logging
baseweb serve --server-workers 1
```

**Development Configuration:**

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

### Running in Production

For production deployments:

```bash
# Use production configuration
BASEWEB_CONFIG=production.toml baseweb serve

# Or with environment overrides
export APP_NAME="myapp"
export APP_TITLE="My Production App"
export GUNICORN_WORKERS=4
export GUNICORN_BIND="0.0.0.0:8000"
baseweb serve
```

**Production Configuration:**

```toml
# production.toml
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
icons_dir = "static/pwa-icons"

[server]
bind = "${GUNICORN_BIND:-0.0.0.0:8000}"
workers = "${GUNICORN_WORKERS:-4}"
worker_class = "uvicorn.workers.UvicornWorker"
timeout = 120
keepalive = 5
```

### Checking Configuration

Validate configuration before deployment:

```bash
# Check default configuration
baseweb check

# Check production configuration
BASEWEB_CONFIG=production.toml baseweb check

# Check with specific settings
baseweb check --app-uri app:asgi_app --server-workers 4

# View configuration being checked
baseweb config
baseweb check
```

### Viewing Configuration

Display current configuration for debugging:

```bash
# Show configuration as table
baseweb config

# Show configuration as TOML (for export)
baseweb config --format toml > current-config.toml

# Show configuration from specific file
BASEWEB_CONFIG=staging.toml baseweb config

# Show with environment variable overrides
APP_NAME="test" baseweb config
```

### Progressive Web App (PWA)

Configure for PWA deployment:

```bash
# 1. Initialize configuration
baseweb init

# 2. Edit baseweb.toml for PWA
```

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
icons_dir = "static/pwa-icons"  # Required for PWA

[server]
bind = "0.0.0.0:8000"
workers = 2
```

```bash
# 3. Create PWA icons directory
mkdir -p static/pwa-icons

# 4. Validate PWA configuration
baseweb check

# 5. Run PWA application
baseweb serve
```

### Docker/Kubernetes Deployment

Configure for containerized deployment:

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

```bash
# Build Docker image
docker build -t myapp:latest .

# Run container with environment variables
docker run -p 8000:8000 \
  -e APP_NAME=myapp \
  -e APP_TITLE="My App" \
  -e PORT=8000 \
  -e GUNICORN_WORKERS=4 \
  myapp:latest

# Kubernetes ConfigMap
kubectl create configmap baseweb-config --from-file=baseweb.toml

# Kubernetes Deployment
kubectl create deployment myapp --image=myapp:latest
kubectl set env deployment/myapp \
  APP_NAME=myapp \
  GUNICORN_WORKERS=4
```

---

## Troubleshooting

### Configuration Not Loading

**Symptom:** Configuration values not being applied from TOML file.

**Solutions:**

1. **Check file location:**
   ```bash
   ls -la baseweb.toml
   # Should show: -rw------- 1 user user ... baseweb.toml
   ```

2. **Validate TOML syntax:**
   ```bash
   baseweb check
   # Look for syntax errors
   ```

3. **Check configuration file path:**
   ```bash
   # Use custom configuration file
   BASEWEB_CONFIG=/path/to/config.toml baseweb serve
   ```

4. **View effective configuration:**
   ```bash
   baseweb config
   # Compare with expected values
   ```

### Cannot Import Application

**Error:**
```
ERROR: Cannot import app_uri 'app:asgi_app': Module 'app' not found
```

**Solutions:**

1. **Check current directory:**
   ```bash
   pwd
   # Should be project root (where app.py is located)
   ```

2. **Verify app_uri format:**
   ```toml
   # Correct format: module:variable
   app_uri = "app:asgi_app"

   # Wrong formats:
   # app_uri = "app"              # Missing variable
   # app_uri = "app.asgi_app"    # Wrong separator
   ```

3. **Check module exists:**
   ```bash
   ls -la app.py
   python -c "import app; print(dir(app))"
   ```

4. **Verify ASGI app variable:**
   ```python
   # In app.py
   app = Baseweb(config)
   asgi_app = app._asgi_app  # This is the variable name

   # app_uri should be: app:asgi_app
   ```

5. **Test import:**
   ```bash
   python -c "from app import asgi_app; print('OK')"
   ```

### Environment Variables Not Working

**Symptom:** Environment variables not overriding TOML values.

**Solutions:**

1. **Use correct prefix:**
   ```bash
   # Correct
   export APP_NAME="myapp"
   export GUNICORN_WORKERS=4

   # Wrong
   export NAME="myapp"        # Missing APP_ prefix
   export WORKERS=4           # Missing GUNICORN_ prefix
   ```

2. **Use correct naming for nested fields:**
   ```bash
   # Correct: double underscores for nested fields
   export APP_BRANDING_COLORS_SCHEME="light"
   export APP_FEATURES_PWA_DISPLAY="fullscreen"

   # Wrong: single underscores
   export APP_BRANDING_COLORS_SCHEME="light"
   ```

3. **Use TOML interpolation:**
   ```toml
   # Correct: ${VAR:-default} syntax
   name = "${APP_NAME:-myapp}"
   bind = "${GUNICORN_BIND:-0.0.0.0:8000}"

   # Wrong: missing braces
   name = "$APP_NAME"
   ```

4. **Check environment:**
   ```bash
   # Show current environment variables
   env | grep -E '^(APP_|GUNICORN_|BASEWEB_)'

   # Test configuration
   baseweb config
   ```

### PWA Icons Directory Required

**Error:**
```
ERROR: icons_dir is required when style='pwa'
```

**Solution:**

Add `icons_dir` to your PWA configuration:

```toml
style = "pwa"

[features.pwa]
display = "standalone"
orientation = "portrait"
start_url = "/"
theme_color = "rgb(21, 101, 192)"
background_color = "rgb(21, 101, 192)"
icons_dir = "static/pwa-icons"  # Required for PWA
```

**Create the directory:**
```bash
mkdir -p static/pwa-icons
# Add your PWA icons (192x192, 512x512, etc.)
```

### Configuration Priority Confusion

**Symptom:** Unexpected configuration values.

**Debugging:**

1. **View effective configuration:**
   ```bash
   baseweb config
   ```

2. **Check priority order:**
   ```bash
   # Priority: CLI args > env vars > TOML file > defaults

   # Test with different sources
   baseweb config                           # TOML + env
   APP_NAME="test" baseweb config          # Env override
   baseweb config --name "cli-test"        # CLI override
   ```

3. **Check environment:**
   ```bash
   env | grep -E '^(APP_|GUNICORN_|BASEWEB_)'
   ```

4. **Check TOML interpolation:**
   ```toml
   # name = "${APP_NAME:-default}"
   # If APP_NAME is set, use it; otherwise use "default"
   ```

### Validation Errors

**Common errors and solutions:**

1. **Missing app_uri:**
   ```
   ERROR: app_uri is required
   ```
   **Solution:** Add to configuration:
   ```toml
   app_uri = "app:asgi_app"
   ```

2. **PWA icons_dir missing:**
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
   **Solution:** Check module exists and format is correct.

### Server Already Running

**Error:**
```
[ERROR] Connection in use: ('0.0.0.0', 8000)
```

**Solutions:**

1. **Find and kill existing process:**
   ```bash
   # Find process on port 8000
   lsof -i :8000

   # Kill process
   kill -9 <PID>
   ```

2. **Use different port:**
   ```bash
   baseweb serve --server-bind :8080
   ```

3. **Use environment variable:**
   ```bash
   export GUNICORN_BIND="0.0.0.0:8080"
   baseweb serve
   ```

### Permission Denied

**Error:**
```
PermissionError: [Errno 13] Permission denied
```

**Solutions:**

1. **Check file permissions:**
   ```bash
   ls -la baseweb.toml
   # Should be readable: -rw-r--r-- or -rw-------
   ```

2. **Fix permissions:**
   ```bash
   chmod 600 baseweb.toml
   ```

3. **Check directory permissions:**
   ```bash
   # Ensure you can write to directory
   ls -la .
   ```

---

## Advanced Usage

### Multiple Configuration Files

Use different configurations for different environments:

```bash
# Directory structure
config/
  ├── development.toml
  ├── staging.toml
  └── production.toml

# Run with specific configuration
BASEWEB_CONFIG=config/production.toml baseweb serve
```

### Configuration Templates

Use TOML interpolation for flexible configurations:

```toml
# baseweb.toml
app_uri = "app:asgi_app"
name = "${APP_NAME:-myapp}"
title = "${APP_TITLE:-My Application}"

[server]
bind = "${HOST:-0.0.0.0}:${PORT:-8000}"
workers = "${GUNICORN_WORKERS:-1}"
```

```bash
# Development
export APP_NAME="myapp-dev"
export HOST="127.0.0.1"
baseweb serve

# Production
export APP_NAME="myapp-prod"
export HOST="0.0.0.0"
export PORT="8080"
export GUNICORN_WORKERS="4"
baseweb serve
```

### Combining CLI and Environment

Override configuration from multiple sources:

```bash
# Base configuration: baseweb.toml
# Environment override: GUNICORN_WORKERS=4
# CLI override: --server-bind :9000

export GUNICORN_WORKERS=4
baseweb serve --server-bind :9000
# Result: baseweb.toml + env + CLI
```

### Programmatic Configuration

Use Python to generate configuration:

```python
from baseweb.config import BasewebConfig
from baseweb import Baseweb

# Create configuration programmatically
config = BasewebConfig(
    name="myapp",
    title="My Application",
    style="pwa"
)

# Use configuration
app = Baseweb(config)
asgi_app = app._asgi_app
```

### Custom Application Configuration

Register application-specific configuration:

```python
from dataclasses import dataclass, field
from baseweb.config import register_app_config

@dataclass
class MyAppConfig:
    """Application-specific configuration."""
    debug: bool = False
    api_key: str = ""

    @dataclass
    class Database:
        host: str = "localhost"
        port: int = 5432

    database: Database = field(default_factory=Database)

# Register before loading config
register_app_config("myapp", MyAppConfig)
```

Use in TOML:

```toml
[app.myapp]
debug = true
api_key = "${API_KEY}"

[app.myapp.database]
host = "${DB_HOST:-localhost}"
port = 5432
```

---

## See Also

- **Configuration Reference**: `docs/configuration.md` - Complete configuration documentation
- **Getting Started**: `docs/getting-started.md` - Tutorial for new users
- **Migration Guide**: `docs/migration-guide.md` - Migrating from older versions
- **Design Documentation**: `analysis/cli-design.md` - CLI and configuration design

## Further Reading

- [Gunicorn Configuration](https://docs.gunicorn.org/en/stable/settings.html) - Server configuration reference
- [TOML Specification](https://toml.io) - TOML file format
- [Clevis Documentation](https://github.com/christophevg/clevis) - Configuration loading library