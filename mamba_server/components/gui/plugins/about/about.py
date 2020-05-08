from PySide2.QtWidgets import QMessageBox, QAction

from mamba_server.components.base.gui_component_base import GuiComponentBase


class About(GuiComponentBase):
    def __init__(self, context=None):
        super(About, self).__init__()

        self.aboutAct = QAction("&About",
                                self,
                                statusTip=self.status_tip(),
                                triggered=self.show)

        self.helpMenu = context.get('main_window').menuBar().addMenu("&Help")
        self.helpMenu.addAction(self.aboutAct)

    def show(self):
        QMessageBox.about(self, "About Mamba MMI",
                          "<b>Mamba MMI v0.1 - Genesis</b>")
