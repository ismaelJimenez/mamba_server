""" Custom Plugin """

import os

from mamba_server.components.gui.plugins.interface import GuiPluginInterface


class GuiPlugin(GuiPluginInterface):
    """ Custom Plugin """
    def __init__(self, context=None):
        super(GuiPlugin, self).__init__(os.path.dirname(__file__), context)

    def execute(self):
        """
        Entry point for running custom plugin
        """
        raise NotImplementedError