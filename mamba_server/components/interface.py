""" The Generic component interface.
"""

import os
import json

from mamba_server.utils.component import generate_component_configuration

SETTINGS_FILE = "settings.json"
COMPONENT_CONFIG_FILE = "component.config.json"


class ComponentInterface:
    def __init__(self, settings_folder, config_folder, context):
        super(ComponentInterface, self).__init__()

        # Retrieve component configuration
        self._context = context
        self._configuration = {}

        with open(os.path.join(settings_folder, SETTINGS_FILE)) as f:
            settings_description = json.load(f)

        with open(os.path.join(config_folder, COMPONENT_CONFIG_FILE)) as f:
            file_config = json.load(f)

        self._configuration = generate_component_configuration(
            settings=settings_description, config_file=file_config)
