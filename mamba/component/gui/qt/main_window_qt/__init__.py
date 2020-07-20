################################################################################################
##
##  Copyright (c) Mamba Developers. All rights reserved.
##  Licensed under the MIT License. See License.txt in the project root for license information.
##
################################################################################################

""" Main window implemented with Qt5 """

import os
from typing import Callable, Optional, Dict, List

from rx import operators as op

from PySide2.QtWidgets import QApplication, QMainWindow, QWidget, \
    QMenu, QAction, QSplashScreen, QMdiArea, QMdiSubWindow, QMenuBar
from PySide2.QtCore import QTimer, Qt
from PySide2.QtGui import QPixmap, QGuiApplication, QKeySequence, QIcon

from mamba.core.context import Context
from mamba.core.component_base import MainWindow
from mamba.core.msg import Empty
from mamba.component.gui.msg import RegisterAction, RunAction
from .eula_manager import EulaManager


class MainWindowQt(MainWindow):
    """ Main window implemented with Qt5 """
    def __init__(self,
                 context: Context,
                 local_config: Optional[Dict[str, dict]] = None) -> None:
        # Initialize custom variables
        self._qt_app = QApplication(
            []) if QApplication.instance() is None else QApplication.instance(
            )
        self._action_widgets: List[QWidget] = []  # Storage of actions

        super().__init__(os.path.dirname(__file__), context, local_config)

    # Functions to be adapted

    def _register_observers(self) -> None:
        super()._register_observers()

        # register_window is received to register a new MDI window
        self._context.rx['register_window'].pipe(
            op.filter(lambda value: isinstance(value, QMdiSubWindow))
        ).subscribe(on_next=self._register_window)

    def _register_window(self, rx_value: QMdiSubWindow):
        self._app.mdiArea.addSubWindow(rx_value)

    def _create_main_window(self) -> None:
        """ Entry point for initializing the main window
            Note: It should be hidden per default.
        """
        self._app: QMainWindow = QMainWindow()
        self._app.setWindowTitle(self._configuration['title'])
        self._app.setWindowIcon(
            QIcon(
                os.path.join(self._context.get('mamba_dir'), 'artwork',
                             'mamba_icon.png')))

        self._app.mdiArea = QMdiArea()
        self._app.mdiArea.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self._app.mdiArea.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self._app.setCentralWidget(self._app.mdiArea)

    def _create_menu_bar(self) -> None:
        """ Entry point for creating the top menu bar """
        self._menu_bar = self._app.menuBar()

    def _create_splash_window(self) -> None:
        """ Entry point for creating and showing the load screen """
        # Create new splash window
        self._load_app = QSplashScreen()
        self._load_app.setPixmap(QPixmap(self.image_file))

        # Customize splash window size
        screen = QGuiApplication.primaryScreen().geometry()
        self._load_app.move(
            int((screen.width() - self._load_app.size().width()) / 2),
            int((screen.height() - self._load_app.size().height()) / 2))

        self._load_app.show()

    def _menu_add_action(self, menu: QMenu, rx_value: RegisterAction) -> None:
        """ Entry point for adding an action to a given menu

            Args:
                menu: The given menu.
                rx_value (RegisterAction): The value published by the subject.
        """
        # Register callback when command is selected from the menu
        widget = QWidget()
        action = QAction(text=rx_value.action_name, parent=widget)
        if rx_value.shortcut is not None:
            action.setShortcut(QKeySequence(rx_value.shortcut))
        action.setStatusTip(rx_value.status_tip)
        action.triggered.connect(
            lambda: self._context.rx['run_plugin'].on_next(
                RunAction(menu_title=rx_value.menu_title,
                          action_name=rx_value.action_name)))

        self._action_widgets.append(widget)
        menu.addAction(action)

    def _close_load_screen(self) -> None:
        """ Entry point for closing the load screen """
        if self._load_app is not None:
            self._load_app.destroy()
            self._load_app = None

    def _show(self) -> None:
        """ Entry point for showing main screen """
        self._app.showMaximized()

        mamba_config = os.path.join(self._context.get('mamba_dir'), 'mamba_config.json')

        if not os.path.exists(mamba_config):
            eula_manager = EulaManager(os.path.join(self._context.get('mamba_dir'), 'LICENSE'), self._app)

            result = eula_manager.run()

            if result == 1:
                f = open(mamba_config, 'w')
                f.close()
            else:
                self._close(Empty())

    def _hide(self) -> None:
        """ Entry point for hiding main screen """
        self._app.hide()

    def _close(self, rx_value: Empty) -> None:
        """ Entry point for closing application

            Args:
                rx_value (Empty): The value published by the subject.
        """
        if self._load_app is not None:
            self._load_app.close()

        if self._app is not None:
            self._app.close()

    def _start_event_loop(self) -> None:
        """
        Enters the main event loop and waits until close() is called.

        It is necessary to call this function to start event handling.The
        main event loop receives events from the window system and dispatches
        these to the application widgets.

        Generally, no user interaction can take place before calling
        start_event_loop().
        """
        if isinstance(self._qt_app, QApplication):
            self._qt_app.exec_()

    def _after(self, time_msec: int, action: Callable) -> None:
        """ Make the application perform an action after a time delay.

        Args:
            time_msec (int): The time in milliseconds to delay he action.
            action (function): The action to execute after time_msec delay.
        """
        QTimer.singleShot(int(time_msec), action)

    def _add_menu(self, menu_name: str) -> QMenu:
        """Add a new top level menu in main window menu bar.

        Args:
            menu_name: The new menu name.

        Returns:
            QMenu: A reference to the newly created menu.
        """
        if not isinstance(self._menu_bar, QMenuBar):
            raise RuntimeError("Missing Menu Bar")

        menu = self._menu_bar.addMenu(menu_name)
        self._menus[menu_name] = menu
        return menu
