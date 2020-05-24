""" Plugin to close Mamba Application """

import os

import time, threading
from PySide2.QtCore import QTimer
import json

from rx import operators as op

from PySide2.QtWidgets import QApplication, QWidget, QInputDialog, QLineEdit, QFileDialog

from mamba_server.components.plugins import PluginBase
from mamba_server.components.observable_types import Empty
from mamba_server.components.main.observable_types import RunAction


class Plugin(PluginBase):
    """ Plugin to close Main Window """
    def __init__(self, context, local_config=None):
        super(Plugin, self).__init__(os.path.dirname(__file__), context,
                                     local_config)

        self._perspectives = []

    def process_received_perspectived(self, perspectives_observer):
        perspectives_observer.dispose()

        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getSaveFileName(QWidget(), "Save Perspective", "",
                                                  "Perspective Files (*.json)", options=options)
        if fileName:
            if not '.json' in fileName:
                fileName = fileName + '.json'
            with open(fileName, 'w') as fout:
                json.dump(self._perspectives, fout)

    def initialize(self):
        super(Plugin, self).initialize()

        # Initialize custom variables
        self._app = QApplication(
            []) if QApplication.instance() is None else QApplication.instance(
            )

    def run(self, rx_value: RunAction):
        """ Entry point for running the plugin

            Args:
                rx_value (RunAction): The value published by the subject.
        """
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getOpenFileName(QWidget(), "Load Perspective", "",
                                                  "Perspective Files (*.json)", options=options)

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