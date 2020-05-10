import os

import tkinter as tk
from tkinter import messagebox

from mamba_server.components.gui.main_window.interface import MainWindowInterface


class MainWindow(MainWindowInterface):
    def __init__(self, context=None):
        super(MainWindow, self).__init__(os.path.dirname(__file__), context)

        self.app = tk.Tk()
        self.hide()
        self.menubar = tk.Menu(self.app)
        self.app.config(menu=self.menubar)
        self.menus = {}

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

        menu.add_command(label=action_name, command=component_action)

    def start_event_loop(self):
        self.app.mainloop()

    def is_menu_in_bar(self, search_menu):
        """Checks if Menu is already in Main Window Menu bar.

        Args:
            search_menu (str): The searched menu name.

        Returns:
            bool: True if it menu is already in menu bar, otherwise false.
        """
        return search_menu in self.menus

    def show(self):
        self.app.update()
        self.app.deiconify()

    def hide(self):
        self.app.withdraw()

    def close(self):
        self.app.destroy()

    def add_menu_in_bar(self, menu_name):
        menu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label=menu_name, menu=menu)
        self.menus[menu_name] = menu
        return menu

    def get_menu_in_bar(self, search_menu):
        """Returns Menu is already in Main Window Menu bar.

        Args:
            search_menu (str): The searched menu name.

        Returns:
            tk.Menu: Menu with title "search_menu". None is menu has not been found.
        """
        if search_menu in self.menus:
            return self.menus[search_menu]

        return None

    def after(self, time_msec, action):
        self.app.after(int(time_msec), action)

class Prueba:
    def about(self):
        messagebox.showinfo("Information", "Informative message")


if __name__ == '__main__':
    prueba = Prueba()
    main_window = MainWindow()
    #main_window.add_menu_in_bar('prueba')
    main_window.register_action('prueba', prueba.about)
    main_window.register_action('prueb2', prueba.about)

    main_window.show()
    main_window.start_event_loop()
