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
Facade that owns the asyncio HTTP/WebSocket server and exposes the interface
that WebConsole depends on.
"""

from __future__ import annotations

import asyncio
import logging
import queue

from .asyncio_server import AsyncioServer
from .buffer import ThreadSafeBuffer

__all__ = ['ServerAdapter']

logger = logging.getLogger(__name__)


class ServerAdapter:
    def __init__(self, host: str, port: int, system_adapter):
        self._system_adapter = system_adapter
        self._input_queue: queue.Queue = queue.Queue()
        self.frame_data: ThreadSafeBuffer = ThreadSafeBuffer()
        self._server = AsyncioServer(host, port, self.frame_data, self._input_queue)
        self._loop: asyncio.AbstractEventLoop | None = None

    @property
    def web_socket_input_queue(self) -> queue.Queue:
        return self._input_queue

    def web_socket_broadcast(self, message: str) -> None:
        self._server.broadcast(message)

    def serve_forever(self) -> None:
        self._loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self._loop)
        try:
            self._loop.run_until_complete(
                self._server.run(
                    self._system_adapter.is_abort_requested,
                    self._system_adapter.on_server_started,
                    self._system_adapter.on_server_stopped,
                )
            )
        except (KeyboardInterrupt, SystemExit):
            pass
        except Exception:
            logger.exception('Web-PDB: unexpected error in server thread')
        finally:
            self._loop.close()
            self._loop = None

    def close(self) -> None:
        self._system_adapter.abort()
        self._server.stop()
