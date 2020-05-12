import os
import json
import time

from mamba_server.context import Context
from mamba_server.exceptions import ComponentConfigException
from mamba_server.components.gui.load_screen.interface import LoadScreenInterface
from mamba_server.components.gui.main_window.interface import MainWindowInterface
from mamba_server.components.gui.plugins.interface import GuiPluginInterface
from mamba_server.utils.misc import get_classes_from_module


def get_component(component_name, component_list):
    if component_name in component_list:
        return component_list[component_name]

    raise ComponentConfigException("Component '{}' is not a valid component identifier".format(component_name))

def get_component(used_component, module, component_type, context):
    all_components_by_type = get_classes_from_module(
        module, component_type)

    if used_component in all_components_by_type:
        return all_components_by_type[used_component](context)

    raise ComponentConfigException("Component '{}' is not a valid component identifier".format(used_component))



def get_components(used_components, module, component_type, context):
    all_components_by_type = get_classes_from_module(
        module, component_type)

    dict_used_components = {}

    for used_component in used_components:
        if used_component in all_components_by_type:
            dict_used_components[used_component] = all_components_by_type[
                used_component](context)
        else:
            raise ComponentConfigException("Component '{}' is not a valid component identifier".format(used_component))

    return dict_used_components


def execute(launch_file):
    context = Context()

    with open(launch_file) as f:
        launch_config = json.load(f)

        # Start Load Screen Component, if any
        if 'load_screen' in launch_config:
            load_screen = get_component(launch_config['load_screen']['component'],
                                         'mamba_server.components.gui.load_screen',
                                         LoadScreenInterface, context)
            load_screen.show()

            min_load_screen_time = None

            if ('app' in launch_config) and ('min_load_screen_secs' in launch_config['app']):
                min_load_screen_time = launch_config['app']['min_load_screen_secs'] * 1000
                start_time = time.time()

        # Start Main Window Component, if any
        if 'main_window' in launch_config:
            main_window = get_component(launch_config['main_window']['component'],
                                         'mamba_server.components.gui.main_window',
                                         MainWindowInterface, context)

            context.set('main_window', main_window)

        # Instantiate GUI Plugins, if any
        if 'gui_plugins' in launch_config:
            gui_plugins = get_components(launch_config['gui_plugins'],
                                        'mamba_server.components.gui.plugins',
                                        GuiPluginInterface, context)

            context.set('gui_plugins', gui_plugins)

        if ('load_screen' in launch_config) and (min_load_screen_time is not None):
            load_screen.after(min_load_screen_time - (time.time() - start_time),
                              load_screen.close)
            load_screen.start_event_loop()

        # Start the event loop.
        context.get('main_window').show()
        context.get('main_window').start_event_loop()


if __name__ == '__main__':
    execute(os.path.join('launch', 'default_qt.launch.json'))
