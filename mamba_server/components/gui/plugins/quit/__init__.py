import os

from mamba_server.components.gui.plugins import GuiPluginsBase


class Quit(GuiPluginsBase):
    def __init__(self, context=None):
        super(Quit, self).__init__(os.path.dirname(__file__), context)

    def show(self):
        self.context.get('main_window').close()
