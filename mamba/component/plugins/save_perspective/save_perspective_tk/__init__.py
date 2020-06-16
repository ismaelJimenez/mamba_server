""" Plugin to close Mamba Application """

import os

# from PySide2.QtCore import QTimer
import json

# from PySide2.QtWidgets import QApplication, QWidget, QFileDialog
import tkinter as tk
from tkinter.filedialog import asksaveasfilename

from mamba.core.component_base import GuiPlugin
from mamba.core.msg import Empty
from mamba.component.gui.msg import RunAction


class Plugin(GuiPlugin):
    """ Plugin to close Main Window """
    def __init__(self, context, local_config=None):
        super(Plugin, self).__init__(os.path.dirname(__file__), context,
                                     local_config)

        self._perspectives = []

    def process_received_perspectived(self, perspectives_observer):
        perspectives_observer.dispose()

        fileName = asksaveasfilename(title="Save View",
                                     defaultextension=".json",
                                     filetypes=[("perspective", "*.json")])
        if fileName:
            if '.json' not in fileName:
                fileName = fileName + '.json'
            with open(fileName, 'w') as fout:
                json.dump(self._perspectives, fout)

    def initialize(self):
        super(Plugin, self).initialize()

    def run(self, rx_value: RunAction):
        """ Entry point for running the plugin

            Args:
                rx_value (RunAction): The value published by the subject.
        """
        self._perspectives = []

        perspectives_observer = self._context.rx[
            'component_perspective'].subscribe(
                on_next=self._process_component_perspective)

        self._app = tk.Tk()
        self._app.overrideredirect(1)
        self._app.withdraw()

        self._app.after(
            int(1000),
            lambda: self.process_received_perspectived(perspectives_observer))

        self._context.rx['generate_perspective'].on_next(Empty())
        print("Sent generate perspective")

    def _process_component_perspective(self, perspective: dict):
        self._perspectives.append(perspective)
