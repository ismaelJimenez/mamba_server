""" Plugin to show About message implemented in TkInter """

import os
import pkgutil

import tkinter as tk
from tkinter import messagebox

from mamba_server.components.plugins import PluginBase
from mamba_server.components.main.observable_types.run_action \
    import RunAction


class Plugin(PluginBase):
    """ Plugin to show About message implemented in TkInter """
    def __init__(self, context, local_config=None):
        super(Plugin, self).__init__(os.path.dirname(__file__), context,
                                     local_config)

        # Define custom variables
        self._version = None
        self._box_message = None

    def initialize(self):
        super(Plugin, self).initialize()

        # Initialize custom variables
        self._version = pkgutil.get_data('mamba_server',
                                         'VERSION').decode('ascii').strip()
        self._box_message = f"Mamba Server v{self._version}"

    def run(self, rx_value):
        """ Entry point for running the plugin

            Args:
                rx_value (RunAction): The value published by the subject.
        """
        app = tk.Tk()
        app.overrideredirect(1)
        app.withdraw()

        messagebox.showinfo(self._configuration['message_box_title'],
                            self._box_message)
