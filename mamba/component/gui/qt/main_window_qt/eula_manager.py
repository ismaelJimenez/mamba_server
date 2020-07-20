############################################################################
#
# Copyright (c) Mamba Developers. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#
############################################################################

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
