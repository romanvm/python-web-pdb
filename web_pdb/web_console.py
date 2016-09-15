# coding: utf-8
# Author: Roman Miroshnychenko aka Roman V.M.
# E-mail: romanvm@yandex.ua
"""
File-like web-based input/output console
"""

from __future__ import absolute_import
from __future__ import print_function

import time
from socket import gethostname
from threading import Thread, Event, Lock
try:
    import queue
except ImportError:
    import Queue as queue
from wsgiref.simple_server import make_server, WSGIRequestHandler
from .wsgi_app import app

__all__ = ['WebConsole']


class SilentWSGIRequestHandler(WSGIRequestHandler):
    """WSGI request handler with logging disabled"""
    def log_message(self, format, *args):
        pass


class ThreadSafeBuffer(object):
    """
    A buffer for data exchange between threads
    """
    def __init__(self, contents=None):
        self._lock = Lock()
        self._contents = contents
        self._is_dirty = contents is not None

    @property
    def is_dirty(self):
        """Indicates whether a buffer contains unread data"""
        with self._lock:
            return self._is_dirty

    @property
    def contents(self):
        """Get or set buffer contents"""
        with self._lock:
            self._is_dirty = False
            return self._contents

    @contents.setter
    def contents(self, value):
        with self._lock:
            self._contents = value
            self._is_dirty = True


class WebConsole(object):
    """
    A file-like class for exchanging data between PDB and the web-UI
    """
    def __init__(self, host, port, debugger):
        self._debugger = debugger
        self._history = ThreadSafeBuffer('')
        self._variables = ThreadSafeBuffer('')
        self._frame_data = ThreadSafeBuffer()
        self._in_queue = queue.Queue()
        self._stop_all = Event()
        self._server_process = Thread(target=self._run_server, args=(host, port))
        self._server_process.daemon = True
        print('Web-PDB: starting web-server on {0}:{1}...'.format(gethostname(), port))
        self._server_process.start()

    @property
    def seekable(self):
        return False

    @property
    def writable(self):
        return True

    def _run_server(self, host, port):
        app.in_queue = self._in_queue
        app.history = self._history
        app.variables = self._variables
        app.frame_data = self._frame_data
        httpd = make_server(host, port, app, handler_class=SilentWSGIRequestHandler)
        httpd.timeout = 0.1
        while not self._stop_all.is_set():
            httpd.handle_request()
        httpd.socket.close()

    def readline(self):
        while not self._stop_all.is_set():
            try:
                data = self._in_queue.get(timeout=0.1)
                break
            except queue.Empty:
                continue
        else:
            data = ''
        self.write(data)
        return data

    read = readline

    def readlines(self):
        return [self.readline()]

    def writeline(self, data):
        self._history.contents += data
        try:
            self._variables.contents = self._debugger.get_variables()
            self._frame_data.contents = self._debugger.get_current_frame_data()
        except (IOError, AttributeError):
            self._variables.contents = 'No data available'
            self._frame_data.contents = {
                'filename': '',
                'listing': 'No data available',
                'curr_line': -1,
                'breaklist': [],
            }

    write = writeline

    def writelines(self, lines):
        for line in lines:
            self.writeline(line)

    def flush(self):
        """
        Wait until history is read but no more than 5 cycles
        in case a browser session is closed.
        """
        i = 0
        while self._history.is_dirty and i <= 5:
            i += 1
            time.sleep(0.1)

    def close(self):
        print('Web-PDB: stopping web-server...')
        self._stop_all.set()
        self._server_process.join()
        print('Web-PDB: web-server stopped.')

    @property
    def closed(self):
        return self._stop_all.is_set()
