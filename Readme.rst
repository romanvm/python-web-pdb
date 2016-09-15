Web-PDB
#######

.. image:: https://travis-ci.org/romanvm/python-web-pdb.svg?branch=master
    :target: https://travis-ci.org/romanvm/python-web-pdb

Web-PDB is a remote web-interface for Python's built-in `PDB`_ debugger.
It allows to debug Python scripts remotely in a web-browser.

Features
========

- Responsive design based on `Bootstrap`_.
- Python syntax highlighting with `Prism`_ ("Okaida" theme).
- Supports all PDB features.
- Standard input and output can be redirected to the web-console
  to interact with Python scripts remotely.
- **Current file** box tracks current position in a file being executed.
  Red line numbers indicate breakpoints, if any.
- **Variables** box shows all variables in the current scope. Special variables that start and end with
  double underscores ``__`` are excluded (you can always view them using PDB commands).
- Command history that stores up to 10 last unique PDB commands (accessed by arrow UP/DOWN keys).

.. figure:: https://raw.githubusercontent.com/romanvm/python-web-pdb/master/screenshot.jpg
  :alt: Web-PDB screenshot

  *Web-PDB console in Chrome browser*

Read docstrings in ``./web_pdb/__init__.py`` file for more info.

Compatibility
=============

- **Python**: 2.7, 3+
- **Browsers**: Firefox, Chrome (all modern browsers should work)

License
=======

MIT, see ``LICENSE.txt``

.. _PDB: https://docs.python.org/3.5/library/pdb.html
.. _Bootstrap: http://getbootstrap.com
.. _Prism: http://prismjs.com/
