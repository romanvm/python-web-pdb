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
File-like web-based input/output console
"""

from __future__ import absolute_import, unicode_literals
import logging
import time
import weakref
from socket import gethostname
from threading import Thread, Event, RLock
try:
    import queue
except ImportError:
    import Queue as queue
from asyncore_wsgi import make_server, AsyncWebSocketHandler
from .wsgi_app import app

__all__ = ['WebConsole']


class ThreadSafeBuffer(object):
    """
    A buffer for data exchange between threads
    """
    def __init__(self, contents=None):
        self._lock = RLock()
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


class WebConsoleSocket(AsyncWebSocketHandler):
    """
    WebConsoleSocket receives PDB commands from the front-end and
    sends pings to client(s) about console updates
    """
    clients = []
    input_queue = queue.Queue()

    @classmethod
    def broadcast(cls, msg):
        for cl in cls.clients:
            if cl.handshaked:
                cl.sendMessage(msg)  # sendMessage uses deque so it is thread-safe

    def handleConnected(self):
        self.clients.append(self)

    def handleMessage(self):
        self.input_queue.put(self.data)

    def handleClose(self):
        self.clients.remove(self)


class WebConsole(object):
    """
    A file-like class for exchanging data between PDB and the web-UI
    """
    def __init__(self, host, port, debugger):
        self._debugger = weakref.proxy(debugger)
        self._console_history = ThreadSafeBuffer('')
        self._frame_data = ThreadSafeBuffer()
        self._stop_all = Event()
        self._server_thread = Thread(target=self._run_server, args=(host, port))
        self._server_thread.daemon = True
        logging.critical(
            'Web-PDB: starting web-server on {0}:{1}...'.format(
                gethostname(), port)
        )
        self._server_thread.start()

    @property
    def seekable(self):
        return False

    @property
    def writable(self):
        return True

    @property
    def encoding(self):
        return 'utf-8'

    @property
    def closed(self):
        return self._stop_all.is_set()

    def _run_server(self, host, port):
        app.frame_data = self._frame_data
        httpd = make_server(host, port, app, ws_handler_class=WebConsoleSocket)
        while not self._stop_all.is_set():
            try:
                httpd.handle_request()
            except (KeyboardInterrupt, SystemExit):
                break
        httpd.handle_close()

    def readline(self):
        while not self._stop_all.is_set():
            try:
                data = WebConsoleSocket.input_queue.get(timeout=0.1)
                break
            except queue.Empty:
                continue
        else:
            data = '\n'  # Empty string causes BdbQuit exception.
        self.writeline(data)
        return data

    read = readline

    def writeline(self, data):
        if isinstance(data, bytes):  # Works for Python 2.7 too
            data = data.decode('utf-8')
        self._console_history.contents += data
        try:
            frame_data = self._debugger.get_current_frame_data()
        except (IOError, AttributeError):
            frame_data = {
                'dirname': '',
                'filename': '',
                'file_listing': 'No data available',
                'current_line': -1,
                'breakpoints': [],
                'globals': 'No data available',
                'locals': 'No data available'
            }
        frame_data['console_history'] = self._console_history.contents
        self._frame_data.contents = frame_data
        WebConsoleSocket.broadcast('ping')  # Ping all clients about data update

    write = writeline

    def flush(self):
        """
        Wait until history is read but no more than 10 cycles
        in case a browser session is closed.
        """
        i = 0
        while self._frame_data.is_dirty and i < 10:
            i += 1
            time.sleep(0.1)

    def close(self):
        logging.critical('Web-PDB: stopping web-server...')
        self._stop_all.set()
        self._server_thread.join()
        logging.critical('Web-PDB: web-server stopped.')
