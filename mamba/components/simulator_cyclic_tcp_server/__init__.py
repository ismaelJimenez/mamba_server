""" Component for handling socket TMTC """

import os
import threading
import socketserver
import time

from rx import operators as op

from mamba.components import ComponentBase
from mamba.components.observable_types import RawTelecommand, \
    RawTelemetry, Empty
from mamba.exceptions import ComponentConfigException


class ThreadedCyclicTmHandler(socketserver.BaseRequestHandler):
    """
    The request handler class for the socket server.

    It is instantiated once per connection to the server, and must
    override the handle() method to implement communication to the
    client.
    """
    def handle(self):
        # Send incoming data to raw_tc
        while True:
            try:
                for telemetry, value in self.server.telemetries.items():
                    self.server.log_dev(
                        fr' - Published socket TM: {telemetry} {value}')
                    self.request.sendall(
                        f'{telemetry} {value}{self.server.eom}'.encode(
                            'utf-8'))
                    time.sleep(1)
            except BrokenPipeError:
                break

        self.server.log_info('Remote socket connection has been closed')


class ThreadedCyclicTmServer(socketserver.ThreadingMixIn,
                             socketserver.TCPServer):
    pass


class ThreadedTcHandler(socketserver.BaseRequestHandler):
    """
    The request handler class for the socket server.

    It is instantiated once per connection to the server, and must
    override the handle() method to implement communication to the
    client.
    """
    def handle(self):
        # Send incoming data to raw_tc
        while True:
            # self.request is the TCP socket connected to the client
            data = str(self.request.recv(1024), 'utf-8')
            if not data:
                break

            print(data.split(self.server.eom))

            for cmd in data.split(self.server.eom)[:-1]:
                print(f"MY TC: {data}")
                cmd = cmd.split(" ")
                print(f"MY TC2: {cmd}")
                self.server.telemetries[cmd[0]] = cmd[1]

        self.server.log_info('Remote socket connection has been closed')


class ThreadedTcServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    pass


class Driver(ComponentBase):
    """ Plugin base class """
    def __init__(self, context, local_config=None):
        super(Driver, self).__init__(os.path.dirname(__file__), context,
                                     local_config)

        # Define custom variables
        self._eom_q = self._configuration['device']['eom']['TCPIP INSTR']['q']
        self._eom_r = self._configuration['device']['eom']['TCPIP INSTR']['r']

        self._dict = {}

        for key, value in self._configuration['device']['properties'].items():
            self._dict[key] = value.get('default')

        self._tm_server = None
        self._tm_server_thread = None
        self._tc_server = None
        self._tc_server_thread = None

        # Initialize observers
        self._register_observers()

    def _register_observers(self):
        # Quit is sent to command App finalization
        self._context.rx['quit'].pipe(
            op.filter(lambda value: isinstance(value, Empty))).subscribe(
                on_next=self._close)

    def initialize(self):
        if not all(key in self._configuration
                   for key in ['host', 'tc_port', 'tm_port']):
            raise ComponentConfigException(
                "Missing required elements in component configuration")

        # Create the socket server, binding to host and port
        socketserver.TCPServer.allow_reuse_address = True
        self._tm_server = ThreadedCyclicTmServer(
            (self._configuration['host'], self._configuration['tm_port']),
            ThreadedCyclicTmHandler)
        self._tm_server.log_dev = self._log_dev
        self._tm_server.log_info = self._log_info
        self._tm_server.telemetries = self._dict
        self._tm_server.eom = self._eom_r

        # Start a thread with the server -- that thread will then start one
        # more thread for each request
        self._tm_server_thread = threading.Thread(
            target=self._tm_server.serve_forever)

        # Exit the server thread when the main thread terminates
        self._tm_server_thread.daemon = True
        self._tm_server_thread.start()
        print("TM Server loop running in thread:", self._tm_server_thread.name)

        # Create the socket server, binding to host and port
        self._tc_server = ThreadedTcServer(
            (self._configuration['host'], self._configuration['tc_port']),
            ThreadedTcHandler)
        self._tc_server.log_dev = self._log_dev
        self._tc_server.log_info = self._log_info
        self._tc_server.telemetries = self._dict
        self._tc_server.eom = self._eom_q

        # Start a thread with the server -- that thread will then start one
        # more thread for each request
        self._tc_server_thread = threading.Thread(
            target=self._tc_server.serve_forever)

        # Exit the server thread when the main thread terminates
        self._tc_server_thread.daemon = True
        self._tc_server_thread.start()
        print("TC Server loop running in thread:", self._tc_server_thread.name)

    def _close(self, rx_value=None):
        """ Entry point for closing application

            Args:
                rx_value (Empty): The value published by the subject.
        """
        self._tm_server.shutdown()
        self._tm_server = None
        self._tc_server.shutdown()
        self._tc_server = None
