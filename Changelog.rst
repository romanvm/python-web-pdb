Changelog
#########

v.1.3.0 (2016-12-12)
====================

* Implemented a multi-threaded WSGI server to increase responsiveness of the web-UI.

v.1.2.2 (2016-11-03)
====================

* Added deflate compression for data sent to a browser.
* Attempt to fix **Current file** box auto-scrolling.

v.1.2.1 (2016-10-08)
====================

* Logger fix.

v.1.2.0 (2016-10-03)
====================

* Minor UI redesign.
* Added a quick action toolbar and hotkeys for common commands.
* Added a quick help dialog.
* Breakpoints can be added/deleted with a click on a line number.
* The **Currrent file** box is not auto-scrolled if the current line hasn't changed.
* Multiple ``set_trace()`` and ``post_mortem()`` calls are processed correctly.
* Added random web-UI port selection with ``port=-1``.

v.1.1.0 (2016-09-24)
====================

* Initial PyPI release
