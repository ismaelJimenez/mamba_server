""" The GuiPlugin components make services available to the application """

import os

from mamba_server.components.interface import ComponentInterface


class GuiPluginInterface(ComponentInterface):
    """ The GuiPlugin components make services available to the application """
    def __init__(self, folder, context):
        super(GuiPluginInterface, self).__init__(os.path.dirname(__file__),
                                                 folder, context)

        self._register_action()

    def execute(self):
        """
        Entry point for running gui plugin
        """
        raise NotImplementedError

    def _register_action(self):
        """
        Registering a new action inside a given menu.
        """
        if (self._context is not None) and self._context.get('main_window'):
            self._context.get('main_window').register_action(
                menu_title=self._configuration['menu'],
                action_name=self._configuration['name'],
                component_action=self.execute,
                shortcut=self._configuration['shortcut'],
                status_tip=self._configuration['status_tip'])
