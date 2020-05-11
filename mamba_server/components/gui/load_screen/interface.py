""" The LoadScreen components enable showing an screen during load.
"""

import os

from mamba_server.components.interface import ComponentInterface


class LoadScreenInterface(ComponentInterface):
    def __init__(self, folder, context):
        super(LoadScreenInterface, self).__init__(
            os.path.dirname(__file__),
            folder,
            context)

    def execute(self):
        """
        Entry point for running load screen
        """
        raise NotImplementedError

    def close(self):
        """
        Entry point for closing load screen
        """
        raise NotImplementedError

    def after(self, time_msec, action):
        """
        Entry point for performing an action after given milliseconds.
        """
        raise NotImplementedError

    def start_event_loop(self):
        """
        Entry point for starting event loop.
        """
        raise NotImplementedError
