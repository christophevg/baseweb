---
name: baseweb-create
description: Create new baseweb applications with guided setup
triggers:
  - when asked to create a new baseweb project
  - when setting up a new web application
  - when starting a new baseweb-based project
---

# Baseweb Create Skill

Guide users through creating new baseweb applications with appropriate structure and configuration.

## Overview

This skill helps create new baseweb projects by:

1. Asking clarifying questions about project needs
2. Generating appropriate project structure
3. Creating initial configuration files
4. Setting up development environment

## When to Use

- Creating a new baseweb project
- Starting a new web application with baseweb
- Setting up a project template

## Project Flavors

Baseweb supports different project types:

| Flavor | Description | Use Case |
|--------|-------------|----------|
| **minimal** | Basic setup with one page | Simple apps, learning |
| **standard** | REST API + pages | Typical web applications |
| **full** | REST API + WebSocket + Auth | Complex interactive apps |
| **pwa** | Progressive Web App | Installable web apps |
| **api-only** | REST API without UI | Backend services |

## Setup Questions

When creating a project, ask these questions:

### 1. Project Basics

```
What is your project name? (e.g., "myapp")
Short description? (e.g., "Task management application")
```

### 2. Project Type

```
What type of project?
- minimal: Basic setup, one page
- standard: REST API + multiple pages
- full: REST API + WebSocket + authentication
- pwa: Progressive Web App (installable)
- api-only: Backend API service
```

### 3. Features

```
Which features do you need?
[ ] Authentication (OAuth)
[ ] WebSocket/Socket.IO
[ ] Database integration (MongoDB)
[ ] File uploads
[ ] Background tasks
```

### 4. Frontend

```
Frontend preferences?
- Default Vuetify layout
- Custom branding (color, theme)
- Additional Vue components needed?
```

## Project Structure

### Minimal Project

```
myapp/
├── app/
│   ├── __init__.py          # Server setup
│   └── pages/
│       └── index/
│           ├── __init__.py
│           └── index.js
├── tests/
│   └── test_init.py
├── pyproject.toml
├── Makefile
├── .env
└── .python-version
```

### Standard Project

```
myapp/
├── app/
│   ├── __init__.py          # Server setup + components
│   ├── pages/
│   │   ├── index/
│   │   ├── admin/
│   │   └── settings/
│   ├── components/          # Shared Vue components
│   └── static/               # Custom CSS, images
├── tests/
│   ├── test_init.py
│   └── test_api.py
├── pyproject.toml
├── Makefile
├── .env
└── .python-version
```

### Full Project

```
myapp/
├── app/
│   ├── __init__.py          # Server + auth + socketio
│   ├── pages/
│   │   ├── index/
│   │   ├── dashboard/
│   │   ├── admin/
│   │   └── settings/
│   ├── components/
│   ├── static/
│   └── api/                  # API resources module
│       ├── __init__.py
│       └── resources.py
├── tests/
│   ├── test_init.py
│   ├── test_api.py
│   └── test_socketio.py
├── pyproject.toml
├── Makefile
├── .env
└── .python-version
```

## File Templates

### pyproject.toml

```toml
[project]
name = "myapp"
version = "0.1.0"
description = "My baseweb application"
requires-python = ">=3.11"
dependencies = [
  "baseweb>=1.0.0",
  "gunicorn>=21.0.0",
  "uvicorn[standard]>=0.24.0",
]

[project.optional-dependencies]
dev = [
  "pytest>=7.0.0",
  "pytest-asyncio>=0.21.0",
  "ruff>=0.1.0",
]

[tool.pytest.ini_options]
asyncio_mode = "auto"

[tool.uv.sources]
baseweb = { path = "../baseweb", editable = true }
```

### app/__init__.py (Minimal)

```python
import logging
import os
from pathlib import Path

from dotenv import find_dotenv, load_dotenv
from baseweb import Baseweb

# Load environment
load_dotenv(find_dotenv())

# Setup logging
LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO")
logging.basicConfig(level=LOG_LEVEL)

# Create server
server = Baseweb("myapp")
server.log_config()

# Register pages
HERE = Path(__file__).resolve().parent
server.register_component("index.js", HERE / "pages" / "index")

server.log_routes()
logger = logging.getLogger(__name__)
logger.info("✅ myapp is ready")

# ASGI entry point
asgi_app = server._asgi_app
```

### app/__init__.py (Full with Auth + WebSocket)

```python
import logging
import os
from pathlib import Path

from dotenv import find_dotenv, load_dotenv
from baseweb import Baseweb

load_dotenv(find_dotenv())

LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO")
logging.basicConfig(level=LOG_LEVEL)

server = Baseweb("myapp")
server.log_config()

# Authentication
def authenticator(scope, request, *args, **kwargs):
    # Implement your auth logic
    return True

server.authenticator = authenticator

# Socket.IO handlers
@server.socketio.on("connect")
async def on_connect(sid, environ):
    logger.info(f"Client connected: {sid}")

@server.socketio.on("disconnect")
async def on_disconnect(sid):
    logger.info(f"Client disconnected: {sid}")

# Register pages
HERE = Path(__file__).resolve().parent
server.register_component("index.js", HERE / "pages" / "index", route="/")
server.register_component("dashboard.js", HERE / "pages" / "dashboard", route="/dashboard")

# Register API resources
from app.api.resources import register_resources
register_resources(server)

server.log_routes()
logger = logging.getLogger(__name__)
logger.info("✅ myapp is ready")

asgi_app = server._asgi_app
```

### Makefile

```makefile
.PHONY: test run run-dev install

test:
	uv run pytest tests/ -v

run:
	uv run gunicorn "app:asgi_app" -w 1 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000

run-dev:
	uv run uvicorn "app:asgi_app" --reload --host 0.0.0.0 --port 8000

install:
	uv sync --all-extras
```

### .env

```bash
# Application
LOG_LEVEL=INFO
APP_NAME=myapp
APP_TITLE=My Application
APP_STYLE=web

# Optional: OAuth
# OAUTH_PROVIDER=google
# OAUTH_CLIENT_ID=your-client-id

# Optional: PWA
# APP_STYLE=pwa
```

### .python-version

```
3.12
```

### tests/test_init.py

```python
"""Tests for app initialization."""

import pytest


class TestMainEntryPoint:
    def test_server_can_be_imported(self):
        """Server module can be imported."""
        from app import server
        assert server is not None

    def test_server_is_baseweb_instance(self):
        """Server is a Baseweb instance."""
        from app import server
        from baseweb import Baseweb
        assert isinstance(server, Baseweb)

    def test_asgi_app_exists(self):
        """ASGI entry point exists."""
        from app import asgi_app
        assert asgi_app is not None
```

### pages/index/index.js

```javascript
var Index = {
  template: `
<div>
  <h1>Welcome</h1>
  <p>Your baseweb application is ready!</p>
</div>
  `,
  navigation: {
    section: null,
    icon: "home",
    text: "Home",
    path: "/",
    index: 1
  }
};

Navigation.add(Index);
```

## Quick Start Commands

After creating the project structure:

```bash
# Create and enter project
mkdir myapp && cd myapp

# Initialize uv project
uv init

# Add dependencies
uv add baseweb gunicorn uvicorn

# Add dev dependencies
uv add --dev pytest pytest-asyncio ruff

# Run the app
make run
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `LOG_LEVEL` | Logging level | `INFO` |
| `APP_NAME` | Application name | Folder name |
| `APP_TITLE` | Browser title | Folder name |
| `APP_STYLE` | Style mode (`web`/`pwa`) | `web` |
| `APP_COLOR` | Primary color | `rgb(21, 101, 192)` |
| `APP_SOCKETIO` | Enable Socket.IO | `yes` |
| `OAUTH_PROVIDER` | OAuth provider | - |
| `OAUTH_CLIENT_ID` | OAuth client ID | - |

## Next Steps After Creation

1. **Run the app**: `make run`
2. **Visit**: http://localhost:8000
3. **Add pages**: Create in `app/pages/`
4. **Add API**: Create Resource classes
5. **Customize**: Edit `.env` for branding

## See Also

- `/baseweb-develop` - Develop features in your app
- `/baseweb-migrate` - Migrate existing Flask apps
- `docs/migration-guide.md` - Migration documentation