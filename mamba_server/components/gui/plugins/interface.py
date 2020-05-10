""" The GuiPlugin components make services available to the application.
"""

import os
import json

from PySide2.QtWidgets import QWidget, QAction

from mamba_server.utils.component import generate_component_configuration

SETTINGS_FILE = "settings.json"
COMPONENT_CONFIG_FILE = "component.config.json"


class GuiPluginInterface:
    def __init__(self, folder, context):
        super(GuiPluginInterface, self).__init__()

        self.context = context
        self.configuration = {}

        with open(os.path.join(os.path.dirname(__file__), SETTINGS_FILE)) as f:
            settings_description = json.load(f)

        with open(os.path.join(folder, COMPONENT_CONFIG_FILE)) as f:
            file_config = json.load(f)

        self.configuration = generate_component_configuration(
            settings=settings_description, config_file=file_config)

        self._register_menu()

    def _register_menu(self):
        # Add Menu if it is not already in menu bar
        if (self.context is not None) and self.context.get('main_window'):
            self.context.get('main_window').register_action(
                menu_title=self.configuration['menu'],
                action_name=self.configuration['name'],
                component_action=self.execute,
                shortcut=self.configuration['shortcut'],
                statusTip=self.configuration['status_tip'])

    def execute(self):
        """
        Entry point for running gui plugin
        """
        raise NotImplementedError
