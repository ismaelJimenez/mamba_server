""" The LoadScreen components enable showing an screen during load."""

import os

from mamba_server.components.interface import ComponentInterface


class MainWindowInterface(ComponentInterface):
    """ The LoadScreen components enable showing an screen during load."""
    def __init__(self, folder, context):
        super(MainWindowInterface, self).__init__(os.path.dirname(__file__),
                                                  folder, context)

    def register_action(self,
                        menu_title,
                        action_name,
                        component_action,
                        shortcut='',
                        status_tip=''):
        """
        Entry point for registering a new action inside a given menu.
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
        Entry point for starting main window event loop.
        """
        raise NotImplementedError

    def after(self, time_msec, action):
        """
        Entry point for performing an action after given milliseconds.
        """
        raise NotImplementedError
