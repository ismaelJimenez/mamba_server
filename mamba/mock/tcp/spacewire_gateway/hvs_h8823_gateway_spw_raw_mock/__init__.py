""" Component for simulating a simple TCP server equipment """
import os
import threading
import socketserver
from typing import Optional

from mamba.core.msg import Empty
from mamba.core.context import Context
from mamba.core.component_base import InstrumentDriver


class H8823GatewaySpwRawMock(InstrumentDriver):
    """ Simple TCP Server Mock """
    def __init__(self,
                 context: Context,
                 local_config: Optional[dict] = None) -> None:
        super().__init__(os.path.dirname(__file__), context, local_config)

        self._server: Optional[ThreadedTcpServer] = None
        self._server_thread: Optional[threading.Thread] = None

        self._app_running = True

    def _close(self, rx_value: Optional[Empty] = None) -> None:
        """ Entry point for closing the component """
        if self._server is not None:
            self._server.do_run = False
            self._server.shutdown()

        if self._server_thread is not None:
            self._server_thread.join()

    def initialize(self) -> None:
        """ Entry point for component initialization """
        # Compose shared memory data dictionaries
        for key, parameter_info in self._configuration['parameters'].items():
            self._shared_memory[key] = parameter_info.get('initial_value')

        # Create the TM socket server, binding to host and port
        socketserver.TCPServer.allow_reuse_address = True
        self._server = ThreadedTcpServer(
            (self._instrument.address, self._instrument.port),
            ThreadedTcpHandler, self)

        # Start a thread with the server -- that thread will then start one
        # more thread for each request
        self._server_thread = threading.Thread(
            target=self._server.serve_forever)

        # Exit the server thread when the main thread terminates
        self._server_thread.daemon = True
        self._server_thread.start()
        self._log_info(f'Simple TCP Server running in thread: '
                       f'{self._server_thread.name}')


class ThreadedTcpHandler(socketserver.BaseRequestHandler):
    """
    The request handler class for the socket server.

    It is instantiated once per connection to the server, and must
    override the handle() method to implement communication to the
    client.
    """
    def handle(self):
        # Server to receive remote commands
        while self.server.do_run:
            # self.request is the TCP socket connected to the client
            data = str(self.request.recv(1024), self.server.encoding)
            if not data:
                break

            for cmd in data.split(self.server.eom_r)[:-1]:
                self.server.log_dev(fr' - Received socket TC: {cmd}')

                if cmd[0] != '0':
                    self.request.sendall(
                        bytes(f'{cmd}{self.server.eom_w}',
                              self.server.encoding))

        self.server.log_info('Remote socket connection has been closed')


class ThreadedTcpServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    """ TC server to modify the telemetries """
    def __init__(self, server_address, request_handler_class,
                 parent: H8823GatewaySpwRawMock) -> None:
        super().__init__(server_address, request_handler_class)
        self.log_dev = parent._log_dev
        self.log_info = parent._log_info
        self.telemetries = parent._shared_memory
        self.eom_r = parent._instrument.terminator_read
        self.eom_w = parent._instrument.terminator_write
        self.encoding = parent._instrument.encoding

        self.do_run = True
