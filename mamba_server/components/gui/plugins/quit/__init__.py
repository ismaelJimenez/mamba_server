""" Plugin to close Mamba Application """

import os

from mamba_server.components.interface import ComponentInterface
from mamba_server.exceptions import ComponentConfigException

from mamba_server.components.observer_types.empty import Empty
from mamba_server.components.gui.main_window.observer_types.register_action\
    import RegisterAction


class GuiPlugin(ComponentInterface):
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
            'register_action',
            RegisterAction(menu_title=self._configuration['menu'],
                           action_name=self._configuration['name'],
                           shortcut=self._configuration['shortcut']
                           if 'shortcut' in self._configuration else None,
                           status_tip=self._configuration['status_tip']
                           if 'status_tip' in self._configuration else None))

    def run(self, rx_value):
        """ Entry point for running the plugin

            Args:
                rx_value (Empty): The value published by the subject.
        """
        self._context.rx.on_next('quit', Empty())
