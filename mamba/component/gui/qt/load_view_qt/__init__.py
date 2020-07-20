############################################################################
#
# Copyright (c) Mamba Developers. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#
############################################################################
""" Load view component """

import os
import json

from typing import Optional, Dict, Any
from PySide2.QtWidgets import QApplication, QWidget, QFileDialog
from PySide2.QtCore import QCoreApplication

from mamba.core.component_base import GuiPlugin
from mamba.component.gui.msg import RunAction
from mamba.core.context import Context


class LoadViewComponent(GuiPlugin):
    """ Load view component in Qt5 """
    def __init__(self,
                 context: Context,
                 local_config: Optional[Dict[str, dict]] = None) -> None:
        super().__init__(os.path.dirname(__file__), context, local_config)

        # Define custom variables
        self._app: Optional[QCoreApplication] = None

    def initialize(self):
        super().initialize()

        # Initialize custom variables
        self._app = QApplication(
            []) if QApplication.instance() is None else QApplication.instance(
            )

    def publish_views(self, profiles: Dict[str, Any]) -> None:
        for profile in profiles:
            self._context.rx['run_plugin'].on_next(
                RunAction(menu_title=profile['menu_title'],
                          action_name=profile['action_name'],
                          perspective=profile['data']))

    def run(self, rx_value: RunAction) -> None:
        """ Entry point for running the plugin

            Args:
                rx_value (RunAction): The value published by the subject.
        """
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        file_name, _ = QFileDialog.getOpenFileName(QWidget(),
                                                   "Load View",
                                                   "",
                                                   "View Files (*.json)",
                                                   options=options)

        if file_name:
            with open(file_name, "r") as read_file:
                self.publish_views(json.load(read_file))
