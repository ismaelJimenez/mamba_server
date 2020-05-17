""" The LoadScreen components enable showing an screen during load."""

import os

from mamba_server.components.component_base import ComponentBase


class MainWindowBase(ComponentBase):
    """ The LoadScreen components enable showing an screen during load."""
    def __init__(self, folder, context):
        super(MainWindowBase, self).__init__(folder, context)

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
