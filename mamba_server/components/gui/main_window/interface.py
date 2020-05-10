""" The LoadScreen components enable showing an screen during load.
"""

import os
import json

from mamba_server.utils.component import generate_component_configuration

SETTINGS_FILE = "settings.json"
COMPONENT_CONFIG_FILE = "component.config.json"


class MainWindowInterface:
    def __init__(self, folder, context):
        super(MainWindowInterface, self).__init__()

        self.context = context
        self.configuration = {}

        with open(os.path.join(os.path.dirname(__file__), SETTINGS_FILE)) as f:
            settings_description = json.load(f)

        with open(os.path.join(folder, COMPONENT_CONFIG_FILE)) as f:
            file_config = json.load(f)

        self.configuration = generate_component_configuration(
            settings=settings_description, config_file=file_config)

    def register_action(self,
                        menu_title,
                        action_name,
                        component_action,
                        shortcut="",
                        statusTip=""):
        """
        Entry point for an action inside a menu
        """
        raise NotImplementedError

    def start_event_loop(self):
        """
        Entry point for starting event loop.
        """
        raise NotImplementedError

    def is_menu_in_bar(self, search_menu):
        """Checks if Menu is already in Main Window Menu bar.

        Args:
            search_menu (str): The searched menu name.

        Returns:
            bool: True if it menu is already in menu bar, otherwise false.
        """
        raise NotImplementedError

    def show(self):
        """
        Entry point for showing main screen
        """
        raise NotImplementedError

    def hide(self):
        """
        Entry point for hiding main screen
        """
        raise NotImplementedError

    def close(self):
        raise NotImplementedError

    def add_menu_in_bar(self, menu_name):
        raise NotImplementedError

    def get_menu_in_bar(self, search_menu):
        raise NotImplementedError

    def after(self, time_msec, action):
        """
        Entry point for performing an action after given milliseconds.
        """
        raise NotImplementedError














    def close(self):
        """
        Entry point for closing load screen
        """
        raise NotImplementedError

    def after(self, time_msec, action):
        """
        Entry point for performing an action after given milliseconds.
        """
        raise NotImplementedError

    def start_event_loop(self):
        """
        Entry point for starting event loop.
        """
        raise NotImplementedError
