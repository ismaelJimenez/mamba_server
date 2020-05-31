""" Custom Main window """

import os

from mamba.component.main import MainBase
from mamba.core.msg.empty import Empty
from mamba.component.main.observable_types.register_action \
    import RegisterAction


class MainWindow(MainBase):
    """ Custom Main window """
    def __init__(self, context, local_config=None):
        super(MainWindow, self).__init__(os.path.dirname(__file__), context,
                                         local_config)

    # Functions to be adapted

    def _create_main_window(self):
        """ Entry point for initializing the main window
            Note: It should be hidden per default.
        """
        raise NotImplementedError

    def _create_menu_bar(self):
        """ Entry point for creating the top menu bar """
        raise NotImplementedError

    def _create_splash_window(self):
        """ Entry point for creating and showing the load screen """
        raise NotImplementedError

    def _menu_add_action(self, menu, rx_value):
        """ Entry point for adding an action to a given menu

            Args:
                menu: The given menu.
                rx_value (RegisterAction): The value published by the subject.
        """
        raise NotImplementedError

    def _close_load_screen(self):
        """ Entry point for closing the load screen """
        raise NotImplementedError

    def _show(self):
        """ Entry point for showing main screen """
        raise NotImplementedError

    def _hide(self):
        """ Entry point for hiding main screen """
        raise NotImplementedError

    def _close(self, rx_value=None):
        """ Entry point for closing application

            Args:
                rx_value (Empty): The value published by the subject.
        """
        raise NotImplementedError

    def _start_event_loop(self):
        """
        Enters the main event loop and waits until close() is called.

        It is necessary to call this function to start event handling.The
        main event loop receives events from the window system and dispatches
        these to the application widgets.

        Generally, no user interaction can take place before calling
        start_event_loop().
        """
        raise NotImplementedError

    def _after(self, time_msec, action):
        """ Make the application perform an action after a time delay.

        Args:
            time_msec (int): The time in milliseconds to delay he action.
            action (function): The action to execute after time_msec delay.
        """
        raise NotImplementedError

    def _add_menu(self, menu_name):
        """Add a new top level menu in main window menu bar.

        Args:
            menu_name (str): The new menu name.

        Returns:
            tk.Menu: A reference to the newly created menu.
        """
        raise NotImplementedError
