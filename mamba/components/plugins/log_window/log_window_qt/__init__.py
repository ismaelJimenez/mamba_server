""" Plugin to show About message implemented in Qt5 """

import os
import time

from rx import operators as op

from PySide2.QtWidgets import QLabel, QWidget, QApplication, QMdiSubWindow,\
    QTableWidget, QVBoxLayout, QGroupBox, QCheckBox, QTableWidgetItem
from PySide2.QtCore import Qt

from mamba.components.plugins import PluginBase
from mamba.components.main.observable_types import RunAction
from mamba.core.msg import Empty, Log, LogLevel


class Plugin(PluginBase):
    """ Plugin to show About message implemented in Qt5 """
    def __init__(self, context, local_config=None):
        # Define custom variables
        self._app = None
        self._log_numer = 1

        self._new_window_observer = None

        super(Plugin, self).__init__(os.path.dirname(__file__), context,
                                     local_config)

    def _received_log(self, log: Log, log_table, debugCheckBox, infoCheckBox,
                      errorCheckBox, criticalCheckBox):
        """ Entry point for processing a new msg telecommand coming from the
            socket server.

            Args:
                raw_tc (Log): The msg telecommand coming from
                                         the socket.
        """
        if (log.level == LogLevel.Dev and
            (debugCheckBox.checkState() == Qt.Unchecked)) or \
                (log.level == LogLevel.Info
                 and (infoCheckBox.checkState() == Qt.Unchecked)) or \
                (log.level == LogLevel.Warning
                 and (errorCheckBox.checkState() == Qt.Unchecked)) or \
                (log.level == LogLevel.Error
                 and (criticalCheckBox.checkState() == Qt.Unchecked)):
            log_table.insertRow(0)
            log_table.setItem(0, 0,
                              QTableWidgetItem('#' + str(self._log_numer)))
            log_table.setItem(0, 1, QTableWidgetItem(log.msg))
            log_table.setItem(0, 2, QTableWidgetItem(str(log.level)))
            log_table.setItem(0, 3, QTableWidgetItem(log.src))
            log_table.setItem(0, 4, QTableWidgetItem(str(time.time())))
            self._log_numer += 1

        print(f'WINDOW: [{log.level}] [{log.src}] {log.msg}')

    def _new_window(self, window: QMdiSubWindow, perspective):
        self._new_window_observer.dispose()

        child = QWidget()
        logLayout = QVBoxLayout()
        excludeMessageLayout = QVBoxLayout()

        logLabel = QLabel("Mamba Log:")
        log_table = QTableWidget()
        log_table.setColumnCount(5)
        log_table.setColumnWidth(0, window.width() * 0.3)
        log_table.setColumnWidth(1, window.width() * 1.2)
        log_table.setColumnWidth(2, window.width() * 1.2)
        log_table.setColumnWidth(3, window.width() * 1.2)
        log_table.setColumnWidth(4, window.width() * 1.2)
        log_table.setHorizontalHeaderLabels(
            ["#", "Message", "Severity", "Node", "Stamp"])

        logLayout.addWidget(logLabel)
        logLayout.addWidget(log_table)

        groupBox = QGroupBox("Exclude Messages:")
        debugCheckBox = QCheckBox("Debug")
        infoCheckBox = QCheckBox("Info")
        errorCheckBox = QCheckBox("Error")
        criticalCheckBox = QCheckBox("Critical")

        groupBoxLayout = QVBoxLayout()
        groupBoxLayout.addWidget(debugCheckBox)
        groupBoxLayout.addWidget(infoCheckBox)
        groupBoxLayout.addWidget(errorCheckBox)
        groupBoxLayout.addWidget(criticalCheckBox)
        groupBox.setLayout(groupBoxLayout)

        mainLayout = QVBoxLayout()
        mainLayout.addLayout(logLayout)
        mainLayout.addWidget(groupBox)

        child.setLayout(mainLayout)

        window.setWidget(child)
        window.setAttribute(Qt.WA_DeleteOnClose)

        if perspective is not None:
            window.move(perspective['pos_x'], perspective['pos_y'])
            window.resize(perspective['width'], perspective['height'])

            if perspective['exclude_debug']:
                debugCheckBox.setChecked(True)

            if perspective['exclude_info']:
                infoCheckBox.setChecked(True)

            if perspective['exclude_error']:
                errorCheckBox.setChecked(True)

            if perspective['exclude_critical']:
                criticalCheckBox.setChecked(True)
        else:
            window.adjustSize()

        window.show()

        # Register to the topic provided by the io_controller services
        log_observer = self._context.rx['log'].pipe(
            op.filter(lambda value: isinstance(value, Log))).subscribe(
                on_next=lambda _: self._received_log(
                    _, log_table, debugCheckBox, infoCheckBox, errorCheckBox,
                    criticalCheckBox))

        window.destroyed.connect(lambda: self.closeEvent(log_observer))

        self._context.rx['generate_perspective'].pipe(
            op.filter(lambda value: isinstance(value, Empty))).subscribe(
                on_next=lambda _: self._generate_perspective(
                    window, debugCheckBox, infoCheckBox, errorCheckBox,
                    criticalCheckBox))

    def _generate_perspective(self, window: QMdiSubWindow, debugCheckBox,
                              infoCheckBox, errorCheckBox, criticalCheckBox):
        perspective = {
            'menu_title': self._configuration['menu'],
            'action_name': self._configuration['name'],
            'data': {
                'pos_x': window.pos().x(),
                'pos_y': window.pos().y(),
                'width': window.size().width(),
                'height': window.size().height(),
                'exclude_debug': debugCheckBox.checkState() == Qt.Checked,
                'exclude_info': infoCheckBox.checkState() == Qt.Checked,
                'exclude_error': errorCheckBox.checkState() == Qt.Checked,
                'exclude_critical': criticalCheckBox.checkState() == Qt.Checked
            }
        }

        self._context.rx['component_perspective'].on_next(perspective)

    def closeEvent(self, log_observer):
        log_observer.dispose()

    def initialize(self):
        super(Plugin, self).initialize()

        # Initialize custom variables
        self._app = QApplication(
            []) if QApplication.instance() is None else QApplication.instance(
            )

    def run(self, rx_value: RunAction):
        """ Entry point for running the plugin

            Args:
                rx_value (RunAction): The value published by the subject.
        """
        # Generate_window is received to generate a new MDI window
        self._new_window_observer = self._context.rx['new_window_widget'].pipe(
            op.filter(lambda value: isinstance(value, QMdiSubWindow))
        ).subscribe(
            on_next=lambda _: self._new_window(_, rx_value.perspective))

        self._context.rx['new_window'].on_next(Empty())
