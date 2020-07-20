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

from PySide2.QtWidgets import QDialog, QHBoxLayout, QPushButton, QVBoxLayout, QTextEdit


class EulaDialog(QDialog):
    def __init__(self, eula_file_path, parent):
        super().__init__(parent)

        self.parent = parent

        self.resize(800, 600)

        self.setWindowTitle("License Agreements and Service Terms")

        self.eula_text = QTextEdit()
        self.eula_text.setReadOnly(True)

        file = open(eula_file_path, 'r')

        self.eula_text.setText(file.read())

        self.accept_button = QPushButton("Accept")
        self.accept_button.setStyleSheet("background-color: green")
        self.decline_button = QPushButton("Decline")

        # Create layout and add widgets

        layout = QVBoxLayout()

        layout.addWidget(self.eula_text)

        button_layout = QHBoxLayout()

        button_layout.addWidget(self.decline_button)
        button_layout.addWidget(self.accept_button)

        layout.addLayout(button_layout)

        # Set dialog layout

        self.setLayout(layout)

        # Add button signal to greetings slot

        self.accept_button.clicked.connect(self.accept)
        self.decline_button.clicked.connect(self.reject)


class EulaManager:
    def __init__(self, eula_file_path, main_window):
        self.eula_file_path = eula_file_path
        self.main_window = main_window

    def run(self):
        eula = EulaDialog(self.eula_file_path, self.main_window)
        return eula.exec_()
