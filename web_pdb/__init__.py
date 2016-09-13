# coding: utf-8
# Author: Roman Miroshnychenko aka Roman V.M.
# E-mail: romanvm@yandex.ua

from __future__ import absolute_import
from __future__ import unicode_literals

import sys
import traceback
from contextlib import contextmanager as _contextmanager
from pdb import Pdb, getsourcelines
from .web_console import WebConsole

__all__ = ['WebPdb', 'set_trace', 'post_mortem', 'catch_post_mortem']


class WebPdb(Pdb):
    active_instance = None

    def __init__(self, host='', port=5555, patch_stdstreams=False):
        self.console = WebConsole(host, port, self)
        super(WebPdb, self).__init__(stdin=self.console, stdout=self.console)
        # Borrowed from here: https://github.com/ionelmc/python-remote-pdb
        self.backup = []
        if patch_stdstreams:
            for name in (
                    'stderr',
                    'stdout',
                    '__stderr__',
                    '__stdout__',
                    'stdin',
                    '__stdin__',
            ):
                self.backup.append((name, getattr(sys, name)))
                setattr(sys, name, self.console)
        WebPdb.active_instance = self

    def do_quit(self, arg):
        """
        quit || exit || q
        Stop and quit the current debugging session
        """
        for name, fh in self.backup:
            setattr(sys, name, fh)
        self.console.close()
        WebPdb.active_instance = None
        return super(WebPdb, self).do_quit(arg)

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
        try:
            filename = self.curframe.f_code.co_filename
            lines, start_line = getsourcelines(self.curframe)
            curr_line = self.curframe.f_lineno
        except OSError:
            filename = ''
            lines = []
            start_line = curr_line = -1
        return {
            'filename': filename,
            'listing': ''.join(lines),
            'start_line': start_line,
            'curr_line': curr_line,
            'total_lines': len(lines),
        }

    def get_variables(self):
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
    pdb = WebPdb.active_instance
    if pdb is None:
        pdb = WebPdb(host, port, patch_stdstreams)
    pdb.set_trace(sys._getframe().f_back)


def post_mortem(tb=None, host='', port=5555, patch_stdstreams=False):
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


@_contextmanager
def catch_post_mortem(host='', port=5555):
    try:
        yield
    except:
        post_mortem(host=host, port=port)
