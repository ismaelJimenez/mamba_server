################################################################################################
##
##  Copyright (c) Mamba Developers. All rights reserved.
##  Licensed under the MIT License. See License.txt in the project root for license information.
##
################################################################################################

""" Plugin to show About message implemented in Qt5 """

import os
import pkgutil
from typing import Optional, Dict

from PySide2.QtWidgets import QMessageBox, QWidget, QApplication
from PySide2.QtGui import QIcon
from PySide2.QtCore import QCoreApplication

from mamba.core.context import Context
from mamba.core.component_base import GuiPlugin
from mamba.component.gui.msg import RunAction


class AboutComponent(GuiPlugin):
    """ Plugin to show About message implemented in Qt5 """
    def __init__(self,
                 context: Context,
                 local_config: Optional[Dict[str, dict]] = None) -> None:
        super().__init__(os.path.dirname(__file__), context, local_config)

        # Define custom variables
        self._version: str = ''
        self._box_message: str = ''
        self._app: Optional[QCoreApplication] = None

    def initialize(self) -> None:
        super().initialize()

        # Initialize custom variables
        self._app = QApplication(
            []) if QApplication.instance() is None else QApplication.instance(
            )

        version = pkgutil.get_data('mamba', 'VERSION')

        if version is not None:
            self._version = version.decode('ascii').strip()

        self._box_message = f"Mamba Server v{self._version}"

        if self._app is not None:
            self._app.setWindowIcon(
                QIcon(
                    os.path.join(self._context.get('mamba_dir'), 'artwork',
                                 'mamba_icon.png')))

    def run(self, rx_value: RunAction) -> None:
        """ Entry point for running the plugin

            Args:
                rx_value (RunAction): The value published by the subject.
        """
        def center(qt_widget):
            frame_gm = qt_widget.frameGeometry()
            screen = QApplication.desktop().screenNumber(
                QApplication.desktop().cursor().pos())
            center_point = QApplication.desktop().screenGeometry(
                screen).center()
            frame_gm.moveCenter(center_point)
            qt_widget.move(frame_gm.topLeft())

        widget = QWidget()
        center(widget)
        QMessageBox.about(widget, self._configuration['message_box_title'],
                          self._box_message)
