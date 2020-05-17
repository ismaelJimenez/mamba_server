""" Plugin to close Mamba Application """

import os

from mamba_server.components.gui.plugins.interface import GuiPluginInterface
from mamba_server.exceptions import ComponentConfigException


class GuiPlugin(GuiPluginInterface):
    """ Plugin to close Main Window """
    def __init__(self, context):
        super(GuiPlugin, self).__init__(os.path.dirname(__file__), context)

        # Initialize observables
        self._register_observables()

        self.initialize()  # TBR

    def _register_observables(self):
        self._context.rx.subscribe(
            subject_name='run_plugin',
            on_next=self.run,
            op_filter=lambda rx_dict: rx_dict['menu'] == self._configuration[
                'menu'] and rx_dict['action'] == self._configuration['name'])

    def initialize(self):
        if not all(key in self._configuration for key in ['menu', 'name']):
            raise ComponentConfigException(
                "Missing required elements in component configuration")

        self._context.rx.on_next(
            'register_menu_action', {
                'menu_title':
                self._configuration['menu'],
                'action_name':
                self._configuration['name'],
                'shortcut': (None, self._configuration['shortcut']
                             )['shortcut' in self._configuration],
                'status_tip': (None, self._configuration['status_tip']
                               )['status_tip' in self._configuration]
            })

    def run(self, rx_value=None):
        """ Entry point for running the plugin

            Args:
                rx_value (None): The value published by the subject.
        """
        self._context.rx.on_next('quit')
