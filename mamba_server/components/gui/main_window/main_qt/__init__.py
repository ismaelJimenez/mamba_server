import os

from PySide2.QtWidgets import QApplication, QMainWindow, QWidget, QMenu, QAction
from PySide2.QtCore import QTimer

from mamba_server.components.gui.main_window.interface import MainWindowInterface


class MainWindow(MainWindowInterface):
    def __init__(self, context=None):
        super(MainWindow, self).__init__(os.path.dirname(__file__), context)

        self.app = QApplication(
            []) if QApplication.instance() is None else QApplication.instance(
            )
        self.main_window = QMainWindow()

        self.main_window.setWindowTitle(self.configuration['title'])

        self.widgets = []

    def register_action(self,
                        menu_title,
                        action_name,
                        component_action,
                        shortcut="",
                        statusTip=""):
        if not self.is_menu_in_bar(menu_title):
            menu = self.add_menu_in_bar(menu_title)
        else:
            menu = self.get_menu_in_bar(menu_title)

        widget = QWidget()
        action = QAction(action_name,
                         widget,
                         shortcut=shortcut,
                         statusTip=statusTip,
                         triggered=component_action)

        self.widgets.append(widget)
        menu.addAction(action)

    def start_event_loop(self):
        self.app.exec_()

    def is_menu_in_bar(self, search_menu):
        """Checks if Menu is already in Main Window Menu bar.

        Args:
            search_menu (str): The searched menu name.

        Returns:
            bool: True if it menu is already in menu bar, otherwise false.
        """
        return search_menu in [
            menu.title()
            for menu in self.main_window.menuBar().findChildren(QMenu)
        ]

    def show(self):
        self.main_window.show()

    def hide(self):
        self.main_window.hide()

    def close(self):
        self.main_window.close()

    def add_menu_in_bar(self, menu_name):
        return self.main_window.menuBar().addMenu(menu_name)

    def get_menu_in_bar(self, search_menu):
        """Returns Menu is already in Main Window Menu bar.

        Args:
            search_menu (str): The searched menu name.
            main_window (QMainWindow): The main window application.

        Returns:
            QMenu: Menu with title "search_menu". None is menu has not been found.
        """
        menu = [
            menu for menu in self.main_window.menuBar().findChildren(QMenu)
            if menu.title() == search_menu
        ]

        if len(menu) > 0:
            return menu[0]

        return None

    def after(self, time_msec, action):
        QTimer.singleShot(int(time_msec), action)

if __name__ == '__main__':
    main_window = MainWindow()
    main_window.show()
    main_window.start_event_loop()

