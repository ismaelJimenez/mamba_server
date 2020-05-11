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

        # Retrieve component configuration
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
                        shortcut='',
                        status_tip=''):
        """
        Entry point for registering a new action inside a given menu.
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
        """
        Entry point for closing main screen
        """
        raise NotImplementedError

    def start_event_loop(self):
        """
        Entry point for starting main window event loop.
        """
        raise NotImplementedError

    def after(self, time_msec, action):
        """
        Entry point for performing an action after given milliseconds.
        """
        raise NotImplementedError
