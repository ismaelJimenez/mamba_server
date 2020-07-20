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

import os

from typing import List, Dict, Optional

from mamba.core.context import Context
from mamba.core.msg import ServiceResponse,\
    ServiceRequest, ParameterInfo, ParameterType
from mamba.core.component_base import Component
from mamba.core.exceptions import ComponentConfigException


class MambaProtocolController(Component):
    def __init__(self,
                 context: Context,
                 local_config: Optional[dict] = None) -> None:
        super().__init__(os.path.dirname(__file__), context, local_config)

        # Initialize observersParameterType
        self._register_observers()

        # Define custom variables
        self._provider_params: Dict[tuple, ParameterInfo] = {}
        self._io_result_subs = None

    def _register_observers(self) -> None:
        """ Entry point for registering component observers """

        # Register to the tc provided by the socket protocol translator service
        self._context.rx['tc'].subscribe(on_next=self._received_tc)

        # Register to the topic provided by the io_controller services
        self._context.rx['io_service_signature'].subscribe(
            on_next=self._io_service_signature)

    def _generate_tm(self, telecommand: ServiceRequest,
                     param_type: ParameterType) -> None:
        """ Entry point for generating response telemetry

            Args:
                telecommand: The service request received.
        """

        result = ServiceResponse(id=telecommand.id, type=telecommand.type)

        if param_type in [ParameterType.get, ParameterType.set]:
            io_service = self._provider_params[(telecommand.id, param_type)]

            result.provider = io_service.provider

            result.value = {
                'signature': io_service.signature,
                'description': io_service.description
            }

        self._context.rx['tm'].on_next(result)

    def _generate_error_tm(self, telecommand: ServiceRequest,
                           message: str) -> None:
        """ Entry point for generating error response telemetry

            Args:
                telecommand: The service request received.
                message: The error feedback message.
        """

        self._context.rx['tm'].on_next(
            ServiceResponse(id=telecommand.id,
                            type=ParameterType.error,
                            value=message))

    def _generate_io_service_request(self,
                                     telecommand: ServiceRequest) -> None:
        """ Entry point for generating a IO Service request to fulfill
            a request

            Args:
                telecommand: The service request received.
        """

        self._io_result_subs = self._context.rx['io_result'].subscribe(
            on_next=self._process_io_result)

        self._context.rx['io_service_request'].on_next(
            ServiceRequest(
                provider=self._provider_params[(telecommand.id,
                                                telecommand.type)].provider,
                id=self._provider_params[(telecommand.id,
                                          telecommand.type)].id,
                type=telecommand.type,
                args=telecommand.args))

    def _received_tc(self, telecommand: ServiceRequest) -> None:
        """ Entry point for processing a new telecommand coming from the
            socket translator.

            Args:
                telecommand: The telecommand coming from the socket translator.
        """
        if telecommand.provider is not None:
            telecommand.id = f'{telecommand.provider}_{telecommand.id}'

        self._log_dev(f'Received TC: {telecommand.id}')

        if telecommand.type == ParameterType.get_meta:
            param_type = ParameterType.get
        elif telecommand.type == ParameterType.set_meta:
            param_type = ParameterType.set
        else:
            param_type = telecommand.type

        if ((telecommand.type != ParameterType.helo)
                and (telecommand.id, param_type) not in self._provider_params):
            self._generate_error_tm(telecommand, 'Not recognized command')
            return

        if telecommand.type in [
                ParameterType.helo, ParameterType.set_meta,
                ParameterType.get_meta
        ]:
            self._generate_tm(telecommand, param_type)
        elif telecommand.type in [ParameterType.get, ParameterType.set]:
            self._generate_io_service_request(telecommand)
        else:
            self._generate_error_tm(telecommand, 'Not recognized command type')

    def _process_io_result(self, rx_result: ServiceResponse) -> None:
        """ Entry point for processing the IO Service results.

            Args:
                rx_result: The io service response.
        """
        if self._io_result_subs is not None:
            self._io_result_subs.dispose()

        self._context.rx['tm'].on_next(rx_result)

    def _io_service_signature(self,
                              parameters_info: List[ParameterInfo]) -> None:
        """ Entry point for processing the service signatures.

            Args:
                signatures: The io service signatures dictionary.
        """
        self._log_info(
            f"Received signatures from {parameters_info[0].provider}: "
            f"{[str(parameter_info) for parameter_info in parameters_info]}")

        for parameter_info in parameters_info:
            if not isinstance(parameter_info.signature, list) or len(
                    parameter_info.signature) != 2 or not isinstance(
                        parameter_info.signature[0], list):
                raise ComponentConfigException(
                    f'Signature of service {parameter_info.provider} -> '
                    f'"{parameter_info.id}" is invalid. Format shall'
                    f' be [[arg_1, arg_2, ...], return_type]')

            hvs_parameter_id = f'{parameter_info.provider}_{parameter_info.id}'

            if (hvs_parameter_id,
                    parameter_info.type) in self._provider_params:
                raise ComponentConfigException(
                    f"Received conflicting parameter key: {hvs_parameter_id}")

            self._provider_params[(hvs_parameter_id,
                                   parameter_info.type)] = parameter_info
