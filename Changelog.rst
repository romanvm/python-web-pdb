Changelog
#########

v.1.5.1
=======

* Fixed using ``inspect`` command for variables with ``None`` values.

v.1.5.0
=======

* Added ``inspect`` command.

v.1.4.4
=======

* Upgrade Prism.js to v.1.15.0

v.1.4.3
=======

* Use gzip compression instead of deflate for web-console endpoints
  (`more info <https://stackoverflow.com/a/9856879/4819775>`_).

v.1.4.2
=======

* Bump ``asyncore-wsgi`` dependency version. This fixes issues with the web-UI
  on some platforms.
* Code cleanup.

v.1.4.1
=======

* Use full path for setting and removing breakpoints.

v.1.4.0
=======

* Replaced a wsgiref-based multi-threaded WSGI server with a single-threaded
  asynchronous WSGI/WebSocket server.
* Implemented WebSockets instead of periodic back-end polling for retrieving
  updated debugger data.

v.1.3.5
=======

* Fix crash when clearing a breakpoint on Linux.
* Fix autoscrolling on large files.
* Move frontend to modern JavaScript syntax and tooling.
* Optimize Python syntax highlighting performance.

v.1.3.4
=======

* Fix a bug with patched ``cl`` command not working.

v.1.3.3
=======

* Fixed setting ``set_trace()`` at the last line of a Python script.
* Fixed clearing a breakpoint at setups with the current workdir different
  from the current module directory.

v.1.3.2
=======

* Internal changes.

v.1.3.1
=======

* Now if web-console data haven't changed
  the back-end sends "null" response body instead of a 403 error.

v.1.3.0
=======

* Implemented a multi-threaded WSGI server to increase responsiveness of the web-UI.

v.1.2.2
=======

* Added deflate compression for data sent to a browser.
* Attempt to fix **Current file** box auto-scrolling.

v.1.2.1
=======

* Logger fix.

v.1.2.0
=======

* Minor UI redesign.
* Added a quick action toolbar and hotkeys for common commands.
* Added a quick help dialog.
* Breakpoints can be added/deleted with a click on a line number.
* The **Currrent file** box is not auto-scrolled if the current line hasn't changed.
* Multiple ``set_trace()`` and ``post_mortem()`` calls are processed correctly.
* Added random web-UI port selection with ``port=-1``.

v.1.1.0
=======

* Initial PyPI release
