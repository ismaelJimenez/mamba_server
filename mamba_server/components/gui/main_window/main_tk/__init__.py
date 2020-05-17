""" Main window implemented with TkInter """

import os
import tkinter as tk

from mamba_server.components.gui.main_window.interface import \
    MainWindowInterface
from mamba_server.exceptions import ComponentConfigException


class MainWindow(MainWindowInterface):
    """ Main window implemented with TkInter """
    def __init__(self, context):
        super(MainWindow, self).__init__(os.path.dirname(__file__), context)

        self._app = tk.Tk()
        self._app.protocol("WM_DELETE_WINDOW", self.close)
        self._app.title(self._configuration['title'])
        self.hide()
        self._menu_bar = tk.Menu(self._app)
        self._app.config(menu=self._menu_bar)
        self._menus = {}
        self._menu_actions = []

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
            raise ComponentConfigException(
                f"Another action '{menu_title}' already exists"
                f" in menu '{action_name}'")

        menu.add_command(
            label=action_name,
            command=lambda: self._context.rx.on_next('run_plugin', {
                'menu': menu_title,
                'action': action_name
            }))
        self._menu_actions.append(f'{menu_title}_{action_name}')

    def show(self):
        """
        Entry point for showing main screen
        """
        self._app.update()
        self._app.deiconify()

    def hide(self):
        """
        Entry point for hiding main screen
        """
        self._app.withdraw()
        self._app.update()

    def close(self, rx_on_next_value=None):
        """
        Entry point for closing main screen
        """

        # INFO: quit() stops the TCL interpreter, so the Tkinter - app will
        # stop. destroy() just terminates the mainloop and deletes all
        # widgets.

        self._app.quit()

    def start_event_loop(self):
        """
        Enters the main event loop and waits until close() is called.

        It is necessary to call this function to start event handling.The
        main event loop receives events from the window system and dispatches
        these to the application widgets.

        Generally, no user interaction can take place before calling
        start_event_loop().
        """
        self._app.mainloop()

    def after(self, time_msec, action):
        """ Make the application perform an action after a time delay.

        Args:
            time_msec (int): The time in milliseconds to delay he action.
            action (function): The action to execute after time_msec delay.
        """
        self._app.after(int(time_msec), action)

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
            tk.Menu: A reference to the newly created menu.
        """
        menu = tk.Menu(self._menu_bar, tearoff=0)
        self._menu_bar.add_cascade(label=menu_name, menu=menu)
        self._menus[menu_name] = menu
        return menu

    def _get_menu(self, search_menu):
        """Returns Menu is already in Main Window Menu bar.

        Args:
            search_menu (str): The searched menu name.

        Returns:
            tk.Menu: Menu with title "search_menu". None is menu has
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
