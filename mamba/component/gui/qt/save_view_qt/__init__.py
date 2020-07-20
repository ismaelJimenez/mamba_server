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

""" Save view component """

import os
import json

from rx.core.typing import Disposable

from typing import Optional, Dict, Any
from PySide2.QtWidgets import QApplication, QWidget, QFileDialog
from PySide2.QtCore import QCoreApplication, QTimer

from mamba.core.component_base import GuiPlugin
from mamba.component.gui.msg import RunAction
from mamba.core.msg import Empty
from mamba.core.context import Context


class SaveViewComponent(GuiPlugin):
    """ Save view component in Qt5 """
    def __init__(self,
                 context: Context,
                 local_config: Optional[Dict[str, dict]] = None) -> None:
        super().__init__(os.path.dirname(__file__), context, local_config)

        # Define custom variables
        self._app: Optional[QCoreApplication] = None
        self._views = []

    def initialize(self) -> None:
        super().initialize()

        # Initialize custom variables
        self._app = QApplication(
            []) if QApplication.instance() is None else QApplication.instance(
            )

    def save_views(self, file_name: str) -> None:
        if '.json' not in file_name:
            file_name = file_name + '.json'
        with open(file_name, 'w') as fout:
            json.dump(self._views, fout)

    def process_received_view(self, perspectives_observer: Disposable) -> None:
        perspectives_observer.dispose()

        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        file_name, _ = QFileDialog.getSaveFileName(QWidget(),
                                                   "Save View",
                                                   "",
                                                   "View Files (*.json)",
                                                   options=options)
        if file_name:
            self.save_views(file_name)

    def run(self, rx_value: RunAction) -> None:
        """ Entry point for running the plugin

            Args:
                rx_value (RunAction): The value published by the subject.
        """
        self._views = []

        perspectives_observer = self._context.rx[
            'component_perspective'].subscribe(
                on_next=self._process_component_perspective)

        QTimer.singleShot(
            int(1000),
            lambda: self.process_received_view(perspectives_observer))

        self._context.rx['generate_perspective'].on_next(Empty())

    def _process_component_perspective(self, perspective: Dict[str,
                                                               Any]) -> None:
        self._views.append(perspective)
