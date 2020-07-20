############################################################################
#
# Copyright (c) Mamba Developers. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#
############################################################################
""" Single Port TCP controller base """

from typing import Optional
import socket
import os

from mamba.core.component_base import TcpInstrumentDriver
from mamba.core.component_base.tcp_instrument_driver import \
    tcp_raw_write, tcp_raw_read
from mamba.core.context import Context
from mamba.core.msg import ServiceResponse, ParameterType, ServiceRequest


class TwoPortsTcpController(TcpInstrumentDriver):
    """ Simple TCP controller base class """
    def __init__(self,
                 context: Context,
                 local_config: Optional[dict] = None) -> None:
        super().__init__(os.path.dirname(__file__), context, local_config)

        # self._inst will be kept for telecommands
        self._inst: Optional[socket.socket] = None
        self._inst_tm: Optional[socket.socket] = None

    def _instrument_connect(self,
                            result: Optional[ServiceResponse] = None) -> None:
        try:
            self._inst = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

            if self._inst is None:
                raise ConnectionRefusedError

            self._inst.connect(
                (self._instrument.address, self._instrument.tc_port))

            self._inst_tm = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

            if self._inst_tm is None:
                raise ConnectionRefusedError

            self._inst_tm.connect(
                (self._instrument.address, self._instrument.tm_port))

            if result is not None and result.id in self._shared_memory_setter:
                self._shared_memory[self._shared_memory_setter[result.id]] = 1

            self._log_dev("Established connection to Instrument")

        except (ConnectionRefusedError, OSError):
            error = 'Instrument is unreachable'
            if result is not None:
                result.type = ParameterType.error
                result.value = error
            self._log_error(error)

    def _instrument_disconnect(self,
                               result: Optional[ServiceResponse] = None
                               ) -> None:
        if self._inst is not None:
            self._inst.close()
            self._inst = None

        if self._inst_tm is not None:
            self._inst_tm.close()
            self._inst_tm = None

        if result is not None and result.id in self._shared_memory_setter:
            self._shared_memory[self._shared_memory_setter[result.id]] = 0

        self._log_dev("Closed connection to Instrument")

    def _process_inst_command(self, cmd_type: str, cmd: str,
                              service_request: ServiceRequest,
                              result: ServiceResponse) -> None:
        connection_attempts = 0
        success = False

        while connection_attempts < self._instrument.max_connection_attempts:
            connection_attempts += 1

            if self._inst is not None and self._inst_tm is not None:
                try:
                    if cmd_type == 'query':
                        tcp_raw_write(self._inst,
                                      cmd.format(*service_request.args),
                                      self._instrument.terminator_write,
                                      self._instrument.encoding)

                        value = tcp_raw_read(self._inst_tm,
                                             self._instrument.terminator_read,
                                             self._instrument.encoding)

                        if service_request.type == ParameterType.set:
                            self._shared_memory[self._shared_memory_setter[
                                service_request.id]] = value
                        else:
                            result.value = value

                    elif cmd_type == 'write':
                        tcp_raw_write(self._inst,
                                      cmd.format(*service_request.args),
                                      self._instrument.terminator_write,
                                      self._instrument.encoding)

                except (ConnectionRefusedError, OSError):
                    self._instrument_disconnect()
                    self._instrument_connect()
                    continue
            else:
                result.type = ParameterType.error
                result.value = 'Not possible to perform command before ' \
                               'connection is established'
                self._log_error(result.value)

            success = True
            break

        if not success:
            result.type = ParameterType.error
            result.value = 'Not possible to communicate to the' \
                           ' instrument'
            self._log_error(result.value)
