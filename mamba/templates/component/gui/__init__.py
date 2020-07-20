################################################################################################
##
##  Copyright (c) Mamba Developers. All rights reserved.
##  Licensed under the MIT License. See License.txt in the project root for license information.
##
################################################################################################

""" Custom Mamba Gui Component """

import os
import pkgutil
from typing import Optional, Dict

from PySide2.QtWidgets import QMessageBox, QWidget, QApplication
from PySide2.QtGui import QIcon
from PySide2.QtCore import QCoreApplication

from mamba.core.context import Context
from mamba.core.component_base import GuiPlugin
from mamba.component.gui.msg import RunAction


class CustomGuiComponent(GuiPlugin):
    """ Custom Mamba Gui Component """
    def __init__(self,
                 context: Context,
                 local_config: Optional[Dict[str, dict]] = None) -> None:
        super().__init__(os.path.dirname(__file__), context, local_config)

        # Define custom variables

    def initialize(self) -> None:
        super().initialize()

        # Initialize custom variables

    def run(self, rx_value: RunAction) -> None:
        """ Entry point for running the plugin

            Args:
                rx_value (RunAction): The value published by the subject.
        """
        pass
