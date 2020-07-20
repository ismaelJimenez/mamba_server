############################################################################
#
# Copyright (c) Mamba Developers. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#
############################################################################
""" Log window GUI Component """

import os
import time

from rx.core.typing import Disposable
from typing import Optional, Dict

from PySide2.QtWidgets import QLabel, QWidget, QApplication, QMdiSubWindow,\
    QTableWidget, QVBoxLayout, QGroupBox, QCheckBox, QTableWidgetItem
from PySide2.QtCore import Qt, QCoreApplication

from mamba.core.component_base import GuiPlugin
from mamba.component.gui.msg import RunAction
from mamba.core.msg import Log, LogLevel
from mamba.core.context import Context


class LogWindowComponent(GuiPlugin):
    """ Log window GUI Component in Qt5 """
    def __init__(self,
                 context: Context,
                 local_config: Optional[Dict[str, dict]] = None) -> None:
        super().__init__(os.path.dirname(__file__), context, local_config)

        # Define custom variables
        self._app: Optional[QCoreApplication] = None
        self._log_number = 1

    def initialize(self) -> None:
        super().initialize()

        # Initialize custom variables
        self._app = QApplication(
            []) if QApplication.instance() is None else QApplication.instance(
            )

    def run(self, rx_value: RunAction) -> None:
        """ Entry point for running the plugin

            Args:
                rx_value (RunAction): The value published by the subject.
        """
        perspective = rx_value.perspective

        window = QMdiSubWindow()
        window.setWindowTitle('Mamba Logger')
        self._context.rx['register_window'].on_next(window)

        child = QWidget()
        log_layout = QVBoxLayout()

        log_label = QLabel("Mamba Log:")
        log_table = QTableWidget()
        log_table.setColumnCount(5)
        log_table.setColumnWidth(0, int(window.width() * 0.3))
        log_table.setColumnWidth(1, int(window.width() * 1.2))
        log_table.setColumnWidth(2, int(window.width() * 1.2))
        log_table.setColumnWidth(3, int(window.width() * 1.2))
        log_table.setColumnWidth(4, int(window.width() * 1.2))
        log_table.setHorizontalHeaderLabels(
            ['#', 'Message', 'Severity', 'Node', 'Stamp'])

        log_layout.addWidget(log_label)
        log_layout.addWidget(log_table)

        group_box = QGroupBox('Exclude Messages:')
        debug_check_box = QCheckBox('Debug')
        info_check_box = QCheckBox('Info')
        error_check_box = QCheckBox('Error')
        critical_check_box = QCheckBox('Critical')

        group_box_layout = QVBoxLayout()
        group_box_layout.addWidget(debug_check_box)
        group_box_layout.addWidget(info_check_box)
        group_box_layout.addWidget(error_check_box)
        group_box_layout.addWidget(critical_check_box)
        group_box.setLayout(group_box_layout)

        main_layout = QVBoxLayout()
        main_layout.addLayout(log_layout)
        main_layout.addWidget(group_box)

        child.setLayout(main_layout)

        window.setWidget(child)
        window.setAttribute(Qt.WA_DeleteOnClose)

        if perspective is not None:
            window.move(perspective['pos_x'], perspective['pos_y'])
            window.resize(perspective['width'], perspective['height'])

            if perspective['exclude_debug']:
                debug_check_box.setChecked(True)

            if perspective['exclude_info']:
                info_check_box.setChecked(True)

            if perspective['exclude_error']:
                error_check_box.setChecked(True)

            if perspective['exclude_critical']:
                critical_check_box.setChecked(True)
        else:
            window.adjustSize()

        window.show()

        # Register to the topic provided by the io_controller services
        log_observer = self._context.rx['log'].subscribe(
            on_next=lambda _: self._received_log(
                _, log_table, debug_check_box, info_check_box, error_check_box,
                critical_check_box))

        generate_pers = self._context.rx['generate_perspective'].subscribe(
            on_next=lambda _: self._generate_perspective(
                window, debug_check_box, info_check_box, error_check_box,
                critical_check_box))

        window.destroyed.connect(
            lambda: self.closeEvent(log_observer, generate_pers))

    def _received_log(self, log: Log, log_table: QTableWidget,
                      debug_check_box: QCheckBox, info_check_box: QCheckBox,
                      error_check_box: QCheckBox,
                      critical_check_box: QCheckBox) -> None:
        """ Entry point for processing a new msg telecommand coming from the
            socket server.

            Args:
                log (Log): The log published by a component.
        """
        if (log.level == LogLevel.Dev and
            (debug_check_box.checkState() == Qt.Unchecked)) or \
                (log.level == LogLevel.Info
                 and (info_check_box.checkState() == Qt.Unchecked)) or \
                (log.level == LogLevel.Warning
                 and (error_check_box.checkState() == Qt.Unchecked)) or \
                (log.level == LogLevel.Error
                 and (critical_check_box.checkState() == Qt.Unchecked)):
            log_table.insertRow(0)
            log_table.setItem(0, 0,
                              QTableWidgetItem('#' + str(self._log_number)))
            log_table.setItem(0, 1, QTableWidgetItem(log.msg))
            log_table.setItem(0, 2, QTableWidgetItem(str(log.level)))
            log_table.setItem(0, 3, QTableWidgetItem(log.src))
            log_table.setItem(0, 4, QTableWidgetItem(str(time.time())))
            self._log_number += 1

    def closeEvent(self, log_observer: Disposable,
                   generate_pers: Disposable) -> None:
        log_observer.dispose()
        generate_pers.dispose()

    def _generate_perspective(self, window: QMdiSubWindow,
                              debug_check_box: QCheckBox,
                              info_check_box: QCheckBox,
                              error_check_box: QCheckBox,
                              critical_check_box: QCheckBox) -> None:
        perspective = {
            'menu_title': self._configuration['menu'],
            'action_name': self._configuration['name'],
            'data': {
                'pos_x': window.pos().x(),
                'pos_y': window.pos().y(),
                'width': window.size().width(),
                'height': window.size().height(),
                'exclude_debug': debug_check_box.checkState() == Qt.Checked,
                'exclude_info': info_check_box.checkState() == Qt.Checked,
                'exclude_error': error_check_box.checkState() == Qt.Checked,
                'exclude_critical':
                critical_check_box.checkState() == Qt.Checked
            }
        }

        self._context.rx['component_perspective'].on_next(perspective)
