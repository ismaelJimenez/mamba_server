import os

from mamba_server.components.gui.plugins import GuiPlugin


class Quit(GuiPlugin):
    def __init__(self, context=None):
        super(Quit, self).__init__(os.path.dirname(__file__), context)

    def show(self):
        self.context.get('main_window').close()
