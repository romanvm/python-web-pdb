# coding: utf-8
# Author: Roman Miroshnychenko aka Roman V.M.
# E-mail: romanvm@yandex.ua

from __future__ import absolute_import
from __future__ import print_function

import time
from socket import gethostname
from threading import Thread, Event, Lock
try:
    from queue import Queue
except ImportError:
    from threading import Queue
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
    def __init__(self, host, port):
        self._history = ThreadSafeBuffer('')
        self._in_queue = Queue()
        self._stop_server = Event()
        self._server_process = Thread(target=self._run_server, args=(host, port))
        self._server_process.daemon = True
        self._server_process.start()

    @property
    def seekable(self):
        return False

    def _run_server(self, host, port):
        app.in_queue = self._in_queue
        app.history = self._history
        httpd = make_server(host, port, app, handler_class=SilentWSGIRequestHandler)
        httpd.timeout = 0.1
        print('Web-PDB: starting web-server on {0}:{1}...'.format(gethostname(), port))
        while not self._stop_server.is_set():
            httpd.handle_request()
        httpd.socket.close()

    def readline(self):
        data = self._in_queue.get()
        self.write(data)
        return data

    read = readline

    def readlines(self):
        return [self.readline()]

    def writeline(self, data):
        self._history.contents += data

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
            time.sleep(0.05)

    def close(self):
        print('Web-PDB: stopping web-server...')
        self._stop_server.set()
        self._server_process.join()
        print('Web-PDB: web-server stopped.')
