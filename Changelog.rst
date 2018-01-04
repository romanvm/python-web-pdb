Changelog
#########

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
