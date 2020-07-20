#############################################################################
##
## Copyright (C) 2020 The Mamba Company.
## Contact: themambacompany@gmail.com
##
## This file is part of Mamba Server.
##
## $MAMBA_BEGIN_LICENSE:LGPL$
## Commercial License Usage
## Licensees holding valid commercial Mamba licenses may use this file in
## accordance with the commercial license agreement provided with the
## Software or, alternatively, in accordance with the terms contained in
## a written agreement between you and The Mamba Company. For licensing terms
## and conditions see LICENSE. For further information contact us at
## themambacompany@gmail.com.
##
## GNU Lesser General Public License Usage
## Alternatively, this file may be used under the terms of the GNU Lesser
## General Public License version 3 as published by the Free Software
## Foundation and appearing in the file LICENSE.LGPL3 included in the
## packaging of this file. Please review the following information to
## ensure the GNU Lesser General Public License version 3 requirements
## will be met: https://www.gnu.org/licenses/lgpl-3.0.html.
##
## GNU General Public License Usage
## Alternatively, this file may be used under the terms of the GNU
## General Public License version 2.0 or (at your option) the GNU General
## Public license version 3 or any later version approved by the KDE Free
## Qt Foundation. The licenses are as published by the Free Software
## Foundation and appearing in the file LICENSE.GPL2 and LICENSE.GPL3
## included in the packaging of this file. Please review the following
## information to ensure the GNU General Public License requirements will
## be met: https://www.gnu.org/licenses/gpl-2.0.html and
## https://www.gnu.org/licenses/gpl-3.0.html.
##
## $MAMBA_END_LICENSE$
##
#############################################################################

""" TCP Instrument driver controller base """

from typing import Optional, Any
import socket

from mamba.core.context import Context
from mamba.core.exceptions import ComponentConfigException
from mamba.core.component_base import InstrumentDriver
from mamba.core.msg import ServiceRequest, \
    ServiceResponse, ParameterType


def tcp_raw_write(sock: socket.socket, message: str, eom_w: str,
                  encoding: str) -> None:
    sock.sendall(bytes(f'{message}{eom_w}', encoding))


def tcp_raw_query(sock: socket.socket, message: str, eom_w: str, eom_r: str,
                  encoding: str) -> str:
    sock.sendall(bytes(f'{message}{eom_w}', encoding))
    return str(sock.recv(1024), encoding)[:-len(eom_r)]


def tcp_raw_read(sock: socket.socket, eom_r: str, encoding: str) -> str:
    return str(sock.recv(1024), encoding)[:-len(eom_r)]


class TcpInstrumentDriver(InstrumentDriver):
    """ VISA Instrument driver controller class """
    def __init__(self,
                 config_folder: str,
                 context: Context,
                 local_config: Optional[dict] = None) -> None:
        super().__init__(config_folder, context, local_config)

        if (self._instrument.port is None and self._instrument.tc_port is None
                and self._instrument.tm_port is None):
            raise ComponentConfigException(
                'Missing port in Instrument Configuration')

        self._inst: Optional[socket.socket] = None

    def _instrument_connect(self,
                            result: Optional[ServiceResponse] = None) -> None:
        try:
            self._inst = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self._inst.connect(
                (self._instrument.address, self._instrument.port))

            if result is not None and result.id in self._shared_memory_setter:
                self._shared_memory[self._shared_memory_setter[result.id]] = 1

            if self._instrument.reply_timeout is not None:
                self._inst.settimeout(float(self._instrument.reply_timeout))

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

            if result is not None and result.id in self._shared_memory_setter:
                self._shared_memory[self._shared_memory_setter[result.id]] = 0
            self._log_dev("Closed connection to Instrument")

    def _process_inst_command(self, cmd_type: str, cmd: Any,
                              service_request: ServiceRequest,
                              result: ServiceResponse) -> None:
        connection_attempts = 0
        success = False

        while connection_attempts < self._instrument.max_connection_attempts:
            connection_attempts += 1

            if self._inst is not None:
                try:
                    if cmd_type == 'query':
                        value = tcp_raw_query(
                            self._inst, cmd.format(*service_request.args),
                            self._instrument.terminator_write,
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
