""" Custom Plugin """

import os

from mamba_server.components import ComponentBase
from mamba_server.exceptions import ComponentConfigException

from mamba_server.components.main.observable_types.register_action \
    import RegisterAction
from mamba_server.components.main.observable_types.run_action \
    import RunAction


class GuiPlugin(ComponentBase):
    """ Custom Plugin """
    def __init__(self, context=None, local_config=None):
        super(GuiPlugin, self).__init__(os.path.dirname(__file__), context,
                                        local_config)

        # Initialize observers
        self._register_observers()

    def _register_observers(self):
        """ Entry point for registering component observers """
        self._context.rx.subscribe(
            subject_name='run_plugin',
            on_next=self.run,
            op_filter=lambda rx: isinstance(
                rx, RunAction) and rx.menu_title == self._configuration[
                    'menu'] and rx.action_name == self._configuration['name'])

        # TODO: Other required observers

    def initialize(self):
        """ Entry point for component initialization """
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

        # TODO: Other required initializations

    def run(self, rx_value):
        """ Entry point for running the plugin

            Args:
                rx_value (RunAction): The value published by the subject.
        """
        raise NotImplementedError
