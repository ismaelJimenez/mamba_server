""" Plugin to show About message implemented in Qt5 """

import os

from mamba.core.component_base import GuiPlugin
from mamba.component.gui.msg.run_action \
    import RunAction


class Plugin(GuiPlugin):
    """ Plugin to show About message implemented in Qt5 """
    def __init__(self, context, local_config=None):
        super(Plugin, self).__init__(os.path.dirname(__file__), context,
                                     local_config)

        # TODO: Define custom variables

    def initialize(self):
        super(Plugin, self).initialize()

        # TODO: Initialize custom variables

    def run(self, rx_value):
        """ Entry point for running the plugin

            Args:
                rx_value (RunAction): The value published by the subject.
        """
        raise NotImplementedError
