""" Plugin base """

from rx import operators as op

from mamba_server.components import ComponentBase
from mamba_server.exceptions import ComponentConfigException

from mamba_server.components.main.observable_types import RegisterAction,\
    RunAction


class PluginBase(ComponentBase):
    """ Plugin base class """
    def __init__(self, config_folder, context, local_config=None):
        super(PluginBase, self).__init__(config_folder, context, local_config)

        # Initialize observers
        self._register_observers()

    def _register_observers(self):
        self._context.rx['run_plugin'].pipe(
            op.filter(lambda value: isinstance(value, RunAction) and value.
                      menu_title == self._configuration['menu'] and value.
                      action_name == self._configuration['name'])).subscribe(
                          on_next=self.run)

    def initialize(self):
        if not all(key in self._configuration for key in ['menu', 'name']):
            raise ComponentConfigException(
                "Missing required elements in component configuration")

        self._context.rx['register_action'].on_next(
            RegisterAction(menu_title=self._configuration['menu'],
                           action_name=self._configuration['name'],
                           shortcut=self._configuration['shortcut']
                           if 'shortcut' in self._configuration else None,
                           status_tip=self._configuration['status_tip']
                           if 'status_tip' in self._configuration else None))

    def run(self, rx_value: RunAction):
        """ Entry point for running the plugin

            Args:
                rx_value (RunAction): The value published by the subject.
        """
        raise NotImplementedError
