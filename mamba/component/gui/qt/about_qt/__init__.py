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
