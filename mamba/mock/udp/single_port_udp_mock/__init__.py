""" Component for simulating a simple UDP server equipment """

import threading
import socketserver
import time
import os
from typing import Optional

from mamba.core.msg import Empty
from mamba.core.context import Context
from mamba.core.component_base import InstrumentDriver


class SinglePortUdpMock(InstrumentDriver):
    def __init__(self,
                 context: Context,
                 local_config: Optional[dict] = None) -> None:
        super().__init__(os.path.dirname(__file__), context, local_config)

        self._server: Optional[ThreadedUDPServer] = None
        self._server_thread: Optional[threading.Thread] = None

    def _close(self, rx_value: Optional[Empty] = None) -> None:
        """ Entry point for closing the component """
        if self._server is not None:
            self._server.do_run = False
            self._server.shutdown()

        if self._server_thread is not None:
            self._server_thread.join()

    def initialize(self) -> None:
        """ Entry point for component initialization """
        self._server = ThreadedUDPServer(
            (self._instrument.address, self._instrument.port),
            ThreadedUDPRequestHandler, self)

        # Start a thread with the server -- that thread will then start one
        # more thread for each request
        self._server_thread = threading.Thread(
            target=self._server.serve_forever)
        # Exit the server thread when the main thread terminates
        self._server_thread.daemon = True
        self._server_thread.start()


class ThreadedUDPRequestHandler(socketserver.BaseRequestHandler):
    def handle(self):
        data = self.request[0]
        socket = self.request[1]

        cmd_id = int.from_bytes(data[4:8], 'big')
        param_id = int.from_bytes(data[8:12], 'big')
        path_name = str(data[12:-5], 'ascii')

        self.server.log_dev(f'[{time.time()}] Incoming: {data}')
        self.server.log_dev(f' - Start of message: {data[0:4]}')
        self.server.log_dev(f' - Command Id: {cmd_id}')
        self.server.log_dev(f' - Parameter Id: {param_id}')
        self.server.log_dev(f' - Path name: {path_name}')
        self.server.log_dev(f' - End of message: {data[-4:]}')

        if cmd_id in [1, 4, 5]:
            reply = bytes('SOME', 'ascii') + (0x101).to_bytes(
                4, 'big') + (0).to_bytes(4, 'big') + bytes('EOME', 'ascii')
        else:
            reply = bytes('SOME', 'ascii') + (0x101).to_bytes(
                4, 'big') + (1).to_bytes(4, 'big') + bytes('EOME', 'ascii')

        self.server.log_dev(f'[{time.time()}] Outgoing: {reply}')

        socket.sendto(reply, self.client_address)


class ThreadedUDPServer(socketserver.ThreadingMixIn, socketserver.UDPServer):
    def __init__(self, server_address, request_handler_class,
                 parent: SinglePortUdpMock) -> None:
        super().__init__(server_address, request_handler_class)
        self.log_dev = parent._log_dev
        self.log_info = parent._log_info
        self.telemetries = parent._shared_memory
        self.eom_r = parent._instrument.terminator_read
        self.eom_w = parent._instrument.terminator_write
        self.encoding = parent._instrument.encoding
