################################################################################################
##
##  Copyright (c) Mamba Developers. All rights reserved.
##  Licensed under the MIT License. See License.txt in the project root for license information.
##
################################################################################################

""" Plugin to show About message implemented in TkInter """

import os
import pkgutil
from typing import Optional, Dict

import tkinter as tk
from tkinter import messagebox

from mamba.core.context import Context
from mamba.core.component_base import GuiPlugin
from mamba.component.gui.msg import RunAction


class AboutComponent(GuiPlugin):
    """ Plugin to show About message implemented in TkInter """
    def __init__(self,
                 context: Context,
                 local_config: Optional[Dict[str, dict]] = None) -> None:
        super().__init__(os.path.dirname(__file__), context, local_config)

        # Define custom variables
        self._version: str = ''
        self._box_message: str = ''

    def initialize(self) -> None:
        super().initialize()

        # Initialize custom variables
        version = pkgutil.get_data('mamba', 'VERSION')

        if version is not None:
            self._version = version.decode('ascii').strip()

        self._box_message = f"Mamba Server v{self._version}"

    def run(self, rx_value: RunAction) -> None:
        """ Entry point for running the plugin

            Args:
                rx_value (RunAction): The value published by the subject.
        """
        app = tk.Tk()
        app.overrideredirect(1)
        app.withdraw()

        messagebox.showinfo(self._configuration['message_box_title'],
                            self._box_message)
