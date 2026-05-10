# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Web-PDB is a web-based interface for Python's built-in PDB debugger. It allows developers to debug
Python scripts remotely in a web browser. The project is currently in minimum maintenance mode,
prioritizing bug fixes and Python version compatibility over new features.

## Architecture

### Backend (Python)

The debugger backend is a two-threaded system:

- **Debugger thread**: Runs the WebPdb class (extends Python's `Pdb`), which executes user code and
  handles debug commands.
- **Web server thread**: Runs a Bottle-based WSGI application that serves the web UI and communicates
  with the debugger thread via WebSockets.

**Key modules:**

- `web_pdb/__init__.py`: Main `WebPdb` class extending `Pdb`, plus module-level functions
  (`set_trace()`, `post_mortem()`, `catch_post_mortem()`). Handles command dispatch, variable
  formatting, and the custom `inspect`/`i` command.
- `web_pdb/web_console.py`: File-like class that serves as stdin/stdout for the debugger thread.
  Manages the WebSocket server, handles bidirectional communication between debugger and web UI.
- `web_pdb/wsgi_app.py`: Bottle application serving the web UI and API endpoints for debugger
  control and frame data retrieval.
- `web_pdb/buffer.py`: Thread-safe buffer (`ThreadSafeBuffer`) used for passing data between
  threads with dirty-flag semantics.

### Frontend (JavaScript)

Static assets (JavaScript, CSS, HTML) are bundled via webpack and served from `web_pdb/static/`.

- `frontend/src/`: Source files (JavaScript, CSS).
- `frontend/webpack.config.js`: Webpack configuration.
- Bundled output: `web_pdb/static/` (pre-bundled for distribution).

## Commands

### Testing

```bash
# Run all tests using Python's unittest discovery
python tests/tests.py

# Run tests across multiple Python versions
tox

# Run a single test (tests are numbered and order-dependent)
python -m unittest tests.tests.SeleniumTestCase.test_1_set_trace
```

Tests are Selenium-based integration tests that spawn a debugger subprocess and interact with it
via the web UI. Test methods are numbered (e.g., `test_1_set_trace`, `test_2_next_command`) to
control execution order, since later tests depend on state from earlier ones.

### Linting & Code Quality

```bash
# Lint Python code
pylint web_pdb/

# Install development dependencies
pip install -r requirements.txt
```

### Frontend Build

```bash
cd frontend
npm install          # Install dependencies
npm run build-dev    # Development bundle
npm run build        # Production (minified) bundle
npm run watch        # Watch for changes and rebuild
npm run lint         # Run ESLint
```

### Installation

```bash
# Development installation
pip install -e .

# Normal installation
pip install .
```

## Threading Model

The debugger maintains one active instance (`WebPdb.active_instance`) that traces one thread at a
time. The WebConsole spawns a daemon thread to run the web server. Thread safety is achieved via:

- `ThreadSafeBuffer` with RLock for console history and frame data.
- `queue.Queue` for PDB commands from the web UI (thread-safe by design).
- WebSocket deque for sending messages to clients (thread-safe for appending).

## Testing Notes

- Tests require Selenium and a headless browser (Chrome on non-Windows, Firefox on Windows).
- Tests are integration tests that actually spawn debugger instances and interact via the browser.
- Test execution order matters; do not run tests in parallel or out of order.
- Tests create temporary Python files (e.g., `tests/db.py`, `tests/db_ps.py`) that are debugged
  during test execution.

## Key Design Decisions

1. **No detach on continue**: Unlike standard remote debuggers, Web-PDB does not detach after
   `continue`; this allows multiple `set_trace()` calls to work as hardcoded breakpoints.
2. **Single browser session**: The UI is designed for one concurrent browser session; multiple
   windows/tabs accessing the same debugger may display inconsistent data.
3. **Customizable ports**: The debugger can listen on any port (default 5555) or choose a random
   port with `port=-1` for multiprocessing scenarios.

## Requirements

- **Python**: 3.6+
- **Core dependencies**: `bottle>=0.12.25`, `asyncore-wsgi>=0.0.11`
- **Test dependencies**: `selenium==4.10.0`, `Pylint==2.15.0`

## Important Notes

- This is in minimum maintenance mode; prioritize bug fixes and compatibility over new features.
- The project aims to support all modern Python versions (3.6+).
- The `inspect`/`i` command is a custom extension; it lists object members, excluding `__` names.
- Post-mortem debugging is supported via `post_mortem()` and the `catch_post_mortem()` context
  manager.

## General Rules

- Do not commit anything to Git or push without an explicit approval.
- Use `uv pip` to manage Python libraries.
