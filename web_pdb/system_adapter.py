# Author: Roman Miroshnychenko aka Roman V.M.
# E-mail: roman1972@gmail.com
#
# Copyright (c) 2026 Roman Miroshnychenko
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
Abstraction layer for using Web-PDB either in a regular PC/Server or in a Kodi addon.
"""

import logging
import traceback
from abc import ABC, abstractmethod
from threading import Event

try:
    import xbmc
    import xbmcaddon
    from xbmcgui import NOTIFICATION_ERROR, Dialog, DialogProgressBG

    is_kodi = True if not getattr(xbmc, '__kodistubs__', False) else False
except ImportError:
    is_kodi = False

__all__ = ['SystemAdapter']


class _BaseAdapter(ABC):
    def __init__(self):
        self._abort_event = Event()

    @abstractmethod
    def is_abort_requested(self):
        raise NotImplementedError

    def abort(self):
        self._abort_event.set()

    def is_aborted(self):
        return self._abort_event.is_set()

    @abstractmethod
    def on_server_started(self, server_name, port):
        raise NotImplementedError

    def on_server_stopped(self):
        pass

    def on_exception(self):
        pass


class _GeneralAdapter(_BaseAdapter):
    def is_abort_requested(self):
        return self._abort_event.is_set()

    def on_server_started(self, server_name, port):
        logging.critical('Web-PDB: starting web-server on http://%s:%s', server_name, port)


SystemAdapter = _GeneralAdapter

if is_kodi:

    class _KodiLogHandler(logging.Handler):
        """
        Logging handler that writes to the Kodi log with correct levels
        """

        LOG_FORMAT = '[kodi.web-pdb] {message}'
        LEVEL_MAP = {
            logging.NOTSET: xbmc.LOGNONE,
            logging.DEBUG: xbmc.LOGDEBUG,
            logging.INFO: xbmc.LOGINFO,
            logging.WARN: xbmc.LOGWARNING,
            logging.WARNING: xbmc.LOGWARNING,
            logging.ERROR: xbmc.LOGERROR,
            logging.CRITICAL: xbmc.LOGFATAL,
        }

        def emit(self, record):
            message = self.format(record)
            kodi_log_level = self.LEVEL_MAP.get(record.levelno, xbmc.LOGDEBUG)
            xbmc.log(message, level=kodi_log_level)

        @classmethod
        def initialize_logging(cls):
            """
            Initialize the root logger that writes to the Kodi log

            After initialization, you can use Python logging facilities as usual.
            """
            logging.basicConfig(
                format=cls.LOG_FORMAT, style='{', level=logging.DEBUG, handlers=[cls()], force=True
            )

    class _KodiAdapter(_BaseAdapter):
        def __init__(self):
            super().__init__()
            self._monitor = xbmc.Monitor()
            self._addon = xbmcaddon.Addon('script.module.web-pdb')
            self._dialog_progress = None
            _KodiLogHandler.initialize_logging()

        def is_abort_requested(self):
            return self._abort_event.is_set() or self._monitor.abortRequested()

        def on_server_started(self, server_name, port):
            xbmc.log('Web-PDB: web-server started.', level=xbmc.LOGINFO)
            self._dialog_progress = DialogProgressBG()
            self._dialog_progress.create(
                self._addon.getLocalizedString(32001),
                self._addon.getLocalizedString(32002).format(server_name, port),
            )
            self._dialog_progress.update(100)

        def on_server_stopped(self):
            self._dialog_progress.close()
            self._dialog_progress = None

        def on_exception(self):
            stack_trace = traceback.format_exc()
            xbmc.log(f'Web-PDB: unhandled exception detected:\n{stack_trace}', xbmc.LOGERROR)
            xbmc.log('Web-PDB: starting post-mortem debugging...', xbmc.LOGERROR)
            Dialog().notification(
                'Web-PDB', self._addon.getLocalizedString(32003), icon=NOTIFICATION_ERROR
            )

    SystemAdapter = _KodiAdapter
