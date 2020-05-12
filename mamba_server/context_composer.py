import os
import json
import time

from mamba_server.context import Context
from mamba_server.utils.misc import get_component, get_components
from mamba_server.components.gui.load_screen.interface import LoadScreenInterface
from mamba_server.components.gui.main_window.interface import MainWindowInterface
from mamba_server.components.gui.plugins.interface import GuiPluginInterface


def execute(launch_file):
    context = Context()

    with open(launch_file) as f:
        launch_config = json.load(f)

        # Start Load Screen Component, if any
        if 'load_screen' in launch_config:
            load_screen = get_component(
                launch_config['load_screen']['component'],
                'mamba_server.components.gui.load_screen', LoadScreenInterface,
                context)
            load_screen.show()

            min_load_screen_time = None

            if 'min_seconds' in launch_config['load_screen']:
                min_load_screen_time = launch_config['load_screen'][
                    'min_seconds'] * 1000
                start_time = time.time()

        # Start Main Window Component, if any
        if 'app' in launch_config:
            main_window = get_component(
                launch_config['app']['component'],
                'mamba_server.components.gui.main_window', MainWindowInterface,
                context)

            context.set('main_window', main_window)

        # Instantiate GUI Plugins, if any
        if 'gui_plugins' in launch_config:
            gui_plugins = get_components(
                launch_config['gui_plugins'],
                'mamba_server.components.gui.plugins', GuiPluginInterface,
                context)

            context.set('gui_plugins', gui_plugins)

        if ('load_screen' in launch_config) and (min_load_screen_time
                                                 is not None):
            load_screen.after(
                min_load_screen_time - (time.time() - start_time),
                load_screen.close)
            load_screen.start_event_loop()

        # Start Main Window Component, if any
        if 'app' in launch_config:
            context.get('main_window').show()

            # Start the event loop.
            context.get('main_window').start_event_loop()


if __name__ == '__main__':
    execute(os.path.join('launch', 'default_qt.launch.json'))
