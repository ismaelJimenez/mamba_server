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

""" Socket to TMTC translator """

import os
import time

from typing import Optional

from mamba.core.context import Context
from mamba.core.msg import Raw, ServiceRequest, ServiceResponse, ParameterType
from mamba.core.component_base import Component


class HvsProtocolTranslator(Component):
    """ Socket to TMTC translator class """
    def __init__(self,
                 context: Context,
                 local_config: Optional[dict] = None) -> None:
        super().__init__(os.path.dirname(__file__), context, local_config)

        # Initialize observers
        self._register_observers()

    def _register_observers(self) -> None:
        # Register to the raw_tc provided by the socket server service
        self._context.rx['raw_tc'].subscribe(on_next=self._received_raw_tc)

        # Register to the telemetries provided by the central controller
        self._context.rx['tm'].subscribe(on_next=self._received_tm)

    def _received_raw_tc(self, raw_tc: Raw) -> None:
        """ Entry point for processing a new msg telecommand coming from the
            socket server.

            Args:
                raw_tc (Raw): The msg telecommand coming from
                                         the socket.
        """
        self._log_dev('Received Raw TC')
        for telecommand in raw_tc.msg.replace('"', '').split('\r\n')[:-1]:
            tc_list = telecommand.rstrip().split(' ')
            self._log_dev('Published TC')
            self._context.rx['tc'].on_next(
                ServiceRequest(id=tc_list[1],
                               args=tc_list[2:],
                               type=ParameterType[tc_list[0].replace(
                                   'tc', 'set').replace('tm', 'get')]))

    def _received_tm(self, telemetry: ServiceResponse) -> None:
        """ Entry point for processing a new telemetry generated by the
            central controller.

            Args:
                tm: The telemetry coming from the central
                    controller.
        """
        self._log_dev('Received TM')
        if telemetry.type == ParameterType.set:
            raw_tm = f"> OK {telemetry.id}\r\n"
        elif telemetry.type == ParameterType.get:
            raw_tm = f"> OK {telemetry.id};{time.time()};{telemetry.value};" \
                     f"{telemetry.value};0;1\r\n"
        elif telemetry.type == ParameterType.set_meta:
            raw_tm = f"> OK {telemetry.id};" \
                     f"{len(telemetry.value['signature'][0])};" \
                     f"{telemetry.value['description']}\r\n"
        elif telemetry.type == ParameterType.get_meta:
            raw_tm = f"> OK {telemetry.id};" \
                     f"{telemetry.value['signature'][1]};" \
                     f"{telemetry.value['signature'][1]};" \
                     f"{telemetry.value['description']};7;4\r\n"
        elif telemetry.type == ParameterType.error:
            raw_tm = f"> ERROR {telemetry.id} {telemetry.value}\r\n"
        else:  # helo and Unrecognized type
            raw_tm = f"> OK helo {telemetry.id}\r\n"

        self._log_dev('Published Raw TM')
        self._context.rx['raw_tm'].on_next(Raw(raw_tm))
