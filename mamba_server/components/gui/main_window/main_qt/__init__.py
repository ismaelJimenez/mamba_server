""" Main window implemented with Qt5 """

import os

from PySide2.QtWidgets import QApplication, QMainWindow, QWidget, \
    QMenu, QAction
from PySide2.QtCore import QTimer

from mamba_server.components.component_base import ComponentBase
from mamba_server.exceptions import ComponentConfigException

from mamba_server.components.observer_types.empty import Empty
from mamba_server.components.observer_types.app_status import AppStatus
from mamba_server.components.gui.main_window.observer_types.register_action\
    import RegisterAction
from mamba_server.components.gui.main_window.observer_types.run_action\
    import RunAction


class MainWindow(ComponentBase):
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

        self._context.rx.subscribe(subject_name='quit',
                                   on_next=self._close,
                                   op_filter=lambda rx: isinstance(rx, Empty))

        self._context.rx.subscribe(
            subject_name='app_status',
            on_next=self._run,
            op_filter=lambda rx: isinstance(rx, AppStatus
                                            ) and rx == AppStatus.Running)

        self._context.rx.subscribe(
            subject_name='register_action',
            on_next=self._register_action,
            op_filter=lambda rx: isinstance(rx, RegisterAction))

    # Internal functions

    def _register_action(self, rx_value):
        """ Entry point for running the plugin

            Note: The expected rx_value is of type RegisterAction.

            Args:
                rx_value (RegisterAction): The value published by
                                           the subject.
        """
        if not self._exists_menu(rx_value.menu_title):
            menu = self._add_menu(rx_value.menu_title)
        else:
            menu = self._get_menu(rx_value.menu_title)

        if self._is_action_in_menu(rx_value.menu_title, rx_value.action_name):
            raise ComponentConfigException(
                f"Another action '{rx_value.menu_title}' already exists"
                f" in menu '{rx_value.action_name}'")

        widget = QWidget()
        action = QAction(rx_value.action_name,
                         widget,
                         shortcut=rx_value.shortcut,
                         statusTip=rx_value.status_tip,
                         triggered=lambda: self._context.rx.on_next(
                             'run_plugin',
                             RunAction(menu_title=rx_value.menu_title,
                                       action_name=rx_value.action_name)))

        self._action_widgets.append(widget)
        menu.addAction(action)

        self._menu_actions.append(
            f'{rx_value.menu_title}_{rx_value.action_name}')

    def _run(self, rx_value):
        """ Entry point for running the window

            Args:
                rx_value (AppStatus): The value published by the subject.
        """
        self._show()
        self._start_event_loop()

    def _show(self):
        """
        Entry point for showing main screen
        """
        self._app.show()

    def _hide(self):
        """
        Entry point for hiding main screen
        """
        self._app.hide()

    def _close(self, rx_value=None):
        """
        Entry point for closing main screen
        """
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

    def _after(self, time_msec, action):
        """ Make the application perform an action after a time delay.

        Args:
            time_msec (int): The time in milliseconds to delay he action.
            action (function): The action to execute after time_msec delay.
        """
        QTimer.singleShot(int(time_msec), action)

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
        return f'{search_menu}_{search_action}' in self._menu_actions
