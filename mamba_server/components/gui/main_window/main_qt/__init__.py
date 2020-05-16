""" Main window implemented with Qt5 """

import os

from PySide2.QtWidgets import QApplication, QMainWindow, QWidget, \
    QMenu, QAction
from PySide2.QtCore import QTimer

from mamba_server.components.gui.main_window.interface import \
    MainWindowInterface
from mamba_server.exceptions import ComponentConfigException


class MainWindow(MainWindowInterface):
    """ Main window implemented with Qt5 """
    def __init__(self, context):
        super(MainWindow, self).__init__(os.path.dirname(__file__), context)

        self._qt_app = QApplication(
            []) if QApplication.instance() is None else QApplication.instance(
            )
        self._app = QMainWindow()
        self._app.setWindowTitle(self._configuration['title'])
        self._menu_bar = self._app.menuBar()
        self._menus = {}
        self._menu_actions = []
        self._action_widgets = []  # Storage of actions

        self._context.rx.subscribe('quit', self.close)

    def register_action(self,
                        menu_title,
                        action_name,
                        component_action,
                        shortcut='',
                        status_tip=''):
        """Register a new action inside a given menu.

        Args:
            menu_title (str): The menu name.
            action_name (str): The action name.
            component_action (function): The action to execute.
            shortcut (str): Keys shorcut to execute action, if available.
            status_tip (str): Action status tip to show, if available.
        """
        if not self._exists_menu(menu_title):
            menu = self._add_menu(menu_title)
        else:
            menu = self._get_menu(menu_title)

        if self._is_action_in_menu(menu_title, action_name):
            raise ComponentConfigException("Another action '{}' already exists"
                                           " in menu '{}'".format(
                                               menu_title, action_name))

        widget = QWidget()
        action = QAction(action_name,
                         widget,
                         shortcut=shortcut,
                         statusTip=status_tip,
                         triggered=component_action)

        self._action_widgets.append(widget)
        menu.addAction(action)

        self._menu_actions.append('{}_{}'.format(menu_title, action_name))

    def show(self):
        """
        Entry point for showing main screen
        """
        self._app.show()

    def hide(self):
        """
        Entry point for hiding main screen
        """
        self._app.hide()

    def close(self, rx_on_next_value=None):
        """
        Entry point for closing main screen
        """
        self._app.close()

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

    # Internal functions

    def _exists_menu(self, search_menu):
        """Checks if Menu is already in Main Window Menu bar.

        Args:
            search_menu (str): The searched menu name.

        Returns:
            bool: True if it menu is already in menu bar, otherwise false.
        """
        return search_menu in self._menus

    def _add_menu(self, menu_name):
        """Add a new top level menu in main window menu bar.

        Args:
            menu_name (str): The new menu name.

        Returns:
            QMenu: A reference to the newly created menu.
        """
        self._menus[menu_name] = self._menu_bar.addMenu(menu_name)
        return self._menus[menu_name]

    def _get_menu(self, search_menu):
        """Returns Menu is already in Main Window Menu bar.

        Args:
            search_menu (str): The searched menu name.

        Returns:
            QMenu: Menu with title "search_menu". None is menu has
                   not been found.
        """
        if search_menu in self._menus:
            return self._menus[search_menu]

        return None

    def _is_action_in_menu(self, search_menu, search_action):
        """Checks if action is already in Menu.

        Args:
            search_menu (str): The searched menu name.
            search_action (str): The searched action name.

        Returns:
            bool: True if it action is already in menu, otherwise false.
        """
        return '{}_{}'.format(search_menu, search_action) in self._menu_actions
