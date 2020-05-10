import os

from PySide2.QtWidgets import QApplication, QSplashScreen
from PySide2.QtGui import QPixmap, QGuiApplication
from PySide2.QtCore import QTimer

from mamba_server.components.gui.load_screen.interface import LoadScreenInterface


class LoadScreen(LoadScreenInterface):
    def __init__(self, context=None):
        self.app = QApplication(
            []) if QApplication.instance() is None else QApplication.instance(
            )

        super(LoadScreen, self).__init__(os.path.dirname(__file__), context)

        self.splash_screen = QSplashScreen()

    def execute(self):
        self.splash_screen.setPixmap(QPixmap(self.configuration['image']))

        screen = QGuiApplication.primaryScreen().geometry()
        self.splash_screen.move(
            (screen.width() - self.splash_screen.size().width()) / 2,
            (screen.height() - self.splash_screen.size().height()) / 2)

        self.splash_screen.show()

    def close(self):
        self.splash_screen.destroy()

    def after(self, time_msec, action):
        QTimer.singleShot(int(time_msec), action)

    def start_event_loop(self):
        self.app.exec_()


if __name__ == '__main__':
    load_screen = LoadScreen()
    load_screen.execute()
    load_screen.start_event_loop()
