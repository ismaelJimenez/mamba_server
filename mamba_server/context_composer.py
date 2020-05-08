import os
import json

from PySide2.QtWidgets import QApplication, QMainWindow

from mamba_server.components.gui.main_window import gui
from mamba_server.components.gui.about import about

from mamba_server.context import Context



def execute():
    app = QApplication([])
    app_window = QMainWindow()

    context = Context()
    context.set('app', app_window)

    with open(os.path.join('launch', 'default.launch.json')) as f:
        info = json.load(f)
        print(info['main']['component'])

        if info['main']['component'] == "main_window":
            gui.execute(context)
            about.initialize(context)
        else:
            print(info)

    # Start the event loop.
    app.exec_()


if __name__ == '__main__':
    execute()