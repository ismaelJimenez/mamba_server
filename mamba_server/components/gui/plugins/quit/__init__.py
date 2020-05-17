""" Plugin to close Mamba Application """

import os

from mamba_server.components.gui.plugins.interface import GuiPluginInterface


class GuiPlugin(GuiPluginInterface):
    """ Plugin to close Main Window """
    def __init__(self, context):
        super(GuiPlugin, self).__init__(os.path.dirname(__file__), context)

        # Initialize observables
        self._register_observables()

    def _register_observables(self):
        self._context.rx.subscribe(
            subject_name='run_plugin',
            on_next=self.run,
            op_filter=lambda rx_dict: rx_dict['menu'] == self._configuration[
                'menu'] and rx_dict['action'] == self._configuration['name'])

    def run(self, rx_on_next_value=None):
        """ Entry point for running quit plugin """
        self._context.rx.on_next('quit')
