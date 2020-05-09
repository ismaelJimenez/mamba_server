import os
import pkgutil

from PySide2.QtWidgets import QMessageBox

from mamba_server.components.gui.plugins import GuiPluginInterface


class GuiPlugin(GuiPluginInterface):
    def __init__(self, context=None):
        super(GuiPlugin, self).__init__(os.path.dirname(__file__), context)

    def show(self):
        __version__ = pkgutil.get_data('mamba_server',
                                       'VERSION').decode('ascii').strip()
        QMessageBox.about(self, "About Mamba Server",
                          "<b>Mamba Server v{}</b>".format(__version__))
