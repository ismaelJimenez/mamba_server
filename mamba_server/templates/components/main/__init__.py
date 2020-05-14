""" Custom Main window """

import os

from mamba_server.components.gui.main_window.interface import \
    MainWindowInterface


class MainWindow(MainWindowInterface):
    """ Custom Main window """
    def __init__(self, context=None):
        super(MainWindow, self).__init__(os.path.dirname(__file__), context)

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
        raise NotImplementedError

    def show(self):
        """
        Entry point for showing main screen
        """
        raise NotImplementedError

    def hide(self):
        """
        Entry point for hiding main screen
        """
        raise NotImplementedError

    def close(self):
        """
        Entry point for closing main screen
        """
        raise NotImplementedError

    def start_event_loop(self):
        """
        Enters the main event loop and waits until close() is called.

        It is necessary to call this function to start event handling.The
        main event loop receives events from the window system and dispatches
        these to the application widgets.

        Generally, no user interaction can take place before calling
        start_event_loop().
        """
        raise NotImplementedError

    def after(self, time_msec, action):
        """ Make the application perform an action after a time delay.

        Args:
            time_msec (int): The time in milliseconds to delay he action.
            action (function): The action to execute after time_msec delay.
        """
        raise NotImplementedError
