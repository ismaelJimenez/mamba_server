""" The Generic component interface """

import os
import yaml

COMPONENT_CONFIG_FILE = "config.yml"


class ComponentBase:
    """ The Generic component interface """
    def __init__(self, config_folder, context, local_config=None):
        super(ComponentBase, self).__init__()

        # Retrieve component configuration
        self._context = context

        with open(os.path.join(config_folder, COMPONENT_CONFIG_FILE)) as file:
            file_config = yaml.load(file, Loader=yaml.FullLoader)

        local_config = local_config or {}

        self._configuration = dict(
            list(file_config.items()) + list(local_config.items()))

    def initialize(self):
        """ Entry point for component initialization """
