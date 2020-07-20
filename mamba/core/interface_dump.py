################################################################################################
##
##  Copyright (c) Mamba Developers. All rights reserved.
##  Licensed under the MIT License. See License.txt in the project root for license information.
##
################################################################################################

""" Compose Mamba App from launch file """

import yaml
import time
import json

from typing import Optional, List, Dict

from mamba.core.context import Context
from mamba.core.utils import get_components
from mamba.core.component_base import Component
from mamba.core.msg import ParameterInfo, ParameterType


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
                   project_dir: Optional[str] = None) -> int:
    """ Compose Mamba App from launch file """

    io_services: Dict[str, List[ParameterInfo]] = {}

    component_folders = ['mamba.component', 'mamba.mock']

    if project_dir is not None:
        component_folders.append('component')

    with open(compose_file) as file:
        compose_config = yaml.load(file, Loader=yaml.FullLoader)

        context = Context()
        context.set('mamba_dir', mamba_dir)
        context.set('project_dir', project_dir)

        context.rx['io_service_signature'].subscribe(
            on_next=lambda parameters_info: io_service_signature(
                parameters_info, io_services))

        if isinstance(compose_config,
                      dict) and compose_config.get('services') is not None:
            services = get_components(compose_config['services'],
                                      component_folders, Component, context)

            for key, service in services.items():
                if isinstance(service, Component):
                    service.initialize()

            time.sleep(1)

            with open(output_file, 'w') as outfile:
                json.dump(io_services, outfile)

            return 0
        else:
            return 1
