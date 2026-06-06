# Clevis Command Pattern - Quick Reference

## The Problem

The developer agent incorrectly reimplemented argparse instead of using Clevis's built-in command support.

**❌ Wrong: Manual argparse**
```python
def main():
    parser = argparse.ArgumentParser(...)
    subparsers = parser.add_subparsers(dest="command")

    init_parser = subparsers.add_parser("init", help="...")
    init_parser.add_argument("--config", "-c", ...)
    init_parser.set_defaults(func=cmd_init)

    # ... more manual setup ...

    args = parser.parse_args()
    args.func(args)
```

**✓ Right: Clevis commands**
```python
@configclass(cmd="init", help="Create configuration file")
class InitConfig:
    config: str = "baseweb.toml"
    force: bool = False

def main():
    cmd = get_cmd()
    if cmd == "init":
        config = get_config(InitConfig, name="baseweb")
        init(config)
```

## Clevis Command System

### 1. Decorator-Based Command Registration

Each command gets its own configclass with `cmd` parameter:

```python
from dataclasses import dataclass, field
from clevis import configclass

@configclass(cmd="serve", help="Run baseweb application")
class ServeConfig:
    app_uri: str = "app:asgi_app"
    bind: str = "0.0.0.0:8000"
    workers: int = 1

@configclass(cmd="check", help="Validate configuration", aliases=["c", "chk"])
class CheckConfig:
    verbose: bool = False

@configclass(cmd="config", help="Display configuration")
class ConfigConfig:
    format: str = "table"  # or "toml"

@configclass(cmd="init", help="Create configuration file")
class InitConfig:
    config: str = "baseweb.toml"
    force: bool = False
```

### 2. Automatic CLI Generation

Clevis generates CLI arguments from dataclass fields:

```bash
# Fields become dashed arguments
baseweb serve --app-uri myapp:app --bind :8080 --workers 4
baseweb check --verbose
baseweb config --format toml
baseweb init --config custom.toml --force
```

Boolean fields use `store_true`:

```python
@configclass(cmd="check")
class CheckConfig:
    verbose: bool = False  # --verbose flag
```

Nested fields become dashed:

```python
@configclass(cmd="serve")
class ServeConfig:
    server: ServerConfig = field(default_factory=ServerConfig)

@dataclass
class ServerConfig:
    bind: str = "0.0.0.0:8000"
    workers: int = 1

# Usage: baseweb serve --server-bind :8080 --server-workers 4
```

### 3. Command Dispatch Pattern

Use `get_cmd()` to dispatch:

```python
from clevis import get_cmd, get_config

def main():
    cmd = get_cmd()

    if cmd == "serve":
        config = get_config(ServeConfig, name="baseweb")
        serve(config)

    elif cmd == "check":
        config = get_config(CheckConfig, name="baseweb")
        check(config)

    elif cmd == "config":
        config = get_config(ConfigConfig, name="baseweb")
        show_config(config)

    elif cmd == "init":
        config = get_config(InitConfig, name="baseweb")
        init(config)

    elif cmd == "version":
        # Simple command, no config needed
        from baseweb import __version__
        print(f"baseweb {__version__}")

    else:
        # No command provided
        print("Use --help for usage")
        sys.exit(1)
```

### 4. Command Implementation

Each command in its own module:

```python
# src/baseweb/commands/serve.py
from dataclasses import dataclass, field
from clevis import configclass
import sys

@configclass(cmd="serve", help="Run baseweb application")
class ServeConfig:
    """Configuration for serve command."""
    app_uri: str = "app:asgi_app"
    bind: str = "0.0.0.0:8000"
    workers: int = 1
    worker_class: str = "uvicorn.workers.UvicornWorker"
    timeout: int = 120
    keepalive: int = 5

def serve(config: ServeConfig):
    """Run baseweb application with Gunicorn."""
    from baseweb.__main__ import import_app
    from gunicorn.app.wsgiapp import WSGIApplication

    # Import app
    try:
        app = import_app(config.app_uri)
    except (ImportError, AttributeError) as e:
        print(f"Failed to import application: {e}")
        sys.exit(1)

    # Run Gunicorn
    options = {
        "bind": config.bind,
        "workers": config.workers,
        "worker_class": config.worker_class,
        "timeout": config.timeout,
        "keepalive": config.keepalive,
    }

    StandaloneApplication(app, options).run()
```

### 5. Layered Configuration

Commands automatically support configuration layers:

```bash
# 1. Dataclass defaults
baseweb serve  # Uses ServeConfig defaults

# 2. User-level TOML (~/.baseweb.toml)
[serve]
bind = "localhost:8000"

# 3. Project-level TOML (./baseweb.toml)
[serve]
workers = 4

# 4. Environment variables
SERVE_BIND=":3000" baseweb serve

# 5. CLI arguments (highest priority)
baseweb serve --bind :8080 --workers 8
```

### 6. Testing Commands

```python
import tempfile
from pathlib import Path
from clevis import get_cmd, get_config, _reset_factories

def test_serve_command():
    """Test serve command."""
    _reset_factories()

    from baseweb.commands.serve import ServeConfig

    # Simulate CLI args
    cmd = get_cmd(args=["serve"])
    assert cmd == "serve"

    # Get config with CLI override
    config = get_config(ServeConfig, name="baseweb", args=["serve", "--bind", ":8080"])
    assert config.bind == ":8080"
    assert config.workers == 1  # Default
```

### 7. Commands Without Configuration

For simple commands like `version`:

```python
# Option 1: Minimal configclass
@configclass(cmd="version", help="Show version")
class VersionConfig:
    """No fields needed."""
    pass

# Option 2: Handle in dispatch
def main():
    cmd = get_cmd()

    if cmd == "version":
        from baseweb import __version__
        print(f"baseweb {__version__}")
        return

    # ... other commands ...
```

## Benefits

1. **Less code** - No manual argparse setup
2. **Type-safe** - Configuration is strongly typed
3. **Consistent** - All commands follow the same pattern
4. **Auto-generated CLI** - Arguments from dataclass fields
5. **Layered config** - TOML + env + CLI support built-in
6. **Testable** - Easy to test with simulated args
7. **Extensible** - Add commands by adding configclasses

## Migration Steps

1. Create `src/baseweb/commands/` directory
2. Create one module per command (serve.py, check.py, etc.)
3. Add `@configclass(cmd="...")` to each config
4. Move command logic to command modules
5. Simplify `__main__.py` to use `get_cmd()` dispatch
6. Remove all manual argparse code
7. Update tests to use `_reset_factories()` and `get_config()`

## Do's and Don'ts

### Do

- Use `@configclass(cmd="...")` for each command
- Use `get_cmd()` to dispatch commands
- Use `get_config()` to load configuration
- Create separate modules for each command
- Test with `_reset_factories()` to isolate tests

### Don't

- Manually create argparse subparsers
- Use `func` callbacks in argparse
- Duplicate Clevis functionality
- Mix argparse with Clevis commands
- Forget to call `_reset_factories()` in tests

## Real Example

See `/Users/xtof/Workspace/agentic/clevis/examples/commands.py` for a working example:

```python
from clevis import configclass, get_cmd, get_config

@configclass(cmd="check", help="Run diagnostics", aliases=["c", "chk"])
class CheckConfig:
    verbose: bool = False

@configclass(cmd="print", help="Print configuration", aliases=["p"])
class PrintConfig:
    rich: bool = False

if __name__ == "__main__":
    cmd = get_cmd()
    if cmd == "check":
        config = get_config(CheckConfig, project=False, user=False)
        print(f"checking verbose={config.verbose}")
    elif cmd == "print":
        config = get_config(PrintConfig, project=False, user=False)
        print(config)
```

## Key Takeaway

**Stop reimplementing argparse.** Clevis provides complete command support through:
- `@configclass(cmd="...")` decorator
- `get_cmd()` for command dispatch
- `get_config()` for configuration loading
- Automatic CLI argument generation

Use these features instead of manual argparse setup.