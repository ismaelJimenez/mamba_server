""" Plugin to show About message implemented in Qt5 """

import os
import pkgutil

from PySide2.QtWidgets import QMessageBox, QWidget, QApplication

from mamba_server.components.gui.plugins.interface import GuiPluginInterface


class GuiPlugin(GuiPluginInterface):
    """ Plugin to show About message implemented in Qt5 """
    def __init__(self, context=None):
        super(GuiPlugin, self).__init__(os.path.dirname(__file__), context)

        self._app = QApplication(
            []) if QApplication.instance() is None else QApplication.instance(
            )

        self._box_message = "Mamba Server v{}"
        self._version = pkgutil.get_data('mamba_server',
                                         'VERSION').decode('ascii').strip()

    def execute(self):
        QMessageBox.about(QWidget(), self._configuration['message_box_title'],
                          self._box_message.format(self._version))
