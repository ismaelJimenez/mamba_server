from PySide2.QtWidgets import QWidget, QMessageBox

class about(QWidget):
    def __init__(self):
        super(about, self).__init__()

    def show(self):
        QMessageBox.about(self, "About Mamba MMI", "<b>Mamba MMI v0.1 - Genesis</b>")