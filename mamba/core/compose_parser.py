""" Compose Mamba App from launch file """
import sys
import yaml

from typing import Optional

from mamba.core.context import Context
from mamba.core.utils import get_components
from mamba.components import ComponentBase

from mamba.core.msg.app_status import AppStatus


def compose_parser(compose_file: str,
                   mamba_dir: str,
                   project_dir: Optional[str] = None) -> None:
    """ Compose Mamba App from launch file """

    component_folders = ['mamba.components', 'mamba.mock']

    if project_dir is not None:
        component_folders.append('components')

    with open(compose_file) as file:
        compose_config = yaml.load(file, Loader=yaml.FullLoader)

        context = Context()
        context.set('mamba_dir', mamba_dir)
        context.set('project_dir', project_dir)

        if isinstance(compose_config, dict) and compose_config.get('services') is not None:
            services = get_components(compose_config['services'],
                                      component_folders, ComponentBase,
                                      context)

            for key, service in services.items():
                service.initialize()

            # Start Mamba App
            context.rx['app_status'].on_next(AppStatus.Running)

            return 0
        else:
            return 1
