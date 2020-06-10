""" Single Port TCP controller base """
from typing import Optional
import os
import socket
import threading

from stringparser import Parser

from mamba.core.component_base import TcpInstrumentDriver
from mamba.core.context import Context
from mamba.core.msg import ServiceResponse, ParameterType


class ThreadedCyclicTmHandler:
    def __init__(self, sock, eom, shared_memory, rx, log_info,
                 cyclic_tm_mapping, provider):
        while True:
            try:
                # self.request is the TCP socket connected to the client
                data = str(sock.recv(1024), 'utf-8')
                if not data:
                    break

                for cmd in data.split(eom)[:-1]:
                    for key, val in cyclic_tm_mapping.items():
                        try:
                            shared_memory[key] = Parser(val)(cmd)

                            result = ServiceResponse(provider=provider,
                                                     id=key,
                                                     type=ParameterType.get,
                                                     value=shared_memory[key])

                            rx['io_result'].on_next(result)

                        except ValueError:
                            continue

            except OSError:
                break

        log_info('Remote Cyclic TM socket connection has been closed')


class CyclicTmTcpController(TcpInstrumentDriver):
    """ Simple TCP controller base class """
    def __init__(self,
                 context: Context,
                 local_config: Optional[dict] = None) -> None:
        super().__init__(os.path.dirname(__file__), context, local_config)

        self._inst_cyclic_tm = None  # self._inst will be kept for telecommands
        self._inst_cyclic_tm_thread: Optional[threading.Thread] = None

        self._cyclic_tm_mapping = {}

    def _instrument_connect(self, result: ServiceResponse) -> None:
        try:
            self._inst = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self._inst.connect(
                (self._instrument.address, self._instrument.tc_port))

            self._inst_cyclic_tm = socket.socket(socket.AF_INET,
                                                 socket.SOCK_STREAM)
            self._inst_cyclic_tm.connect(
                (self._instrument.address, self._instrument.tm_port))

            self._inst_cyclic_tm_thread = threading.Thread(
                target=ThreadedCyclicTmHandler,
                args=(self._inst_cyclic_tm, self._instrument.terminator_read,
                      self._shared_memory, self._context.rx, self._log_info,
                      self._cyclic_tm_mapping, self._name))

            self._inst_cyclic_tm_thread.start()

        except ConnectionRefusedError:
            result.type = ParameterType.error
            result.value = 'Instrument is unreachable'
            self._log_error(result.value)

    def initialize(self) -> None:
        super().initialize()

        for key, parameter_info in self._configuration['parameters'].items():
            cmd_list = (parameter_info.get('get')
                        or {}).get('instrument_command', {})
            if len(cmd_list) > 0:
                cmd_type = list(cmd_list[0].keys())[0]
                cmd = list(cmd_list[0].values())[0]

                if cmd_type == 'cyclic':
                    self._cyclic_tm_mapping[key] = cmd

    def _instrument_disconnect(self,
                               result: Optional[ServiceResponse] = None
                               ) -> None:
        if self._inst is not None:
            self._inst.close()
            self._inst = None

        if self._inst_cyclic_tm is not None:
            self._inst_cyclic_tm.close()
            self._inst_cyclic_tm = None
