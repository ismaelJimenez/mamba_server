import os

from mamba_server.components.gui.plugins import GuiPluginInterface


class Quit(GuiPluginInterface):
    def __init__(self, context=None):
        super(Quit, self).__init__(os.path.dirname(__file__), context)

    def show(self):
        self.context.get('main_window').close()
