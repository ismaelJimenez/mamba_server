""" The LoadScreen components enable showing an screen during load.
"""

import os
import json

from mamba_server.utils.component import generate_component_configuration

SETTINGS_FILE = "settings.json"
COMPONENT_CONFIG_FILE = "component.config.json"


class LoadScreenInterface:
    def __init__(self, folder, context):
        super(LoadScreenInterface, self).__init__()

        self.context = context
        self.configuration = {}

        with open(os.path.join(os.path.dirname(__file__), SETTINGS_FILE)) as f:
            settings_description = json.load(f)

        with open(os.path.join(folder, COMPONENT_CONFIG_FILE)) as f:
            file_config = json.load(f)

        self.configuration = generate_component_configuration(
            settings=settings_description, config_file=file_config)

    def execute(self):
        """
        Entry point for running load screen
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
