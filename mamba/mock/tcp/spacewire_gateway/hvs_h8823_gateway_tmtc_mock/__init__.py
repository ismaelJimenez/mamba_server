""" Component for simulating a simple TCP server equipment """
import os
import time
import threading
import socketserver
from typing import Optional, Dict
import queue

from stringparser import Parser

from mamba.core.msg import Empty
from mamba.core.context import Context
from mamba.core.component_base import InstrumentDriver

cyclic_tm_delay = 10


class H8823GatewayTmTcMock(InstrumentDriver):
    """ Simple TCP Server Mock """
    def __init__(self,
                 context: Context,
                 local_config: Optional[dict] = None) -> None:
        super().__init__(os.path.dirname(__file__), context, local_config)

        self._tm_server: Optional[ThreadedCyclicTmServer] = None
        self._tm_server_thread: Optional[threading.Thread] = None
        self._tc_server: Optional[ThreadedTcpServer] = None
        self._tc_server_thread: Optional[threading.Thread] = None

        self._cyclic_tm_mapping: Dict[str, str] = {}
        self._tc_mapping: Dict[str, str] = {}
        global cyclic_tm_delay
        cyclic_tm_delay = self._configuration['instrument']['tm_period']

        self._app_running = True

        self.tc_ack_queue: queue.Queue = queue.Queue()

    def _close(self, rx_value: Optional[Empty] = None) -> None:
        """ Entry point for closing the component """
        if self._tm_server is not None:
            self._tm_server.do_run = False
            self._tm_server.shutdown()
        if self._tc_server is not None:
            self._tc_server.do_run = False
            self._tc_server.shutdown()

        if self._tm_server_thread is not None:
            self._tm_server_thread.join()
        if self._tc_server_thread is not None:
            self._tc_server_thread.join()

    def initialize(self) -> None:
        """ Entry point for component initialization """
        # Compose shared memory data dictionaries
        for key, parameter_info in self._configuration['parameters'].items():
            self._shared_memory[key] = parameter_info.get('initial_value')

            cmd_list = parameter_info.get('get',
                                          {}).get('instrument_command', {})
            if len(cmd_list) > 0:
                cmd_type = list(cmd_list[0].keys())[0]
                cmd = list(cmd_list[0].values())[0]

                if cmd_type == 'cyclic':
                    self._cyclic_tm_mapping[key] = cmd

            cmd_list = parameter_info.get('set',
                                          {}).get('instrument_command', {})
            if len(cmd_list) > 0:
                cmd_type = list(cmd_list[0].keys())[0]
                cmd = list(cmd_list[0].values())[0]

                self._tc_mapping[key] = cmd

        # Create the TM socket server, binding to host and port
        socketserver.TCPServer.allow_reuse_address = True
        self._tm_server = ThreadedCyclicTmServer(
            (self._instrument.address, self._instrument.tm_port),
            ThreadedCyclicTmHandler, self)

        # Start a thread with the server -- that thread will then start one
        # more thread for each request
        self._tm_server_thread = threading.Thread(
            target=self._tm_server.serve_forever)

        # Exit the server thread when the main thread terminates
        self._tm_server_thread.daemon = True
        self._tm_server_thread.start()
        self._log_info(f'Cyclic TM Server running in thread: '
                       f'{self._tm_server_thread.name}')

        # Create the TC socket server, binding to host and port
        self._tc_server = ThreadedTcpServer(
            (self._instrument.address, self._instrument.tc_port),
            ThreadedTcpHandler, self)

        # Start a thread with the server -- that thread will then start one
        # more thread for each request
        self._tc_server_thread = threading.Thread(
            target=self._tc_server.serve_forever)

        # Exit the server thread when the main thread terminates
        self._tc_server_thread.daemon = True
        self._tc_server_thread.start()
        self._log_info(f'TC Server running in thread: '
                       f'{self._tc_server_thread.name}')

class ThreadedCyclicTmHandler(socketserver.BaseRequestHandler):
    """
    The request handler class for the socket server.

    It is instantiated once per connection to the server, and must
    override the handle() method to implement communication to the
    client.
    """
    def handle(self):
        # Send  telemetries
        while self.server.do_run:
            try:
                for key, value in self.server.telemetry_map.items():
                    socket_tm = value.format(self.server.telemetries[key])
                    self.server.log_dev(
                        fr' - Publish socket cyclic TM: {socket_tm}')
                    self.request.sendall(
                        f'{time.time()} {socket_tm}{self.server.eom_w}'.encode(
                            self.server.encoding))

                global cyclic_tm_delay

                try:
                    start_time = time.time()
                    while time.time()-start_time < cyclic_tm_delay:
                        tc_ack = self.server.queue.get(True, cyclic_tm_delay - (time.time()-start_time))

                        self.request.sendall(
                            f'{time.time()} {tc_ack}{self.server.eom_w}'.encode(
                                self.server.encoding))

                except queue.Empty:
                    continue

            except BrokenPipeError:
                break

        self.server.log_info('Remote socket connection has been closed')


class ThreadedCyclicTmServer(socketserver.ThreadingMixIn,
                             socketserver.TCPServer):
    """  Telemetry server """
    def __init__(self, server_address, request_handler_class,
                 parent: H8823GatewayTmTcMock) -> None:
        super().__init__(server_address, request_handler_class)
        self.log_dev = parent._log_dev
        self.log_info = parent._log_info
        self.telemetries = parent._shared_memory
        self.eom_w = parent._instrument.terminator_write
        self.encoding = parent._instrument.encoding
        self.telemetry_map = parent._cyclic_tm_mapping
        self.queue = parent.tc_ack_queue

        self.do_run = True


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
                processed = False
                for key, val in self.server.tc_mapping.items():
                    try:
                        args = Parser(val)(cmd)

                        if (key == 'spw_link_enabled' or key == 'spw_link_autostart' or
                            key == 'spw_link_timecode_enabled' or key == 'spw_link_start'):
                            value_split = self.server.telemetries[key].split(" ")
                            status = 1 if args[0] == 'ENA' else 0
                            value_split[int(args[1])] = str(status)
                            self.server.telemetries[key] = " ".join(value_split)
                        elif key == 'spw_link_tx_rate':
                            value_split = self.server.telemetries[key].split(" ")
                            value_split[int(args[0])] = str(args[1])
                            self.server.telemetries[key] = " ".join(value_split)
                        elif key == 'tm_period':
                            global cyclic_tm_delay
                            cyclic_tm_delay = int(args[0])

                        processed = True

                    except ValueError:
                        continue

                if processed:
                    self.server.queue.put(cmd)
                else:
                    self.server.queue.put(cmd.replace('_TC_', '_ER_'))

        self.server.log_info('Remote socket connection has been closed')


class ThreadedTcpServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    """ TC server to modify the telemetries """
    def __init__(self, server_address, request_handler_class,
                 parent: H8823GatewayTmTcMock) -> None:
        super().__init__(server_address, request_handler_class)
        self.log_dev = parent._log_dev
        self.log_info = parent._log_info
        self.telemetries = parent._shared_memory
        self.eom_r = parent._instrument.terminator_read
        self.eom_w = parent._instrument.terminator_write
        self.encoding = parent._instrument.encoding
        self.tc_mapping = parent._tc_mapping
        self.queue = parent.tc_ack_queue

        self.do_run = True
