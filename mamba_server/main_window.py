import sys

from PySide2.QtWidgets import QApplication, QPushButton, QMainWindow, \
    QWidget, QVBoxLayout, QLabel, QAction
from PySide2.QtCore import Slot

from mamba_server.components.gui.about.about import About


# Subclass QMainWindow to customise your application's main window
class MainWindow(QMainWindow):
    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)

        self.setWindowTitle("My Awesome App")

        layout = QVBoxLayout()

        # Create a button, connect it and show it
        self.click_me = QPushButton("Click me")
        self.click_me.clicked.connect(self.say_hello)

        layout.addWidget(self.click_me)

        self.click_me_label = QLabel("Named:")

        layout.addWidget(self.click_me_label)

        widget = QWidget()
        widget.setLayout(layout)

        self.about = About()

        self.aboutAct = QAction("&About",
                                self,
                                statusTip=self.about.status_tip(),
                                triggered=self.about.show)

        self.helpMenu = self.menuBar().addMenu("&Help")
        self.helpMenu.addAction(self.aboutAct)

        # Set the central widget of the Window. Widget will expand
        # to take up all the space in the window by default.
        self.setCentralWidget(widget)

    @Slot()
    def say_hello(self):
        self.click_me_label.setText("Hello!")


def execute():
    # You need one (and only one) QApplication instance per application.
    # Pass in sys.argv to allow command line arguments for your app.
    # If you know you won't use command line arguments
    # QApplication([]) works too.
    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()  # IMPORTANT!!!!! Windows are hidden by default.

    # Start the event loop.
    app.exec_()

    # Your application won't reach here until you exit and the event
    # loop has stopped.


if __name__ == '__main__':
    execute()
