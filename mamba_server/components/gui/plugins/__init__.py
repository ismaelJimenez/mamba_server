import os
import json

from PySide2.QtWidgets import QWidget, QAction, QMenu

from mamba_server.utils.component import generate_component_configuration

SETTINGS_FILE = "settings.json"
COMPONENT_CONFIG_FILE = "component.config.json"

class GuiPlugin(QWidget):
    def __init__(self, folder, context):
        super(GuiPlugin, self).__init__()

        self.context = context
        self.configuration = {}

        with open(os.path.join(os.path.dirname(__file__), SETTINGS_FILE)) as f:
            settings_description = json.load(f)

        with open(os.path.join(folder, COMPONENT_CONFIG_FILE)) as f:
            file_config = json.load(f)

        self.configuration = generate_component_configuration(settings=settings_description,
                                     config_file=file_config)

        self._register_menu()

    def _register_menu(self):
        self.action = QAction(self.configuration['name'],
                              self,
                              shortcut=self.configuration['shortcut'],
                              statusTip=self.configuration['status_tip'],
                              triggered=self.show)

        # Add Menu if it is not already in menu bar
        if self.configuration['menu'] not in [
                menu.title()
                for menu in self.context.get('main_window').menuBar().findChildren(QMenu)
        ]:
            self.menu = self.context.get('main_window').menuBar().addMenu(
                self.configuration['menu'])

        self.menu.addAction(self.action)

    def show(self):
        """
        Entry point for showing gui plugin
        """
        raise NotImplementedError
