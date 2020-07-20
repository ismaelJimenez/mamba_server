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

from typing import Optional
import os

from stringparser import Parser

from mamba.core.component_base import TcpTmTcCyclic
from mamba.core.context import Context
from mamba.core.msg import ServiceResponse, ParameterType


class ThreadedCyclicTmHandler:
    def __init__(self, sock, eom, shared_memory, rx, log_info,
                 cyclic_tm_mapping, provider):
        half_tm = ''
        while True:
            try:
                # self.request is the TCP socket connected to the client
                data = str(sock.recv(1024), 'utf-8')
                if not data:
                    break

                if half_tm != '':
                    data = half_tm + data

                data_split = data.split(eom)

                if data[-1] != eom:
                    if len(data_split) > 0:
                        half_tm = data_split[-1]
                    else:
                        half_tm = data
                else:
                    half_tm = ''

                data_split = data_split[:-1]

                for raw_cmd in data_split:
                    if '_TC_' in raw_cmd:  # Filter TC echos
                        continue
                    cmd = raw_cmd.split(' ', 1)[1]
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


class H8823TmTcController(TcpTmTcCyclic):
    """ Simple TCP controller base class """
    def __init__(self,
                 context: Context,
                 local_config: Optional[dict] = None) -> None:
        super().__init__(os.path.dirname(__file__), context, local_config,
                         ThreadedCyclicTmHandler)
