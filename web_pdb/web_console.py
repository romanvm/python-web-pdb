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

import logging
import queue
import time
import weakref
from threading import Thread

from .buffer import ThreadSafeBuffer
from .server_adapter import ServerAdapter
from .system_adapter import SystemAdapter

__all__ = ['WebConsole']


class WebConsole:
    """
    A file-like class for exchanging data between PDB and the web-UI
    """

    def __init__(self, host, port, debugger):
        self._system_adapter = SystemAdapter()
        self._server_adapter = ServerAdapter(host, port, self._system_adapter)
        self._debugger = weakref.proxy(debugger)
        self._console_history = ThreadSafeBuffer('')
        self._frame_data = self._server_adapter.frame_data
        self._server_thread = Thread(target=self._server_adapter.serve_forever)
        self._server_thread.daemon = True
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
        return self._system_adapter.is_aborted()

    def readline(self):
        while not self._system_adapter.is_abort_requested():
            try:
                data = self._server_adapter.web_socket_input_queue.get(timeout=0.1)
                break
            except queue.Empty:
                continue
        else:
            data = '\n'  # Empty string causes BdbQuit exception.
        self.writeline(data)
        return data

    read = readline

    def writeline(self, data):
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
                'locals': 'No data available',
            }
        frame_data['console_history'] = self._console_history.contents
        self._frame_data.contents = frame_data
        self._server_adapter.web_socket_broadcast('ping')  # Ping all clients about data update

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
        logging.debug('Web-PDB: stopping web-server...')
        self._server_adapter.close()
        self._server_thread.join()
        logging.debug('Web-PDB: web-server stopped.')
