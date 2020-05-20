""" Main window implemented with Qt5 """

import os

from PySide2.QtWidgets import QApplication, QMainWindow, QWidget, \
    QMenu, QAction, QSplashScreen
from PySide2.QtCore import QTimer
from PySide2.QtGui import QPixmap, QGuiApplication

from mamba_server.components.main import MainBase
from mamba_server.components.observable_types import Empty
from mamba_server.components.main.observable_types import RegisterAction, \
    RunAction


class MainWindow(MainBase):
    """ Main window implemented with Qt5 """
    def __init__(self, context, local_config=None):
        # Initialize custom variables
        self._qt_app = self._qt_app = QApplication(
            []) if QApplication.instance() is None else QApplication.instance(
            )
        self._action_widgets = []  # Storage of actions

        super(MainWindow, self).__init__(os.path.dirname(__file__), context,
                                         local_config)

    # Functions to be adapted

    def _create_main_window(self):
        """ Entry point for initializing the main window
            Note: It should be hidden per default.
        """
        self._app = QMainWindow()
        self._app.setWindowTitle(self._configuration['title'])

    def _create_menu_bar(self):
        """ Entry point for creating the top menu bar """
        self._menu_bar = self._app.menuBar()

    def _create_splash_window(self):
        """ Entry point for creating and showing the load screen """
        # Create new splash window
        self._load_app = QSplashScreen()
        self._load_app.setPixmap(QPixmap(self.image_file))

        # Customize splash window size
        screen = QGuiApplication.primaryScreen().geometry()
        self._load_app.move(
            (screen.width() - self._load_app.size().width()) / 2,
            (screen.height() - self._load_app.size().height()) / 2)

        self._load_app.show()

    def _menu_add_action(self, menu: QMenu, rx_value: RegisterAction):
        """ Entry point for adding an action to a given menu

            Args:
                menu: The given menu.
                rx_value (RegisterAction): The value published by the subject.
        """
        # Register callback when command is selected from the menu
        widget = QWidget()
        action = QAction(
            rx_value.action_name,
            widget,
            shortcut=rx_value.shortcut,
            statusTip=rx_value.status_tip,
            triggered=lambda: self._context.rx['run_plugin'].on_next(
                RunAction(menu_title=rx_value.menu_title,
                          action_name=rx_value.action_name)))

        self._action_widgets.append(widget)
        menu.addAction(action)

    def _close_load_screen(self):
        """ Entry point for closing the load screen """
        self._load_app.destroy()
        self._load_app = None

    def _show(self):
        """ Entry point for showing main screen """
        self._app.show()

    def _hide(self):
        """ Entry point for hiding main screen """
        self._app.hide()

    def _close(self, rx_value: Empty):
        """ Entry point for closing application

            Args:
                rx_value (Empty): The value published by the subject.
        """
        if self._load_app is not None:
            self._load_app.close()

        if self._app is not None:
            self._app.close()

    def _start_event_loop(self):
        """
        Enters the main event loop and waits until close() is called.

        It is necessary to call this function to start event handling.The
        main event loop receives events from the window system and dispatches
        these to the application widgets.

        Generally, no user interaction can take place before calling
        start_event_loop().
        """
        self._qt_app.exec_()

    def _after(self, time_msec: int, action: callable):
        """ Make the application perform an action after a time delay.

        Args:
            time_msec (int): The time in milliseconds to delay he action.
            action (function): The action to execute after time_msec delay.
        """
        QTimer.singleShot(int(time_msec), action)

    def _add_menu(self, menu_name: str) -> QMenu:
        """Add a new top level menu in main window menu bar.

        Args:
            menu_name (str): The new menu name.

        Returns:
            QMenu: A reference to the newly created menu.
        """
        menu = self._menu_bar.addMenu(menu_name)
        self._menus[menu_name] = menu
        return menu
