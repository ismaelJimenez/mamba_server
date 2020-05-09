import os
import json

from PySide2.QtWidgets import QWidget, QAction, QMenu

from mamba_server.utils.component import generate_component_configuration, is_menu_in_bar, get_menu_in_bar

SETTINGS_FILE = "settings.json"
COMPONENT_CONFIG_FILE = "component.config.json"


class GuiPluginInterface(QWidget):
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
            self.action = QAction(self.configuration['name'],
                                  self,
                                  shortcut=self.configuration['shortcut'],
                                  statusTip=self.configuration['status_tip'],
                                  triggered=self.show)

            if not is_menu_in_bar(self.configuration['menu'],
                                  self.context.get('main_window')):
                self.menu = self.context.get('main_window').menuBar().addMenu(
                    self.configuration['menu'])
            else:
                self.menu = get_menu_in_bar(self.configuration['menu'],
                                            self.context.get('main_window'))

            self.menu.addAction(self.action)

    def show(self):
        """
        Entry point for showing gui plugin
        """
        raise NotImplementedError
