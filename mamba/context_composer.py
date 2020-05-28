""" Compose context from launch file """
import sys
import yaml

from mamba.context import Context
from mamba.utils.misc import get_components
from mamba.components import ComponentBase

from mamba.components.observable_types.app_status import AppStatus

DEFAULT_RX = 'mamba'


def execute(launch_file, mamba_dir, project_dir):
    """ Compose context from launch file """
    component_folders = ['mamba.components']

    if project_dir is not None:
        component_folders.append('components')

    with open(launch_file) as file:
        launch_config = yaml.load(file, Loader=yaml.FullLoader)

        context = Context()
        context.set('mamba_dir', mamba_dir)
        context.set('project_dir', project_dir)

        # Start Main Window Component, if any
        if 'services' in launch_config:
            services = get_components(launch_config['services'],
                                      component_folders, ComponentBase,
                                      context)

            for key, service in services.items():
                service.initialize()

        # Start Main Component
        context.rx['app_status'].on_next(AppStatus.Running)

        sys.exit(0)
