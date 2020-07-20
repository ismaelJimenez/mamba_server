################################################################################################
##
##  Copyright (c) Mamba Developers. All rights reserved.
##  Licensed under the MIT License. See License.txt in the project root for license information.
##
################################################################################################

""" Plugin to close Mamba Application """

import os

from typing import Optional

from mamba.core.context import Context
from mamba.core.component_base import GuiPlugin
from mamba.core.msg import Empty
from mamba.component.gui.msg import RunAction


class QuitComponent(GuiPlugin):
    """ Plugin to close Main Window """
    def __init__(self,
                 context: Context,
                 local_config: Optional[dict] = None) -> None:
        super().__init__(os.path.dirname(__file__), context, local_config)

    def run(self, rx_value: RunAction) -> None:
        """ Entry point for running the plugin

            Args:
                rx_value (RunAction): The value published by the subject.
        """
        self._context.rx['quit'].on_next(Empty())
