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
