import os
import json
import time

from PySide2.QtCore import QTimer, Qt
from PySide2.QtWidgets import QApplication

from mamba_server.components.gui.main.window.window import MainWindow

from mamba_server.context import Context
from mamba_server.components.gui.plugins.interface import GuiPluginInterface
from mamba_server.utils.misc import get_classes_from_module
from mamba_server.components.gui.load_screen.mamba_splash import LoadScreen


def execute():
    app = QApplication([])
    context = Context()

    with open(os.path.join('launch', 'default.launch.json')) as f:
        info = json.load(f)

        if 'load_screen' in info:
            load_screen = LoadScreen()
            load_screen.show()

            start_time = time.time()

            load_screen.showMessage("Loading Main Window ...")

        if info['main']['component'] == "window":
            context.set('main_window', MainWindow(context))
        else:
            print(info)

        if 'load_screen' in info:
            load_screen.showMessage("Loading User Interface Plugins ...",
                                    alignment=Qt.AlignBottom,
                                    color=Qt.white)

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
            load_screen.showMessage("Starting...",
                                    alignment=Qt.AlignBottom,
                                    color=Qt.white)
            min_splash_time = info['load_screen']["min_seconds"] * 1000
            QTimer.singleShot(min_splash_time - (time.time() - start_time),
                              load_screen.close)
            QTimer.singleShot(min_splash_time - (time.time() - start_time),
                              context.get('main_window').show)

    # Start the event loop.
    app.exec_()


if __name__ == '__main__':
    execute()
