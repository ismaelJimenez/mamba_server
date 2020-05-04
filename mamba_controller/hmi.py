import sys
from PySide2.QtWidgets import QApplication, QLabel


def execute():
    app = QApplication(sys.argv)
    label = QLabel("Hello World!")
    label.show()
    app.exec_()
