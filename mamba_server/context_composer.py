import os
import json
import time

from mamba_server.components.gui.main_window.main_tk import MainWindow

from mamba_server.context import Context
from mamba_server.components.gui.plugins.interface import GuiPluginInterface
from mamba_server.utils.misc import get_classes_from_module
from mamba_server.components.gui.load_screen.splash_tk import LoadScreen


def execute():
    context = Context()

    with open(os.path.join('launch', 'default.launch.json')) as f:
        info = json.load(f)

        if 'load_screen' in info:
            load_screen = LoadScreen(context)
            load_screen.show()

            start_time = time.time()

        if info['main']['component'] == "window":
            context.set('main_window', MainWindow(context))
        else:
            print(info)

        all_gui_plugins = get_classes_from_module(
            'mamba_server.components.gui.plugins', GuiPluginInterface)

        dict_gui_plugins = {}

        for used_gui_plugin in info['gui_plugins']:
            if used_gui_plugin in all_gui_plugins:
                dict_gui_plugins[used_gui_plugin] = all_gui_plugins[
                    used_gui_plugin](context)
            else:
                print("Que ases cabesa! {}".format(used_gui_plugin))

        context.set('gui_plugins', dict_gui_plugins)

        if 'load_screen' in info:
            min_splash_time = info['load_screen']["min_seconds"] * 1000

            load_screen.after(min_splash_time - (time.time() - start_time),
                              load_screen.close)

            context.get('main_window').after(
                min_splash_time - (time.time() - start_time),
                context.get('main_window').show)

    # Start the event loop.
    context.get('main_window').start_event_loop()


if __name__ == '__main__':
    execute()
