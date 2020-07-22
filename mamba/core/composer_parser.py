############################################################################
#
# Copyright (c) Mamba Developers. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#
############################################################################
""" Compose Mamba App from launch file """

import yaml

from typing import Optional

from mamba.core.context import Context
from mamba.core.utils import get_components
from mamba.core.component_base import Component

from mamba.core.msg.app_status import AppStatus

context = Context()


def compose_parser(compose_file: str,
                   mamba_dir: str,
                   project_dir: Optional[str] = None,
                   local_context: Context = context) -> int:
    """ Compose Mamba App from launch file """
    component_folders = ['mamba.component']

    if project_dir is not None:
        component_folders.insert(0, 'components')

    with open(compose_file) as file:
        compose_config = yaml.load(file, Loader=yaml.FullLoader)

        local_context.set('mamba_dir', mamba_dir)
        local_context.set('project_dir', project_dir)

        if isinstance(compose_config,
                      dict) and compose_config.get('services') is not None:
            services = get_components(compose_config['services'],
                                      component_folders, Component,
                                      local_context)

            for key, service in services.items():
                if isinstance(service, Component):
                    service.initialize()

            return 0
        else:
            return 1


def start_mamba_app(local_context: Context = context) -> None:
    # Start Mamba App
    local_context.rx['app_status'].on_next(AppStatus.Running)
