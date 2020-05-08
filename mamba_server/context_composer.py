import os
import json

from PySide2.QtWidgets import QApplication

from mamba_server.components.gui.main.window.window import MainWindow
from mamba_server.components.gui.plugins.about.about import About

from mamba_server.context import Context



def execute():
    app = QApplication([])

    context = Context()

    with open(os.path.join('launch', 'default.launch.json')) as f:
        info = json.load(f)

        if info['main']['component'] == "window":
            #window = MainWindow(context)
            #about.initialize(context)

            context.set('window', MainWindow(context))
            about = About(context)
        else:
            print(info)

        print(context.get('window'))

    # Start the event loop.
    app.exec_()


if __name__ == '__main__':
    execute()