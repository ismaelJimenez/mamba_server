################################################################################################
##
##  Copyright (c) Mamba Developers. All rights reserved.
##  Licensed under the MIT License. See License.txt in the project root for license information.
##
################################################################################################

""" Plugin base """

from rx import operators as op

from typing import Optional

from mamba.core.context import Context
from mamba.core.component_base import Component
from mamba.core.exceptions import ComponentConfigException
from mamba.component.gui.msg import RegisterAction, RunAction


class GuiPlugin(Component):
    """ Plugin base class """
    def __init__(self,
                 config_folder: str,
                 context: Context,
                 local_config: Optional[dict] = None) -> None:
        super().__init__(config_folder, context, local_config)

        # Initialize observers
        self._register_observers()

    def _register_observers(self) -> None:
        self._context.rx['run_plugin'].pipe(
            op.filter(lambda value: value.menu_title == self._configuration[
                'menu'] and value.action_name == self._configuration['name'])
        ).subscribe(on_next=self.run)

    def initialize(self) -> None:
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

    def run(self, rx_value: RunAction) -> None:
        """ Entry point for running the plugin

            Args:
                rx_value (RunAction): The value published by the subject.
        """
        raise NotImplementedError
