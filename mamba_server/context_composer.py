import os
import json

from PySide2.QtWidgets import QApplication, QMainWindow

from mamba_server.components.gui.main_window.main_window import MainWindow
from mamba_server.components.gui.about.about import About

from mamba_server.context import Context



def execute():
    app = QApplication([])

    context = Context()

    with open(os.path.join('launch', 'default.launch.json')) as f:
        info = json.load(f)

        if info['main']['component'] == "main_window":
            #main_window = MainWindow(context)
            #about.initialize(context)

            context.set('main_window', MainWindow(context))
            about = About(context)
        else:
            print(info)

        print(context.get('main_window'))

    # Start the event loop.
    app.exec_()


if __name__ == '__main__':
    execute()