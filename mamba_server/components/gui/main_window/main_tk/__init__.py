""" Main window implemented with TkInter """

import os
import tkinter as tk

from mamba_server.components.component_base import ComponentBase
from mamba_server.exceptions import ComponentConfigException

from mamba_server.components.observer_types.empty import Empty
from mamba_server.components.gui.main_window.observer_types.register_action\
    import RegisterAction
from mamba_server.components.gui.main_window.observer_types.run_action\
    import RunAction


class MainWindow(ComponentBase):
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

        self._context.rx.subscribe(subject_name='quit',
                                   on_next=self.close,
                                   op_filter=lambda rx: isinstance(rx, Empty))

        self._context.rx.subscribe(
            subject_name='register_action',
            on_next=self.register_action,
            op_filter=lambda rx: isinstance(rx, RegisterAction))

    def register_action(self, rx_value):
        """ Entry point for running the plugin.

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

        menu.add_command(label=rx_value.action_name,
                         command=lambda: self._context.rx.on_next(
                             'run_plugin',
                             RunAction(menu_title=rx_value.menu_title,
                                       action_name=rx_value.action_name)))
        self._menu_actions.append(
            f'{rx_value.menu_title}_{rx_value.action_name}')

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

    def close(self, rx_value=None):
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
