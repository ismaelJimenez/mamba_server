""" Plugin to show About message implemented in Qt5 """

import os
import pkgutil

from PySide2.QtWidgets import QMessageBox, QWidget, QApplication

from mamba.components.plugins import PluginBase
from mamba.components.main.observable_types import RunAction


class Plugin(PluginBase):
    """ Plugin to show About message implemented in Qt5 """
    def __init__(self, context, local_config=None):
        super(Plugin, self).__init__(os.path.dirname(__file__), context,
                                     local_config)

        # Define custom variables
        self._version = None
        self._box_message = None
        self._app = None

    def initialize(self):
        super(Plugin, self).initialize()

        # Initialize custom variables
        self._app = QApplication(
            []) if QApplication.instance() is None else QApplication.instance(
            )

        self._version = pkgutil.get_data('mamba',
                                         'VERSION').decode('ascii').strip()
        self._box_message = f"Mamba Server v{self._version}"

    def run(self, rx_value: RunAction):
        """ Entry point for running the plugin

            Args:
                rx_value (RunAction): The value published by the subject.
        """
        QMessageBox.about(QWidget(), self._configuration['message_box_title'],
                          self._box_message)
