""" The Generic component interface """

import os
import json
import yaml

from mamba_server.utils.component import generate_component_configuration

SETTINGS_FILE = "settings.yml"
COMPONENT_CONFIG_FILE = "config.yml"


class ComponentInterface:
    """ The Generic component interface """
    def __init__(self, settings_folder, config_folder, context):
        super(ComponentInterface, self).__init__()

        # Retrieve component configuration
        self._context = context
        self._configuration = {}

        with open(os.path.join(settings_folder, SETTINGS_FILE)) as file:
            settings_description = yaml.load(file, Loader=yaml.FullLoader)

        with open(os.path.join(config_folder, COMPONENT_CONFIG_FILE)) as file:
            file_config = yaml.load(file, Loader=yaml.FullLoader)

        self._configuration = generate_component_configuration(
            settings=settings_description, config_file=file_config)
