################################################################################################
##
##  Copyright (c) Mamba Developers. All rights reserved.
##  Licensed under the MIT License. See License.txt in the project root for license information.
##
################################################################################################

import os
import yaml

from PySide2.QtWidgets import QWidget, QDialog, QHBoxLayout, QPushButton, \
    QVBoxLayout, QTextEdit, QToolBox, QGridLayout, QToolButton, QLabel, QApplication,\
    QButtonGroup, QFileDialog, QMessageBox

from PySide2.QtGui import QIcon
from PySide2.QtCore import QSize
from PySide2 import QtCore

from mamba.core.utils import copytree


class MarketComponentDialog(QDialog):
    def __init__(self, mamba_dir, marketplace_dir, parent):
        super().__init__(parent)

        self.parent = parent

        self.resize(800, 600)

        self.setWindowTitle("Marketplace")

        self.description_text = QTextEdit()
        self.description_text.setReadOnly(True)

        self.download_button = QPushButton("Download")
        self.download_button.setEnabled(False)
        self.close_button = QPushButton("Close")

        self.cell_button_group = QButtonGroup()
        self.cell_button_group.buttonClicked.connect(self.cell_button_group_clicked)

        self.toolBox = QToolBox()

        toolboxes_list = [x for x in os.listdir(marketplace_dir) if '.py' not in x and '__' not in x]

        self.component_name_mapping = {}

        for toolbox in toolboxes_list:
            components_list = [x for x in os.listdir(os.path.join(marketplace_dir, toolbox)) if '.py' not in x and '__pycache__' not in x]

            toolbox_layout = QGridLayout()

            index = 0

            for component in components_list:
                self.component_name_mapping[component.replace('_', ' ').title()] = os.path.join(marketplace_dir, toolbox, component)
                toolbox_layout.addWidget(self.create_cell_widget(component.replace('_', ' ').title(),
                                                                 os.path.join(mamba_dir, 'artwork', 'plugin.png')), int(index/2), index%2)
                index += 1

            toolbox_layout.setRowStretch(2, 10)
            toolbox_layout.setColumnStretch(2, 10)

            toolbox_widget = QWidget()
            toolbox_widget.setLayout(toolbox_layout)

            self.toolBox.addItem(toolbox_widget, toolbox.replace('_', ' ').title())

        # Create layout and add widgets

        toolbox_detail_layout = QHBoxLayout()

        toolbox_detail_layout.addWidget(self.toolBox)
        toolbox_detail_layout.addWidget(self.description_text)

        layout = QVBoxLayout()

        button_layout = QHBoxLayout()

        button_layout.addWidget(self.download_button)
        button_layout.addWidget(self.close_button)

        layout.addLayout(toolbox_detail_layout)
        layout.addLayout(button_layout)

        # Set dialog layout

        self.setLayout(layout)

        # Add button signal to greetings slot

        self.download_button.clicked.connect(self.download_button_clicked)
        self.close_button.clicked.connect(self.accept)

        self.center()

    def download_button_clicked(self):
        dir = QFileDialog.getExistingDirectory(QWidget(), 'Download Component',
                                               os.getcwd(),
                                               QFileDialog.ShowDirsOnly
                                               | QFileDialog.DontResolveSymlinks)
        if dir:
            component_name = os.path.basename(self.component_name_mapping[self.selected_item])
            target_dir = os.path.join(dir, os.path.basename(self.component_name_mapping[self.selected_item]))

            if os.path.exists(target_dir):
                QMessageBox.warning(self, 'Mamba Component Download ERROR',
                                  f'Folder {target_dir} already exists.')
            else:
                copytree(self.component_name_mapping[self.selected_item],
                                  os.path.join(dir, component_name))

                QMessageBox.about(self, 'Mamba Component Download',
                                  f'Component {component_name} downloaded successfully to:\n'
                                  f' {target_dir}')

    def cell_button_group_clicked(self, button):
        self.download_button.setEnabled(True)
        self.download_button.setStyleSheet("background-color: green")

        buttons = self.cell_button_group.buttons()
        for myButton in buttons:
            if myButton != button:
                button.setChecked(False)

        self.selected_item = button.text()

        dir = self.component_name_mapping[self.selected_item]

        with open(os.path.join(dir, 'config.yml')) as file:
            compose_config = yaml.load(file, Loader=yaml.FullLoader)

            component_description = \
                f'<b>Description</b>: {compose_config["name"]}<br><br>' \
                f'<b>Version</b>: {compose_config["version"]}<br><br>' \
                f'<b>Status</b>: {compose_config["status"]}<br><br>' \
                f'<b>Maintainer</b>: {compose_config["maintainer"]}<br><br>' \
                f'<b>Maintainer Email</b>: {compose_config["maintainer_email"]}<br><br>'

            self.description_text.setText(component_description)

    def create_cell_widget(self, text, image):
        button = QToolButton()
        button.setText(text)
        button.setIcon(QIcon(image))
        button.setIconSize(QSize(50, 50))
        button.setCheckable(True)
        self.cell_button_group.addButton(button)

        layout = QGridLayout()
        layout.addWidget(button, 0, 0, QtCore.Qt.AlignHCenter)
        layout.addWidget(QLabel(text), 1, 0, QtCore.Qt.AlignCenter)

        widget = QWidget()
        widget.setLayout(layout)

        return widget

    def center(self):
        frame_gm = self.frameGeometry()
        screen = QApplication.desktop().screenNumber(
            QApplication.desktop().cursor().pos())
        center_point = QApplication.desktop().screenGeometry(
            screen).center()
        frame_gm.moveCenter(center_point)
        self.move(frame_gm.topLeft())
