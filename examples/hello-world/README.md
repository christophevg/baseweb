# Hello World Example

A minimal example application demonstrating Vue 3 + Vuetify 3 integration with baseweb.

## Purpose

This example validates that the core baseweb setup works correctly after the Vue 3 + Vuetify 3 migration. It serves as a "canary" to detect configuration or compatibility issues early.

## Prerequisites

- Python 3.10+
- [uv](https://docs.astral.sh/uv/) installed

## Quick Start

```bash
# Navigate to this example
cd examples/hello-world

# Install dependencies (creates virtualenv automatically)
uv sync

# Run the server
uv run uvicorn app:asgi_app --reload
```

Then open http://localhost:8000 in your browser.

## Running the Server

### Option 1: Using uvicorn (development)

```bash
uv run uvicorn app:asgi_app --reload --port 8000
```

### Option 2: Using gunicorn (production-like)

```bash
uv run gunicorn -w 1 -k uvicorn.workers.UvicornWorker "app:asgi_app" --bind 0.0.0.0:8000
```

## Expected Output

### Server Startup

You should see the baseweb banner in the console:

```
 _                   _
| |__   __ _ _ __ __| |
| '_ \ / _` | '__/ _` |
| |_) | (_| | |  | (_| |
|_.__/ \__,_|_|   \__,_|
baseweb 0.4.3
[INFO] Starting uvicorn...
[INFO] Uvicorn running on http://127.0.0.1:8000
```

### Browser

1. Open http://localhost:8000
2. You should see a styled page with:
   - A toolbar showing "hello-world" as the app name
   - A card containing "Hello World" title
   - Welcome message text

### Browser Console

Open the browser developer console (F12). You should see:

```
Queueing component: HelloWorld
Registering components: ['HelloWorld']
✓ Registered: HelloWorld
✅ Vue 3 app mounted successfully
```

## Validation Checklist

- [ ] `uv sync` completes without errors
- [ ] Server starts with `uv run uvicorn app:asgi_app --reload`
- [ ] Page loads at http://localhost:8000
- [ ] Browser console shows "Vue 3 app mounted successfully"
- [ ] Browser console shows "Registered: HelloWorld"
- [ ] No JavaScript errors in browser console
- [ ] Vuetify styling is applied (Material Design appearance)
- [ ] v-toolbar shows "hello-world"
- [ ] Hello World card is centered and styled

## Troubleshooting

### `uv sync` fails

- Ensure uv is installed: `uv --version`
- Check Python version: `python --version` (need 3.10+)
- Ensure baseweb source exists in parent directory

### Server won't start

- Run from the hello-world directory: `cd examples/hello-world`
- Check the virtualenv was created: `ls .venv`

### Page shows blank or errors

- Check browser console for errors
- Verify static files are being served (check Network tab)
- Ensure Vue 3 and Vuetify 3 are loaded

### Component not registered

- Check that `HelloWorld.js` is in `static/js/`
- Verify the path in `app.py` is correct

## Files

```
hello-world/
  pyproject.toml       # Project config with uv support
  app.py               # Main application entry point
  README.md            # This file
  static/
    js/
      HelloWorld.js    # Vue 3 component
```

## Architecture Notes

- **Backend**: Minimal Quart application using baseweb
- **Frontend**: Single Vue 3 component with Vuetify 3
- **Routing**: Single route (/) handled by baseweb
- **No database**: This is a stateless example
- **No authentication**: Simplified for demonstration
- **uv**: Manages virtualenv and dependencies automatically