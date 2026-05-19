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
- **Web server thread**: Runs a pure-stdlib asyncio HTTP+WebSocket server that serves the web UI
  and communicates with the debugger thread via a shared queue.

**Key modules:**

- `web_pdb/__init__.py`: Main `WebPdb` class extending `Pdb`, plus module-level functions
  (`set_trace()`, `post_mortem()`, `catch_post_mortem()`). Handles command dispatch, variable
  formatting, and the custom `inspect`/`i` command.
- `web_pdb/web_console.py`: File-like class that serves as stdin/stdout for the debugger thread.
  Delegates server management and WebSocket broadcasting to `ServerAdapter`. Maintains
  `console_history` buffer and frame data, pinging clients on each write.
- `web_pdb/server_adapter.py`: Thin facade over `AsyncioServer`. `ServerAdapter` owns the
  `input_queue` and `frame_data` buffer, starts the asyncio event loop in a daemon thread via
  `serve_forever()`, and exposes `web_socket_broadcast()` and `web_socket_input_queue` to
  `WebConsole`. Shutdown is coordinated via `SystemAdapter.abort()` and `AsyncioServer.stop()`.
- `web_pdb/asyncio_server.py`: Pure-stdlib asyncio HTTP/WebSocket server. `AsyncioServer` handles
  all HTTP routing (index, `/frame-data`, `/static/`, `/ws`), WebSocket handshake and framing, and
  gzip compression. `_WebSocketConnection` manages per-connection send/receive coroutines and feeds
  incoming PDB commands into the shared `input_queue`. Active connections are tracked in
  `AsyncioServer._connections` (a `set`).
- `web_pdb/system_adapter.py`: Abstraction layer for running in a standard Python environment vs.
  a Kodi addon. Exposes `SystemAdapter` (alias to `_GeneralAdapter` or `_KodiAdapter` depending on
  whether the Kodi runtime is detected). Both implement `is_abort_requested()`,
  `on_server_started()`, `on_server_stopped()`, and `on_exception()`. The Kodi variant uses
  `xbmc.Monitor` for abort detection and shows progress dialogs/notifications.
- `web_pdb/buffer.py`: Thread-safe buffer (`ThreadSafeBuffer`) used for passing data between
  threads with dirty-flag semantics.

### Frontend (JavaScript)

Static assets (JavaScript, CSS, HTML) are bundled via webpack and served from `web_pdb/static/`.

- `frontend/src/`: Source files (JavaScript, CSS).
- `frontend/webpack.config.js`: Webpack configuration.
- Bundled output: `web_pdb/static/` (pre-bundled for distribution).

`node` and `npm` are available via NVM at the path `~/.nvm/versions/node/v24.15.0/bin`

## Commands

### Testing

```bash
# Run all tests using Python's unittest discovery
make test
# or directly:
python tests/tests.py

# Run a single test (tests are numbered and order-dependent)
python -m unittest tests.tests.SeleniumTestCase.test_1_set_trace
```

Tests are Selenium-based integration tests that spawn a debugger subprocess and interact with it
via the web UI. Test methods are numbered (e.g., `test_1_set_trace`, `test_2_next_command`) to
control execution order, since later tests depend on state from earlier ones.

### Linting & Code Quality

```bash
# Lint Python code
make lint

# Fix linting issues automatically
make lint-fix

# Install development dependencies
uv pip install -r requirements.txt
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

### Build & Package

```bash
# Build distribution packages
make build

# Clean build artifacts
make clean
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
time. `WebConsole` spawns a daemon thread that runs `ServerAdapter.serve_forever()`. Thread safety
is achieved via:

- `ThreadSafeBuffer` with RLock for console history and frame data.
- `queue.Queue` (instance-level on `ServerAdapter`) for PDB commands from the web UI.
- `asyncio.Queue` per `_WebSocketConnection` for outbound WebSocket messages (asyncio-internal).
- `threading.Event` in `_BaseAdapter` (`SystemAdapter`) for coordinating server shutdown.

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
- **Core dependencies**: pure Python stdlib (no third-party runtime dependencies)
- **Development dependencies**: `ruff==0.15.12`, `selenium==4.10.0`
- **Package manager**: `uv`

## Important Notes

- This is in minimum maintenance mode; prioritize bug fixes and compatibility over new features.
- The project aims to support all modern Python versions (3.6+).
- The `inspect`/`i` command is a custom extension; it lists object members, excluding `__` names.
- Post-mortem debugging is supported via `post_mortem()` and the `catch_post_mortem()` context
  manager.

## General Rules

- Use best coding practices for Python and JavaScript.
- Do not commit anything to Git or push without an explicit approval!
- Use `uv pip` to install/update Python libraries.
