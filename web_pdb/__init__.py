# coding: utf-8
# Author: Roman Miroshnychenko aka Roman V.M.
# E-mail: romanvm@yandex.ua
"""
A web-interface for Python's built-in PDB debugger
"""

from __future__ import absolute_import
from __future__ import unicode_literals

import inspect
import sys
import traceback
from contextlib import contextmanager
from pdb import Pdb
from .web_console import WebConsole

__all__ = ['WebPdb', 'set_trace', 'post_mortem', 'catch_post_mortem']

__version__ = '1.0.0'


# This function is added for compatibility with Python 2
def getsourcelines(obj):
    lines, lineno = inspect.findsource(obj)
    if inspect.isframe(obj) and obj.f_globals is obj.f_locals:
        # must be a module frame: do not try to cut a block out of it
        return lines, 1
    elif inspect.ismodule(obj):
        return lines, 1
    return inspect.getblock(lines[lineno:]), lineno + 1


class WebPdb(Pdb):
    """
    The main debugger class

    It provides a web-interface for Python's built-in PDB debugger
    """
    active_instance = None

    def __init__(self, host='', port=5555, patch_stdstreams=False):
        """
        :param host: web-UI hostname or IP-address
        :type host: str
        :param port: web-UI port
        :type port: int
        :param patch_stdstreams: redirect all standard input and output
            streams to the web-UI.
        :type patch_stdstreams: bool
        """
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
        self.console.close()
        WebPdb.active_instance = None
        return Pdb.do_quit(self, arg)

    do_q = do_exit = do_quit

    def do_longlist(self, arg):
        """longlist | ll
        List the whole source code for the current function or frame.
        """
        # This command is added here for Python 2
        filename = self.curframe.f_code.co_filename
        breaklist = self.get_file_breaks(filename)
        try:
            lines, lineno = getsourcelines(self.curframe)
        except OSError as err:
            self.error(err)
            return
        self._print_lines(lines, lineno, breaklist, self.curframe)

    do_ll = do_longlist

    def get_current_frame_data(self):
        """
        Get all date about the current execution frame

        :return: current frame data
        :rtype: dict
        :raises AttributeError: if the debugger does hold any execution frame.
        :raises OSError: if source code for the current execution frame is not accessible.
        """
        filename = self.curframe.f_code.co_filename
        breaklist = self.get_file_breaks(filename)
        lines, start_line = getsourcelines(self.curframe)
        curr_line = self.curframe.f_lineno
        return {
            'filename': filename,
            'listing': ''.join(lines),
            'start_line': start_line,
            'curr_line': curr_line,
            'total_lines': len(lines),
            'breaklist': breaklist,
        }

    def get_variables(self):
        """
        Get all variables in the current scope

        .. note:: special variables starting with ``__`` are not included.

        :return: a listing of ``var = value`` pairs sorted alphabetically
        :rtype: str
        """
        raw_vars = {}
        raw_vars.update(self.curframe.f_globals)
        raw_vars.update(self.curframe.f_locals)
        f_vars = []
        for var, value in raw_vars.items():
            if var.startswith('__'):
                continue
            f_vars.append('{0} = {1}'.format(var, repr(value)))
        return '\n'.join(sorted(f_vars))


def set_trace(host='', port=5555, patch_stdstreams=False):
    """
    Start the debugger

    This method suspend execution of the current script and starts PDB debugger.
    A web-interface is opened on ``host:port``.

    Example::

        import web_pdb; web_pdb.set_trace()

    thi

    :param host: web-UI hostname or IP-address
    :type host: str
    :param port: web-UI port
    :type port: int
    :param patch_stdstreams: redirect all standard input and output
        streams to the web-UI.
    :type patch_stdstreams: bool
    """
    pdb = WebPdb.active_instance
    if pdb is None:
        pdb = WebPdb(host, port, patch_stdstreams)
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
    :param port: web-UI port
    :type port: int
    :param patch_stdstreams: redirect all standard input and output
        streams to the web-UI.
    :type patch_stdstreams: bool
    """
    if WebPdb.active_instance is not None:
        raise RuntimeError('No active WebPdb instances allowed when doing post-mortem!')
    # handling the default
    if tb is None:
        # sys.exc_info() returns (type, value, traceback) if an exception is
        # being handled, otherwise it returns None
        t, v, tb = sys.exc_info()
        exc_data = traceback.format_exception(t, v, tb)
    else:
        exc_data = traceback.format_tb(tb)
    if tb is None:
        raise ValueError('A valid traceback must be passed if no '
                         'exception is being handled')
    p = WebPdb(host, port, patch_stdstreams)
    p.console.write('Web-PDB post-mortem:\n')
    p.console.write(''.join(exc_data))
    p.reset()
    p.interaction(None, tb)


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
    :param port: web-UI port
    :type port: int
    :param patch_stdstreams: redirect all standard input and output
        streams to the web-UI.
    :type patch_stdstreams: bool
    """
    try:
        yield
    except:
        post_mortem(None, host, port, patch_stdstreams)
