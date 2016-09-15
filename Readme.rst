Web-PDB
=======

.. image:: https://travis-ci.org/romanvm/python-web-pdb.svg?branch=master
    :target: https://travis-ci.org/romanvm/python-web-pdb

Web-PDB is a remote web-interface for Python's built-in `PDB`_ debugger.
It allows to debug Python scripts remotely using a web-browser.

Features
--------

- Responsive design based on `Bootstrap`_.
- Python syntax highlighting with `Prismjs`_ ("Okaida" theme).
- Supports all PDB features.
- Standard input and output can be redirected to the web-console
  to interact with your Python script remotely.
- **Current file** box shows current position in a script being executed.
  Red line numbers indicate breakpoints, if any.
- **Variables** box shows all variables in the current scope. Special variables that start and end with
  double underscores ``__`` are excluded (you can always view them using PDB commands).
- The arrow up/down keys allow to scroll through the history of the last 10 unique commands.

.. figure:: https://raw.githubusercontent.com/romanvm/python-web-pdb/master/screenshot.jpg
  :alt: Web-PDB screenshot

  Web-PDB console in Chrome browser

License
-------

MIT, see LICENSE.txt

.. _PDB: https://docs.python.org/3.5/library/pdb.html
.. _Bootstrap: http://getbootstrap.com
.. _Prismjs: http://prismjs.com/
