import os
import pkgutil

from PySide2.QtWidgets import QMessageBox

from mamba_server.components.gui.plugins.interface import GuiPluginInterface


class GuiPlugin(GuiPluginInterface):
    def __init__(self, context=None):
        super(GuiPlugin, self).__init__(os.path.dirname(__file__), context)
        self.box_message = "<b>Mamba Server v{}</b>"
        self.version = ""

    def execute(self):
        self.version = pkgutil.get_data('mamba_server',
                                        'VERSION').decode('ascii').strip()
        QMessageBox.about(self.widget, self.configuration['message_box_title'],
                          self.box_message.format(self.version))
