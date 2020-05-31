""" Component for handling socket TMTC """

import os
import threading
import socketserver

from rx import operators as op

from mamba.components import ComponentBase
from mamba.core.msg import Raw, Empty
from mamba.core.exceptions import ComponentConfigException


class ThreadedTCPRequestHandler(socketserver.BaseRequestHandler):
    """
    The request handler class for the socket server.

    It is instantiated once per connection to the server, and must
    override the handle() method to implement communication to the
    client.
    """
    def handle(self):
        # Register observer for raw_tm
        observer = self.server.raw_tm.pipe(
            op.filter(lambda value: isinstance(value, Raw))).subscribe(
                on_next=self.send_tm)

        # Send incoming data to raw_tc
        while True:
            # self.request is the TCP socket connected to the client
            data = str(self.request.recv(1024), 'utf-8')
            if not data:
                break
            self.server.log_dev(fr' -> Received socket TC: {data}')
            self.server.raw_tc.on_next(Raw(data))

        # Dispose observer when connection is closed
        observer.dispose()

        self.server.log_info('Remote socket connection has been closed')

    def send_tm(self, raw_tm: Raw):
        """ Send msg telemetry over the socket connection """
        self.server.log_dev(fr' <- Published socket TM: {raw_tm.raw}')
        self.request.sendall(raw_tm.raw.encode('utf-8'))


class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    pass


class Driver(ComponentBase):
    """ Plugin base class """
    def __init__(self, context, local_config=None):
        super(Driver, self).__init__(os.path.dirname(__file__), context,
                                     local_config)

        # Define custom variables
        self._server = None
        self._server_thread = None

        # Initialize observers
        self._register_observers()

    def _register_observers(self):
        # Quit is sent to command App finalization
        self._context.rx['quit'].pipe(
            op.filter(lambda value: isinstance(value, Empty))).subscribe(
                on_next=self._close)

    def initialize(self):
        if not all(key in self._configuration for key in ['host', 'port']):
            raise ComponentConfigException(
                "Missing required elements in component configuration")

        # Create the socket server, binding to host and port
        socketserver.TCPServer.allow_reuse_address = True
        self._server = ThreadedTCPServer(
            (self._configuration['host'], self._configuration['port']),
            ThreadedTCPRequestHandler)
        self._server.raw_tc = self._context.rx['raw_tc']
        self._server.raw_tm = self._context.rx['raw_tm']
        self._server.log_dev = self._log_dev
        self._server.log_info = self._log_info

        # Start a thread with the server -- that thread will then start one
        # more thread for each request
        self._server_thread = threading.Thread(
            target=self._server.serve_forever)

        # Exit the server thread when the main thread terminates
        self._server_thread.daemon = True
        self._server_thread.start()
        print("Server loop running in thread:", self._server_thread.name)

    def _close(self, rx_value=None):
        """ Entry point for closing application

            Args:
                rx_value (Empty): The value published by the subject.
        """
        self._server.shutdown()
        self._server = None
