""" Plugin to close Main Window """

import os

from mamba_server.components.gui.plugins.interface import GuiPluginInterface


class GuiPlugin(GuiPluginInterface):
    """ Plugin to close Main Window """
    def __init__(self, context):
        super(GuiPlugin, self).__init__(os.path.dirname(__file__), context)

        self._context.rx.subscribe(
            subject_name='run_plugin',
            on_next=self.execute,
            op_filter=lambda rx_dict: rx_dict['menu'] == self._configuration[
                'menu'] and rx_dict['action'] == self._configuration['name'])

    def execute(self, rx_on_next_value=None):
        """
        Entry point for running gui plugin
        """
        self._context.rx.on_next('quit')
