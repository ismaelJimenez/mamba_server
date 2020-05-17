""" Compose context from launch file """
import time
import yaml

from mamba_server.context_mamba import Context
from mamba_server.utils.misc import get_component, get_components
from mamba_server.components.gui.load_screen.interface import \
    LoadScreenBase
from mamba_server.components.component_base import ComponentBase

from mamba_server.components.observer_types.app_status import AppStatus


def execute(launch_file, mamba_dir, project_dir):
    """ Compose context from launch file """
    context = Context()
    context.set('mamba_dir', mamba_dir)
    context.set('project_dir', project_dir)

    component_folders = ['mamba_server.components']

    if project_dir is not None:
        component_folders.append('components')

    with open(launch_file) as file:
        launch_config = yaml.load(file, Loader=yaml.FullLoader)

        # Start Load Screen Component, if any
        if 'load_screen' in launch_config:
            load_screen = get_component(
                launch_config['load_screen']['component'], component_folders,
                LoadScreenBase, context)
            load_screen.show()

            min_load_screen_time = None

            if 'min_seconds' in launch_config['load_screen']:
                min_load_screen_time = launch_config['load_screen'][
                    'min_seconds'] * 1000
                start_time = time.time()

        # Start Main Window Component, if any
        if 'services' in launch_config:
            services = get_components(launch_config['services'],
                                      component_folders, ComponentBase,
                                      context)

            for key, service in services.items():
                service.initialize()

        if ('load_screen' in launch_config) and (min_load_screen_time
                                                 is not None):
            load_screen.after(
                min_load_screen_time - (time.time() - start_time),
                load_screen.close)
            load_screen.start_event_loop()

        # Start Main Component, if any
        context.rx.on_next('app_status', AppStatus.Running)
