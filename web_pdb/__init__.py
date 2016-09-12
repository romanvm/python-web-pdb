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

    def __init__(self, host='', port=5555):
        self.console = WebConsole(host, port, self)
        super(WebPdb, self).__init__(stdin=self.console, stdout=self.console)
        WebPdb.active_instance = self

    def do_quit(self, arg):
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


def set_trace(host='', port=5555):
    pdb = WebPdb.active_instance
    if pdb is None:
        pdb = WebPdb(host, port)
    pdb.set_trace(sys._getframe().f_back)


def post_mortem(t=None, host='', port=5555):
    # handling the default
    if t is None:
        # sys.exc_info() returns (type, value, traceback) if an exception is
        # being handled, otherwise it returns None
        t = sys.exc_info()[2]
    if t is None:
        raise ValueError('A valid traceback must be passed if no '
                         'exception is being handled')
    p = WebPdb.active_instance
    if p is None:
        p = WebPdb(host, port)
    p.console.write('Web-PDB post-mortem:\n')
    p.console.write(''.join(traceback.format_tb(t)))
    p.reset()
    p.interaction(None, t)


@_contextmanager
def catch_post_mortem(host='', port=5555):
    try:
        yield
    except:
        post_mortem(host=host, port=port)
