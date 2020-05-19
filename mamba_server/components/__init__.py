""" The Generic component interface """

import os
import yaml

from mamba_server.utils.component import merge_dicts

COMPONENT_CONFIG_FILE = "config.yml"


class ComponentBase:
    """ The Generic component interface """
    def __init__(self, config_folder, context, local_config=None):
        super(ComponentBase, self).__init__()

        # Retrieve component configuration
        self._context = context

        try:
            with open(os.path.join(config_folder,
                                   COMPONENT_CONFIG_FILE)) as file:
                file_config = yaml.load(file, Loader=yaml.FullLoader)
        except FileNotFoundError:
            file_config = {}

        local_config = local_config or {}

        self._configuration = merge_dicts(local_config, file_config)

    def initialize(self):
        """ Entry point for component initialization """
