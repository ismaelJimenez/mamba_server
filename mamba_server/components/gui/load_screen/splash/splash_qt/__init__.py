""" Splash screen implemented with Qt5 """

import os

from PySide2.QtWidgets import QApplication, QSplashScreen
from PySide2.QtGui import QPixmap, QGuiApplication
from PySide2.QtCore import QTimer

from mamba_server.utils.misc import path_from_string
from mamba_server.components.gui.load_screen.interface import \
    LoadScreenInterface


class LoadScreen(LoadScreenInterface):
    """ Splash screen implemented with Qt5 """
    def __init__(self, context=None):
        super(LoadScreen, self).__init__(os.path.dirname(__file__), context)

        self._qt_app = QApplication(
            []) if QApplication.instance() is None else QApplication.instance(
            )

        self._app = QSplashScreen()
        self._app.setPixmap(
            QPixmap(path_from_string(self._configuration['image'])))

        screen = QGuiApplication.primaryScreen().geometry()
        self._app.move((screen.width() - self._app.size().width()) / 2,
                       (screen.height() - self._app.size().height()) / 2)

    def show(self):
        """
        Entry point for showing load screen
        """
        self._app.show()

    def hide(self):
        """
        Entry point for hiding load screen
        """
        self._app.hide()

    def close(self):
        """
        Entry point for closing load screen
        """
        self._app.close()
        self._qt_app.quit()

    def start_event_loop(self):
        """
        Enters the main event loop and waits until close() is called.

        It is necessary to call this function to start event handling.The
        main event loop receives events from the window system and dispatches
        these to the application widgets.

        Generally, no user interaction can take place before calling
        start_event_loop().
        """
        self._qt_app.exec_()

    def after(self, time_msec, action):
        """ Make the application perform an action after a time delay.

        Args:
            time_msec (int): The time in milliseconds to delay he action.
            action (function): The action to execute after time_msec delay.
        """
        QTimer.singleShot(int(time_msec), action)
