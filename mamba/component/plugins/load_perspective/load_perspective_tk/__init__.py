""" Plugin to close Mamba Application """

import os
import json

from tkinter.filedialog import askopenfilename

from mamba.component.plugins import PluginBase
from mamba.component.gui.msg import RunAction


class Plugin(PluginBase):
    """ Plugin to close Main Window """
    def __init__(self, context, local_config=None):
        super(Plugin, self).__init__(os.path.dirname(__file__), context,
                                     local_config)

        self._perspectives = []

    def initialize(self):
        super(Plugin, self).initialize()

    def run(self, rx_value: RunAction):
        """ Entry point for running the plugin

            Args:
                rx_value (RunAction): The value published by the subject.
        """
        import tkinter as tk
        self._app = tk.Tk()
        self._app.overrideredirect(1)
        self._app.withdraw()

        fileName = askopenfilename(title="Load Perspective",
                                   defaultextension=".json",
                                   filetypes=[("perspective", "*.json")])

        if fileName:
            with open(fileName, "r") as read_file:
                profiles = json.load(read_file)
                for profile in profiles:
                    print(profile)

                    self._context.rx['run_plugin'].on_next(
                        RunAction(menu_title=profile['menu_title'],
                                  action_name=profile['action_name'],
                                  perspective=profile['data']))

    def _process_component_perspective(self, perspective: dict):
        self._perspectives.append(perspective)
