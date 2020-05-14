""" Custom Load screen """

import os

from mamba_server.components.gui.load_screen.interface import \
    LoadScreenInterface


class LoadScreen(LoadScreenInterface):
    """ Custom Load screen """
    def __init__(self, context=None):
        super(LoadScreen, self).__init__(os.path.dirname(__file__), context)

    def show(self):
        """
        Entry point for showing load screen
        """
        raise NotImplementedError

    def hide(self):
        """
        Entry point for hiding load screen
        """
        raise NotImplementedError

    def close(self):
        """
        Entry point for closing load screen
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
