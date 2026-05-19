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
