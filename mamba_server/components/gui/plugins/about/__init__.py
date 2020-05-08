import os
import pkgutil

from PySide2.QtWidgets import QMessageBox

from mamba_server.components.gui.plugins import GuiPlugin


class About(GuiPlugin):
    def __init__(self, context=None):
        super(About, self).__init__(os.path.dirname(__file__), context)

    def show(self):
        __version__ = pkgutil.get_data('mamba_server', 'VERSION').decode('ascii').strip()
        QMessageBox.about(self, "About Mamba Server",
                          f"<b>Mamba Server v{__version__}</b>")
