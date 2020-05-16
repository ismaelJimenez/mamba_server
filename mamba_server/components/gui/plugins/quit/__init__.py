""" Plugin to close Main Window """

import os

from mamba_server.components.gui.plugins.interface import GuiPluginInterface


class GuiPlugin(GuiPluginInterface):
    """ Plugin to close Main Window """
    def __init__(self, context=None):
        super(GuiPlugin, self).__init__(os.path.dirname(__file__), context)

    def execute(self):
        """
        Entry point for running gui plugin
        """
        if self._context is not None:
            self._context.rx.on_next('quit')
