""" Plugin to close Mamba Application """

import os

from mamba_server.components.plugins import PluginBase

from mamba_server.components.observable_types import Empty
from mamba_server.components.main.observable_types import RunAction


class Plugin(PluginBase):
    """ Plugin to close Main Window """
    def __init__(self, context, local_config=None):
        super(Plugin, self).__init__(os.path.dirname(__file__), context,
                                     local_config)

    def run(self, rx_value: RunAction):
        """ Entry point for running the plugin

            Args:
                rx_value (RunAction): The value published by the subject.
        """
        self._context.rx['quit'].on_next(Empty())
