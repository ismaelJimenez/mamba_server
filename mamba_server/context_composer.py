import os
import json

from PySide2.QtWidgets import QApplication

from mamba_server.components.gui.main.window.window import MainWindow
from mamba_server.components.gui.plugins.about import About
from mamba_server.components.gui.plugins.quit import Quit

from mamba_server.utils.context import Context
from mamba_server.components.gui.plugins import GuiPlugin
from mamba_server.utils.misc import get_classes_from_module


def execute():
    app = QApplication([])
    context = Context()

    all_gui_plugins = get_classes_from_module('mamba_server.components.gui.plugins', GuiPlugin)

    with open(os.path.join('launch', 'default.launch.json')) as f:
        info = json.load(f)

        if info['main']['component'] == "window":
            context.set('main_window', MainWindow(context))
        else:
            print(info)

        dict_gui_plugins = {}

        for used_gui_plugin in info['gui_plugins']:
            if used_gui_plugin in all_gui_plugins:
                dict_gui_plugins[used_gui_plugin] = all_gui_plugins[used_gui_plugin](context)
            else:
                print(f"Que ases cabesa! {used_gui_plugin}")

        context.set('gui_plugins', dict_gui_plugins)

    # Start the event loop.
    app.exec_()


if __name__ == '__main__':
    execute()