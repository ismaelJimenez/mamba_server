############################################################################
#
# Copyright (c) Mamba Developers. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#
############################################################################
""" Compose Mamba IF from launch file """

import time
import json

from typing import Optional, List, Dict

from mamba.core.context import Context
from mamba.core.msg import ParameterInfo
from mamba.core.composer_parser import compose_parser

context = Context()


def io_service_signature(parameters_info: List[ParameterInfo],
                         io_services) -> None:
    """ Entry point for processing the service signatures.

        Args:
            signatures: The io service signatures dictionary.
    """
    io_services[parameters_info[0].provider] = [(param.id, int(param.type),
                                                 param.signature)
                                                for param in parameters_info]


def interface_dump(compose_file: str,
                   mamba_dir: str,
                   output_file: str,
                   project_dir: Optional[str] = None,
                   local_context: Context = context) -> int:
    """ Compose Mamba IF from launch file """

    io_services: Dict[str, List[ParameterInfo]] = {}

    local_context.rx['io_service_signature'].subscribe(
        on_next=lambda parameters_info: io_service_signature(
            parameters_info, io_services))

    result = compose_parser(compose_file, mamba_dir, project_dir,
                            local_context)

    if result == 0:
        time.sleep(1)

        with open(output_file, 'w') as outfile:
            json.dump(io_services, outfile)
    else:
        return 1
