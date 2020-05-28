""" Plugin to show About message implemented in Qt5 """

import os

from mamba.components.plugins import PluginBase
from mamba.components.main.observable_types.run_action \
    import RunAction


class Plugin(PluginBase):
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
