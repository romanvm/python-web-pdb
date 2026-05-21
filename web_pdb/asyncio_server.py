"""
Asyncio-based HTTP server with WebSocket support for Web-PDB
"""

from __future__ import annotations

try:  # Kodi compatibility fix
    import xbmc

    if not getattr(xbmc, '__kodistubs__', False):
        import sys

        sys.modules['_asyncio'] = None  # See: https://kodi.wiki/view/Python_Problems#asyncio
except ImportError:
    pass

import asyncio
import base64
import gzip
import hashlib
import json
import logging
import mimetypes
import queue
import socket
import struct
from pathlib import Path
from urllib.parse import unquote

__all__ = ['AsyncioServer']

logger = logging.getLogger(__name__)

_WS_MAGIC = '258EAFA5-E914-47DA-95CA-C5AB0DC85B11'
_GZIP_TYPES = ('text/', 'application/json', 'application/javascript', 'image/svg+xml')
_GZIP_MIN_SIZE = 1024
_MAX_HEADER_SIZE = 8192
_WS_OUTBOUND_QUEUE_SIZE = 32
_WS_MAX_FRAME_SIZE = 10 * 1024 * 1024

_this_dir = Path(__file__).parent
_static_dir = _this_dir / 'static'
_static_dir_resolved = _static_dir.resolve()
_index_file = _this_dir / 'templates' / 'index.html'

# Opcode constants
_OP_CONTINUATION = 0x0
_OP_TEXT = 0x1
_OP_BINARY = 0x2
_OP_CLOSE = 0x8
_OP_PING = 0x9
_OP_PONG = 0xA


def _ws_accept_key(key: str) -> str:
    digest = hashlib.sha1((key + _WS_MAGIC).encode()).digest()
    return base64.b64encode(digest).decode()


def _ws_encode_frame(payload: bytes, opcode: int = _OP_TEXT) -> bytes:
    length = len(payload)
    if length <= 125:
        header = bytes([0x80 | opcode, length])
    elif length <= 65535:
        header = bytes([0x80 | opcode, 126]) + struct.pack('>H', length)
    else:
        header = bytes([0x80 | opcode, 127]) + struct.pack('>Q', length)
    return header + payload


async def _ws_read_frame(reader: asyncio.StreamReader):
    """Read one WebSocket frame; return (fin, opcode, payload_bytes) or raise."""
    header = await reader.readexactly(2)
    fin = (header[0] & 0x80) != 0
    opcode = header[0] & 0x0F
    masked = (header[1] & 0x80) != 0
    length = header[1] & 0x7F

    if length == 126:
        length = struct.unpack('>H', await reader.readexactly(2))[0]
    elif length == 127:
        length = struct.unpack('>Q', await reader.readexactly(8))[0]
    elif length > _WS_MAX_FRAME_SIZE:
        raise ValueError(f'WebSocket frame too large: {length} bytes')

    mask_key = await reader.readexactly(4) if masked else b''
    payload = bytearray(await reader.readexactly(length))

    if masked:
        for i in range(length):
            payload[i] ^= mask_key[i % 4]

    return fin, opcode, bytes(payload)


def _gzip_if_accepted(body: bytes, content_type: str, accept_encoding: str) -> tuple:
    """Return (body, extra_headers) with gzip applied when appropriate."""
    if (
        'gzip' in accept_encoding
        and len(body) > _GZIP_MIN_SIZE
        and any(content_type.startswith(t) for t in _GZIP_TYPES)
    ):
        body = gzip.compress(body)
        return body, {'Content-Encoding': 'gzip'}
    return body, {}


def _build_response(
    status: str,
    body: bytes,
    content_type: str,
    extra_headers: dict | None = None,
) -> bytes:
    headers = {
        'Content-Type': content_type,
        'Content-Length': str(len(body)),
        'Connection': 'close',
    }
    if extra_headers:
        headers.update(extra_headers)
    header_lines = ''.join(f'{k}: {v}\r\n' for k, v in headers.items())
    return f'HTTP/1.1 {status}\r\n{header_lines}\r\n'.encode() + body


class _WebSocketConnection:
    def __init__(self, reader, writer, input_queue: queue.Queue):
        self._reader = reader
        self._writer = writer
        self._input_queue = input_queue
        self._send_queue: asyncio.Queue = asyncio.Queue(maxsize=_WS_OUTBOUND_QUEUE_SIZE)
        self._closed = False

    def send(self, message: str) -> None:
        if self._closed:
            return
        payload = message.encode('utf-8')
        try:
            self._send_queue.put_nowait(payload)
        except asyncio.QueueFull:
            # Drop the oldest ping and enqueue the new one
            try:
                self._send_queue.get_nowait()
            except asyncio.QueueEmpty:
                pass
            try:
                self._send_queue.put_nowait(payload)
            except asyncio.QueueFull:
                pass

    async def run(self) -> None:
        writer_task = asyncio.create_task(self._writer_loop())
        try:
            await self._reader_loop()
        finally:
            self._closed = True
            writer_task.cancel()
            try:
                await writer_task
            except (asyncio.CancelledError, Exception):
                # CancelledError is not a subclass of Exception in 3.8+; both are expected here
                pass
            try:
                self._writer.write(_ws_encode_frame(b'', _OP_CLOSE))
                await self._writer.drain()
            except Exception:
                logger.debug('WebSocket close frame could not be sent', exc_info=True)
            try:
                self._writer.close()
            except Exception:
                logger.debug('WebSocket writer close failed', exc_info=True)

    async def _reader_loop(self) -> None:
        while True:
            try:
                fin, opcode, payload = await _ws_read_frame(self._reader)
            except (asyncio.IncompleteReadError, ConnectionError, EOFError):
                break
            if opcode in (_OP_TEXT, _OP_BINARY, _OP_CONTINUATION):
                if not fin or opcode == _OP_CONTINUATION:
                    continue  # We don't reassemble fragmented messages
                text = payload.decode('utf-8', errors='replace')
                self._input_queue.put(text)
            elif opcode == _OP_PING:
                self._writer.write(_ws_encode_frame(payload, _OP_PONG))
                try:
                    await self._writer.drain()
                except Exception:
                    break
            elif opcode == _OP_CLOSE:
                break

    async def _writer_loop(self) -> None:
        while True:
            payload = await self._send_queue.get()
            try:
                self._writer.write(_ws_encode_frame(payload, _OP_TEXT))
                await self._writer.drain()
            except Exception:
                break


class AsyncioServer:
    def __init__(self, host: str, port: int, frame_data, input_queue: queue.Queue):
        self._host = host
        self._port = port
        self._frame_data = frame_data
        self._input_queue = input_queue
        self._connections: set[_WebSocketConnection] = set()
        self._loop: asyncio.AbstractEventLoop | None = None
        self._stop_event: asyncio.Event | None = None
        self.server_name: str = ''
        self.server_port: int = 0

    def _broadcast(self, message: str) -> None:
        for conn in tuple(self._connections):
            conn.send(message)

    def broadcast(self, message: str) -> None:
        if self._loop is not None:
            try:
                self._loop.call_soon_threadsafe(self._broadcast, message)
            except RuntimeError:
                pass

    def stop(self) -> None:
        if self._loop is not None and self._stop_event is not None:
            try:
                self._loop.call_soon_threadsafe(self._stop_event.set)
            except RuntimeError:
                pass

    async def run(self, is_abort_requested, on_started, on_stopped) -> None:
        self._loop = asyncio.get_running_loop()
        self._stop_event = asyncio.Event()

        server = await asyncio.start_server(self._handle_connection, self._host, self._port)
        try:
            sock = server.sockets[0]
            addr = sock.getsockname()
            self.server_port = addr[1]
            self.server_name = socket.getfqdn(self._host or '')
            on_started(self.server_name, self.server_port)

            async def _abort_watcher():
                while not is_abort_requested():
                    await asyncio.sleep(0.1)
                self._stop_event.set()

            watcher = asyncio.create_task(_abort_watcher())
            try:
                await self._stop_event.wait()
            finally:
                watcher.cancel()

            # Stop accepting new connections.
            server.close()

            # Cancel in-flight connection handlers before wait_closed(), which on
            # Python 3.12+ blocks until every active client connection finishes.
            current = asyncio.current_task()
            pending = {
                t for t in asyncio.all_tasks(self._loop)
                if t is not current and not t.done()
            }
            for task in pending:
                task.cancel()
            if pending:
                await asyncio.gather(*pending, return_exceptions=True)

            await server.wait_closed()
        finally:
            on_stopped()

    async def _handle_connection(
        self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter
    ) -> None:
        try:
            await self._process_request(reader, writer)
        except Exception:
            logger.exception('Unhandled error in HTTP connection handler')
        finally:
            try:
                writer.close()
            except Exception:
                pass

    async def _process_request(
        self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter
    ) -> None:
        try:
            raw = await asyncio.wait_for(reader.readuntil(b'\r\n\r\n'), timeout=10.0)
        except asyncio.LimitOverrunError:
            writer.write(b'HTTP/1.1 414 Request-URI Too Long\r\nConnection: close\r\n\r\n')
            await writer.drain()
            return
        except (asyncio.TimeoutError, asyncio.IncompleteReadError, ConnectionError):
            return

        if len(raw) > _MAX_HEADER_SIZE:
            writer.write(b'HTTP/1.1 414 Request-URI Too Long\r\nConnection: close\r\n\r\n')
            await writer.drain()
            return

        lines = raw.split(b'\r\n')
        try:
            request_line = lines[0].decode('latin-1')
            method, raw_path, _ = request_line.split()
        except (ValueError, UnicodeDecodeError):
            writer.write(b'HTTP/1.1 400 Bad Request\r\nConnection: close\r\n\r\n')
            await writer.drain()
            return

        headers: dict[str, str] = {}
        for line in lines[1:]:
            if b':' in line:
                k, _, v = line.partition(b':')
                headers[k.strip().lower().decode('latin-1')] = v.strip().decode('latin-1')

        path = unquote(raw_path.split('?')[0])
        accept_encoding = headers.get('accept-encoding', '')

        if method != 'GET':
            writer.write(b'HTTP/1.1 405 Method Not Allowed\r\nConnection: close\r\n\r\n')
            await writer.drain()
            return

        if path == '/':
            await self._serve_index(writer, accept_encoding)
        elif path == '/frame-data':
            await self._serve_frame_data(writer, accept_encoding)
        elif path.startswith('/static/'):
            await self._serve_static(writer, path[len('/static/') :], accept_encoding)
        elif path == '/ws':
            await self._serve_websocket(reader, writer, headers)
        else:
            writer.write(b'HTTP/1.1 404 Not Found\r\nConnection: close\r\n\r\n')
            await writer.drain()

    async def _serve_index(self, writer, accept_encoding: str) -> None:
        body = _index_file.read_bytes()
        body, gz_headers = _gzip_if_accepted(body, 'text/html; charset=utf-8', accept_encoding)
        response = _build_response('200 OK', body, 'text/html; charset=utf-8', gz_headers)
        writer.write(response)
        await writer.drain()

    async def _serve_frame_data(self, writer, accept_encoding: str) -> None:
        body = json.dumps(self._frame_data.contents).encode('utf-8')
        body, gz_headers = _gzip_if_accepted(body, 'application/json', accept_encoding)
        extra = {'Cache-Control': 'no-store'}
        extra.update(gz_headers)
        response = _build_response('200 OK', body, 'application/json', extra)
        writer.write(response)
        await writer.drain()

    async def _serve_static(self, writer, rel_path: str, accept_encoding: str) -> None:
        try:
            requested = (_static_dir / rel_path).resolve()
        except Exception:
            writer.write(b'HTTP/1.1 400 Bad Request\r\nConnection: close\r\n\r\n')
            await writer.drain()
            return

        if _static_dir_resolved not in requested.parents:
            writer.write(b'HTTP/1.1 403 Forbidden\r\nConnection: close\r\n\r\n')
            await writer.drain()
            return

        if not requested.is_file():
            writer.write(b'HTTP/1.1 404 Not Found\r\nConnection: close\r\n\r\n')
            await writer.drain()
            return

        body = requested.read_bytes()
        content_type = mimetypes.guess_type(str(requested))[0] or 'application/octet-stream'
        body, gz_headers = _gzip_if_accepted(body, content_type, accept_encoding)
        response = _build_response('200 OK', body, content_type, gz_headers)
        writer.write(response)
        await writer.drain()

    async def _serve_websocket(self, reader, writer, headers: dict) -> None:
        ws_key = headers.get('sec-websocket-key', '').strip()
        ws_version = headers.get('sec-websocket-version', '').strip()

        if not ws_key or ws_version != '13':
            writer.write(b'HTTP/1.1 400 Bad Request\r\nConnection: close\r\n\r\n')
            await writer.drain()
            return

        accept = _ws_accept_key(ws_key)
        handshake = (
            'HTTP/1.1 101 Switching Protocols\r\n'
            'Upgrade: websocket\r\n'
            'Connection: Upgrade\r\n'
            f'Sec-WebSocket-Accept: {accept}\r\n'
            '\r\n'
        )
        writer.write(handshake.encode())
        await writer.drain()

        conn = _WebSocketConnection(reader, writer, self._input_queue)
        self._connections.add(conn)
        try:
            await conn.run()
        finally:
            self._connections.discard(conn)
