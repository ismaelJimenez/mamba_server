from PySide2.QtWidgets import QMessageBox

from mamba_server.components.base.gui_component_base import GuiComponentBase


class About(GuiComponentBase):
    def __init__(self):
        super(About, self).__init__()

    def show(self):
        QMessageBox.about(self, "About Mamba MMI",
                          "<b>Mamba MMI v0.1 - Genesis</b>")
