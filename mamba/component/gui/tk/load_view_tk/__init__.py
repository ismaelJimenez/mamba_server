#############################################################################
##
## Copyright (C) 2020 The Mamba Company.
## Contact: themambacompany@gmail.com
##
## This file is part of Mamba Server.
##
## $MAMBA_BEGIN_LICENSE:LGPL$
## Commercial License Usage
## Licensees holding valid commercial Mamba licenses may use this file in
## accordance with the commercial license agreement provided with the
## Software or, alternatively, in accordance with the terms contained in
## a written agreement between you and The Mamba Company. For licensing terms
## and conditions see LICENSE. For further information contact us at
## themambacompany@gmail.com.
##
## GNU Lesser General Public License Usage
## Alternatively, this file may be used under the terms of the GNU Lesser
## General Public License version 3 as published by the Free Software
## Foundation and appearing in the file LICENSE.LGPL3 included in the
## packaging of this file. Please review the following information to
## ensure the GNU Lesser General Public License version 3 requirements
## will be met: https://www.gnu.org/licenses/lgpl-3.0.html.
##
## GNU General Public License Usage
## Alternatively, this file may be used under the terms of the GNU
## General Public License version 2.0 or (at your option) the GNU General
## Public license version 3 or any later version approved by the KDE Free
## Qt Foundation. The licenses are as published by the Free Software
## Foundation and appearing in the file LICENSE.GPL2 and LICENSE.GPL3
## included in the packaging of this file. Please review the following
## information to ensure the GNU General Public License requirements will
## be met: https://www.gnu.org/licenses/gpl-2.0.html and
## https://www.gnu.org/licenses/gpl-3.0.html.
##
## $MAMBA_END_LICENSE$
##
#############################################################################

""" Load view component """

import os
import json

from typing import Optional, Dict, Any
from tkinter.filedialog import askopenfilename
import tkinter as tk

from mamba.core.component_base import GuiPlugin
from mamba.component.gui.msg import RunAction
from mamba.core.context import Context


class LoadViewComponent(GuiPlugin):
    """ Load view component in Tk """
    def __init__(self,
                 context: Context,
                 local_config: Optional[Dict[str, dict]] = None) -> None:
        super().__init__(os.path.dirname(__file__), context, local_config)

        self._app: Optional[tk.Tk] = None
        self._views = []

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
        self._app = tk.Tk()
        self._app.overrideredirect(1)
        self._app.withdraw()

        file_name = askopenfilename(title="Load View",
                                    defaultextension=".json",
                                    filetypes=[("perspective", "*.json")])

        if file_name:
            with open(file_name, "r") as read_file:
                self.publish_views(json.load(read_file))
