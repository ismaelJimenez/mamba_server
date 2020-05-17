""" Custom Plugin """

import os

from mamba_server.components.interface import ComponentInterface


class GuiPlugin(ComponentInterface):
    """ Custom Plugin """
    def __init__(self, context=None):
        super(GuiPlugin, self).__init__(os.path.dirname(__file__), context)

    def run(self):
        """
        Entry point for running custom plugin
        """
        raise NotImplementedError
