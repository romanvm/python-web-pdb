# coding: utf-8
# Author: Roman Miroshnychenko aka Roman V.M.
# E-mail: roman1972@gmail.com
#
# Copyright (c) 2016 Roman Miroshnychenko
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
"""
A web-interface for Python's built-in PDB debugger
"""

from __future__ import absolute_import, unicode_literals
import inspect
import os
import sys
import random
import traceback
from contextlib import contextmanager
from pprint import pformat
if sys.version_info[0] == 2:
    from .pdb_py2 import PdbPy2 as Pdb
else:
    from pdb import Pdb
from .web_console import WebConsole

__all__ = ['WebPdb', 'set_trace', 'post_mortem', 'catch_post_mortem']

__version__ = '1.5.7'


class WebPdb(Pdb):
    """
    The main debugger class

    It provides a web-interface for Python's built-in PDB debugger
    with extra convenience features.
    """
    active_instance = None
    null = object()

    def __init__(self, host='', port=5555, patch_stdstreams=False):
        """
        :param host: web-UI hostname or IP-address
        :type host: str
        :param port: web-UI port. If ``port=-1``, choose a random port value
            between 32768 and 65536.
        :type port: int
        :param patch_stdstreams: redirect all standard input and output
            streams to the web-UI.
        :type patch_stdstreams: bool
        """
        if port == -1:
            random.seed()
            port = random.randint(32768, 65536)
        self.console = WebConsole(host, port, self)
        Pdb.__init__(self, stdin=self.console, stdout=self.console)
        # Borrowed from here: https://github.com/ionelmc/python-remote-pdb
        self._backup = []
        if patch_stdstreams:
            for name in (
                    'stderr',
                    'stdout',
                    '__stderr__',
                    '__stdout__',
                    'stdin',
                    '__stdin__',
            ):
                self._backup.append((name, getattr(sys, name)))
                setattr(sys, name, self.console)
        WebPdb.active_instance = self

    def do_quit(self, arg):
        """
        quit || exit || q
        Stop and quit the current debugging session
        """
        for name, fh in self._backup:
            setattr(sys, name, fh)
        self.console.writeline('*** Aborting program ***\n')
        self.console.flush()
        self.console.close()
        WebPdb.active_instance = None
        return Pdb.do_quit(self, arg)

    do_q = do_exit = do_quit

    def do_inspect(self, arg):
        """
        i(nspect) object
        Inspect an object
        """
        if arg in self.curframe_locals:
            obj = self.curframe_locals[arg]
        elif arg in self.curframe.f_globals:
            obj = self.curframe.f_globals[arg]
        else:
            obj = WebPdb.null
        if obj is not WebPdb.null:
            self.console.writeline(
                '{0} = {1}:\n'.format(arg, type(obj))
            )
            for name, value in inspect.getmembers(obj):
                if not (name.startswith('__') and (name.endswith('__'))):
                    self.console.writeline('    {0}: {1}\n'.format(
                        name, self._get_repr(value, pretty=True, indent=8)
                    ))
        else:
            self.console.writeline(
                'NameError: name "{0}" is not defined\n'.format(arg)
            )
        self.console.flush()

    do_i = do_inspect

    @staticmethod
    def _get_repr(obj, pretty=False, indent=1):
        """
        Get string representation of an object

        :param obj: object
        :type obj: object
        :param pretty: use pretty formatting
        :type pretty: bool
        :param indent: indentation for pretty formatting
        :type indent: int
        :return: string representation
        :rtype: str
        """
        if pretty:
            repr_value = pformat(obj, indent)
        else:
            repr_value = repr(obj)
        if sys.version_info[0] == 2:
            # Try to convert Unicode string to human-readable form
            try:
                repr_value = repr_value.decode('raw_unicode_escape')
            except UnicodeError:
                repr_value = repr_value.decode('utf-8', 'replace')
        return repr_value

    def set_continue(self):
        # We do not detach the debugger
        # for correct multiple set_trace() and post_mortem() calls.
        self._set_stopinfo(self.botframe, None, -1)

    def dispatch_return(self, frame, arg):
        # The parent's method needs to be called first.
        ret = Pdb.dispatch_return(self, frame, arg)
        if frame.f_back is None:
            self.console.writeline('*** Thread finished ***\n')
            if not self.console.closed:
                self.console.flush()
                self.console.close()
                WebPdb.active_instance = None
        return ret

    def get_current_frame_data(self):
        """
        Get all date about the current execution frame

        :return: current frame data
        :rtype: dict
        :raises AttributeError: if the debugger does hold any execution frame.
        :raises IOError: if source code for the current execution frame is not accessible.
        """
        filename = self.curframe.f_code.co_filename
        lines, start_line = inspect.findsource(self.curframe)
        if sys.version_info[0] == 2:
            lines = [line.decode('utf-8') for line in lines]
        return {
            'dirname': os.path.dirname(os.path.abspath(filename)) + os.path.sep,
            'filename': os.path.basename(filename),
            'file_listing': ''.join(lines),
            'current_line': self.curframe.f_lineno,
            'breakpoints': self.get_file_breaks(filename),
            'globals': self.get_globals(),
            'locals': self.get_locals()
        }

    def _format_variables(self, raw_vars):
        """
        :param raw_vars: a `dict` of `var_name: var_object` pairs
        :type raw_vars: dict
        :return: sorted list of variables as a unicode string
        :rtype: unicode
        """
        f_vars = []
        for var, value in raw_vars.items():
            if not (var.startswith('__') and var.endswith('__')):
                repr_value = self._get_repr(value)
                f_vars.append('{0} = {1}'.format(var, repr_value))
        return '\n'.join(sorted(f_vars))

    def get_globals(self):
        """
        Get the listing of global variables in the current scope

        .. note:: special variables that start and end with
            double underscores ``__`` are not included.

        :return: a listing of ``var = value`` pairs sorted alphabetically
        :rtype: unicode
        """
        return self._format_variables(self.curframe.f_globals)

    def get_locals(self):
        """
        Get the listing of local variables in the current scope

        .. note:: special variables that start and end with
            double underscores ``__`` are not included.
            For module scope globals and locals listings are the same.

        :return: a listing of ``var = value`` pairs sorted alphabetically
        :rtype: unicode
        """
        return self._format_variables(self.curframe_locals)

    def remove_trace(self, frame=None):
        """
        Detach the debugger from the execution stack

        :param frame: the lowest frame to detach the debugger from.
        :type frame: types.FrameType
        """
        sys.settrace(None)
        if frame is None:
            frame = self.curframe
        while frame and frame is not self.botframe:
            del frame.f_trace
            frame = frame.f_back


def set_trace(host='', port=5555, patch_stdstreams=False):
    """
    Start the debugger

    This method suspends execution of the current script
    and starts a PDB debugging session. The web-interface is opened
    on the specified port (default: ``5555``).

    Example::

        import web_pdb;web_pdb.set_trace()

    Subsequent :func:`set_trace` calls can be used as hardcoded breakpoints.

    :param host: web-UI hostname or IP-address
    :type host: str
    :param port: web-UI port. If ``port=-1``, choose a random port value
     between 32768 and 65536.
    :type port: int
    :param patch_stdstreams: redirect all standard input and output
        streams to the web-UI.
    :type patch_stdstreams: bool
    """
    pdb = WebPdb.active_instance
    if pdb is None:
        pdb = WebPdb(host, port, patch_stdstreams)
    else:
        # If the debugger is still attached reset trace to a new location
        pdb.remove_trace()
    pdb.set_trace(sys._getframe().f_back)


def post_mortem(tb=None, host='', port=5555, patch_stdstreams=False):
    """
    Start post-mortem debugging for the provided traceback object

    If no traceback is provided the debugger tries to obtain a traceback
    for the last unhandled exception.

    Example::

        try:
            # Some error-prone code
            assert ham == spam
        except:
            web_pdb.post_mortem()

    :param tb: traceback for post-mortem debugging
    :type tb: types.TracebackType
    :param host: web-UI hostname or IP-address
    :type host: str
    :param port: web-UI port. If ``port=-1``, choose a random port value
        between 32768 and 65536.
    :type port: int
    :param patch_stdstreams: redirect all standard input and output
        streams to the web-UI.
    :type patch_stdstreams: bool
    :raises ValueError: if no valid traceback is provided and the Python
        interpreter is not handling any exception
    """
    # handling the default
    if tb is None:
        # sys.exc_info() returns (type, value, traceback) if an exception is
        # being handled, otherwise it returns (None, None, None)
        t, v, tb = sys.exc_info()
        exc_data = traceback.format_exception(t, v, tb)
    else:
        exc_data = traceback.format_tb(tb)
    if tb is None:
        raise ValueError('A valid traceback must be passed if no '
                         'exception is being handled')
    pdb = WebPdb.active_instance
    if pdb is None:
        pdb = WebPdb(host, port, patch_stdstreams)
    else:
        pdb.remove_trace()
    pdb.console.writeline('*** Web-PDB post-mortem ***\n')
    pdb.console.writeline(''.join(exc_data))
    pdb.reset()
    pdb.interaction(None, tb)


@contextmanager
def catch_post_mortem(host='', port=5555, patch_stdstreams=False):
    """
    A context manager for tracking potentially error-prone code

    If an unhandled exception is raised inside context manager's code block,
    the post-mortem debugger is started automatically.

    Example::

        with web_pdb.catch_post_mortem()
            # Some error-prone code
            assert ham == spam

    :param host: web-UI hostname or IP-address
    :type host: str
    :param port: web-UI port. If ``port=-1``, choose a random port value
        between 32768 and 65536.
    :type port: int
    :param patch_stdstreams: redirect all standard input and output
        streams to the web-UI.
    :type patch_stdstreams: bool
    """
    try:
        yield
    except Exception:
        post_mortem(None, host, port, patch_stdstreams)
