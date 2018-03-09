Frontend Code
=============

Web-PDB is distributed with pre-bundled and minified JavaScript and CSS files,
and all the necessary static assets. However, if you want to make some changes
to the frontend code and/or to bundle the resulting code yourself, you need
to install the necessary development dependencies. First, install Node.js and NPM
for your platform. Then go to the ``./frontend/`` directory and run
``npm install`` there.

Available Commands
------------------

- ``npm run build-dev``: build development bundle.
- ``npm run build``: build production (minified) bundle.
- ``npm run watch``: watch the frontend source files for changes (during development).
- ``npm run lint``: run ESLint with the default set of rules for ES6.

Bundled static files are automatically placed in ``./web_pdb/static`` directory.
