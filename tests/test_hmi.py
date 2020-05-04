from mamba_controller.hmi import MainWindow
from PySide2 import QtCore


def test_hello(qtbot):
    widget = MainWindow()
    qtbot.addWidget(widget)

    # click in the Greet button and make sure it updates the appropriate label
    qtbot.mouseClick(widget.click_me, QtCore.Qt.LeftButton)

    assert widget.click_me_label.text() == "Hello!"
