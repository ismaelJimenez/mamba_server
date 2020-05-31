""" The Generic component interface """

import os
import yaml

from mamba.utils.component import merge_dicts
from mamba.core.msg import Log, LogLevel

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

        self._name = self._configuration[
            'name'] if 'name' in self._configuration else ''
        self._log_dev = lambda message: self._context.rx['log'].on_next(
            Log(LogLevel.Dev, message, self._name))
        self._log_info = lambda message: self._context.rx['log'].on_next(
            Log(LogLevel.Info, message, self._name))
        self._log_warning = lambda message: self._context.rx['log'].on_next(
            Log(LogLevel.Warning, message, self._name))
        self._log_error = lambda message: self._context.rx['log'].on_next(
            Log(LogLevel.Error, message, self._name))

    def initialize(self):
        """ Entry point for component initialization """
