############################################################################
#
# Copyright (c) Mamba Developers. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#
############################################################################
""" Component for simulating a simple TCP server equipment """

import os
import time
import threading
import socketserver
from typing import Optional, Dict

from mamba.core.msg import Empty
from mamba.core.context import Context
from mamba.core.component_base import InstrumentDriver


class CyclicTmTcpMock(InstrumentDriver):
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
        self._cyclic_tm_delay = self._configuration['instrument']['cyclic_tm']

        self._app_running = True

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

            tm_format = parameter_info.get('cyclic_tm_server',
                                           {}).get('format', {})
            if len(tm_format) > 0:
                self._cyclic_tm_mapping[key] = tm_format

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
                        f'{socket_tm}{self.server.eom_w}'.encode(
                            self.server.encoding))
                time.sleep(self.server.cyclic_tm_delay)
            except BrokenPipeError:
                break

        self.server.log_info('Remote socket connection has been closed')


class ThreadedCyclicTmServer(socketserver.ThreadingMixIn,
                             socketserver.TCPServer):
    """  Telemetry server """
    def __init__(self, server_address, request_handler_class,
                 parent: CyclicTmTcpMock) -> None:
        super().__init__(server_address, request_handler_class)
        self.log_dev = parent._log_dev
        self.log_info = parent._log_info
        self.telemetries = parent._shared_memory
        self.eom_w = parent._instrument.terminator_write
        self.encoding = parent._instrument.encoding
        self.telemetry_map = parent._cyclic_tm_mapping
        self.cyclic_tm_delay = parent._cyclic_tm_delay

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
                cmd = cmd.split(" ")
                if len(cmd) >= 2:
                    key = cmd[0].lower()

                    if key in self.server.telemetries:
                        self.server.telemetries[cmd[0].lower()] = cmd[1]
                    else:
                        self.server.telemetries[
                            'syst_err'] = '1,_Command_Error'
                elif cmd[0][-1] == '?':
                    key = cmd[0][:-1].lower().replace(':', '_')

                    if key[0] == '*':
                        key = key[1:]

                    if key in self.server.telemetries:
                        self.request.sendall(
                            bytes(
                                f'{self.server.telemetries[key]}'
                                f'{self.server.eom_w}', self.server.encoding))
                        if key == 'syst_err':
                            self.server.telemetries['syst_err'] = '0,_No_Error'
                    else:
                        self.request.sendall(
                            bytes(f'KeyError{self.server.eom_w}',
                                  self.server.encoding))
                        self.server.telemetries[
                            'syst_err'] = '1,_Command_Error'
                else:
                    key = cmd[0].lower()

                    if key[0] == '*':
                        key = key[1:]

                    if key not in self.server.telemetries:
                        self.server.telemetries[
                            'syst_err'] = '1, Command error'

        self.server.log_info('Remote socket connection has been closed')


class ThreadedTcpServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    """ TC server to modify the telemetries """
    def __init__(self, server_address, request_handler_class,
                 parent: CyclicTmTcpMock) -> None:
        super().__init__(server_address, request_handler_class)
        self.log_dev = parent._log_dev
        self.log_info = parent._log_info
        self.telemetries = parent._shared_memory
        self.eom_r = parent._instrument.terminator_read
        self.eom_w = parent._instrument.terminator_write
        self.encoding = parent._instrument.encoding

        self.do_run = True
