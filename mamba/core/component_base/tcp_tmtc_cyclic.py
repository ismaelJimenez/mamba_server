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

""" Single Port TCP controller base """

from typing import Optional, Dict
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


class TcpTmTcCyclic(TcpInstrumentDriver):
    """ Simple TCP controller base class """
    def __init__(self,
                 config_folder: str,
                 context: Context,
                 local_config: Optional[dict] = None,
                 cyclic_tm_class=ThreadedCyclicTmHandler) -> None:
        super().__init__(config_folder, context, local_config)

        # self._inst will be kept for telecommands

        self._inst: Optional[socket.socket] = None

        self._inst_cyclic_tm: Optional[socket.socket] = None
        self._inst_cyclic_tm_thread: Optional[threading.Thread] = None

        self._cyclic_tm_mapping: Dict[str, str] = {}
        self._cyclic_tm_class = cyclic_tm_class

    def _instrument_connect(self,
                            result: Optional[ServiceResponse] = None) -> None:
        try:
            self._inst = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

            if self._inst is None:
                raise ConnectionRefusedError

            self._inst.connect(
                (self._instrument.address, self._instrument.tc_port))

            self._inst_cyclic_tm = socket.socket(socket.AF_INET,
                                                 socket.SOCK_STREAM)

            if self._inst_cyclic_tm is None:
                raise ConnectionRefusedError

            self._inst_cyclic_tm.connect(
                (self._instrument.address, self._instrument.tm_port))

            self._inst_cyclic_tm_thread = threading.Thread(
                target=self._cyclic_tm_class,
                args=(self._inst_cyclic_tm, self._instrument.terminator_read,
                      self._shared_memory, self._context.rx, self._log_info,
                      self._cyclic_tm_mapping, self._name))

            self._inst_cyclic_tm_thread.start()

            if result is not None and result.id in self._shared_memory_setter:
                self._shared_memory[self._shared_memory_setter[result.id]] = 1

            self._log_dev("Established connection to Instrument")

        except ConnectionRefusedError:
            error = 'Instrument is unreachable'
            if result is not None:
                result.type = ParameterType.error
                result.value = error
            self._log_error(error)

    def initialize(self) -> None:
        super().initialize()

        for key, parameter_info in self._configuration['parameters'].items():
            tm_format = parameter_info.get('cyclic_tm_client',
                                           {}).get('format', {})
            if len(tm_format) > 0:
                self._cyclic_tm_mapping[key] = tm_format

    def _instrument_disconnect(self,
                               result: Optional[ServiceResponse] = None
                               ) -> None:
        if self._inst is not None:
            self._inst.close()
            self._inst = None

        if self._inst_cyclic_tm is not None:
            self._inst_cyclic_tm.close()
            self._inst_cyclic_tm = None

        if result is not None and result.id in self._shared_memory_setter:
            self._shared_memory[self._shared_memory_setter[result.id]] = 0

        self._log_dev("Closed connection to Instrument")
