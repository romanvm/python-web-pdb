import queue

from asyncore_wsgi import AsyncWebSocketHandler, make_server

from .system_adapter import SystemAdapter
from .wsgi_app import app


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


class ServerAdapter:
    def __init__(self, host, port):
        self._system_adapter = SystemAdapter()
        self._httpd = make_server(host, port, app, ws_handler_class=WebConsoleSocket)

    @property
    def web_socket_input_queue(self):
        return WebConsoleSocket.input_queue

    @staticmethod
    def web_socket_broadcast(message):
        WebConsoleSocket.broadcast(message)

    def serve_forever(self) -> None:
        is_started = False
        while not self._system_adapter.is_abort_requested():
            if not is_started:
                self._system_adapter.on_server_started(self._httpd.server_name, self._httpd.server_port)
                is_started = True
            try:
                self._httpd.handle_request()
            except (KeyboardInterrupt, SystemExit):
                break
        self._httpd.handle_close()
        self._system_adapter.on_server_stopped()

    def close(self):
        self._system_adapter.abort()
