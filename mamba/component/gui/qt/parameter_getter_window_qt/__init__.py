################################################################################################
##
##  Copyright (c) Mamba Developers. All rights reserved.
##  Licensed under the MIT License. See License.txt in the project root for license information.
##
################################################################################################

""" Parameter Getter window GUI Component """

import os
import time
from typing import List, Dict, Optional, Any

from rx import operators as op
from rx.subject import Subject
from rx.core.typing import Disposable

from PySide2.QtWidgets import QLabel, QWidget, QApplication, QComboBox, \
    QHBoxLayout, QMdiSubWindow, QPushButton, QTableWidget, QMenu, QVBoxLayout,\
    QAbstractItemView, QTableWidgetItem
from PySide2.QtCore import Qt, QCoreApplication
from PySide2.QtGui import QIcon, QCursor, QFont, QMouseEvent

from mamba.core.context import Context
from mamba.core.component_base import GuiPlugin
from mamba.component.gui.msg import RunAction
from mamba.core.msg import Empty, ServiceResponse, ParameterInfo, \
    ParameterType, ServiceRequest


class ParameterGetterTable(QTableWidget):
    def __init__(self, observed_services: Dict[tuple, int],
                 observer_modified: Subject, *args, **kwargs):
        QTableWidget.__init__(self, *args, **kwargs)
        self._observed_services = observed_services
        self._observer_modified = observer_modified

    def mousePressEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.RightButton:
            it = self.itemAt(event.pos())

            if it is not None:
                menu = QMenu(self)
                remove_action = menu.addAction("Remove")
                action = menu.exec_(QCursor.pos())

                if action == remove_action:

                    param_text = self.cellWidget(it.row(),
                                                 0).text().split(' -> ')
                    service = param_text[1]
                    provider = param_text[0]

                    self._observed_services[(provider, service)] -= 1

                    if self._observed_services[(provider, service)] == 0:
                        self._observed_services.pop((provider, service), None)
                        self._observer_modified.on_next(None)

                    self.removeRow(it.row())

        QTableWidget.mousePressEvent(self, event)


class ParameterGetterComponent(GuiPlugin):
    """ Parameter Getter window GUI Component in Qt5 """
    def __init__(self,
                 context: Context,
                 local_config: Optional[Dict[str, dict]] = None) -> None:

        self._observer_modified = Subject()

        super().__init__(os.path.dirname(__file__), context, local_config)

        # Define custom variables
        self._app: Optional[QCoreApplication] = None
        self._io_services: Dict[str, List[ParameterInfo]] = {}

        self._service_tables: List[ParameterGetterTable] = []
        self._observed_services: Dict[tuple, int] = {}
        self._io_result_subs: Optional[Disposable] = None

    def initialize(self) -> None:
        super().initialize()

        # Initialize custom variables
        self._app = QApplication(
            []) if QApplication.instance() is None else QApplication.instance(
            )

    def _register_observers(self) -> None:
        super()._register_observers()

        # Register to the topic provided by the io_controller services
        self._context.rx['io_service_signature'].subscribe(
            on_next=self._io_service_signature)

        self._observer_modified.subscribe(
            on_next=self._process_observer_modification)

    def run(self, rx_value: RunAction):
        """ Entry point for running the plugin

            Args:
                rx_value (RunAction): The value published by the subject.
        """
        perspective = rx_value.perspective

        window = QMdiSubWindow()
        window.setWindowTitle('Parameter Getter')
        self._context.rx['register_window'].on_next(window)

        child = QWidget()
        provider_label = QLabel("Provider:")
        provider_combo = QComboBox()

        service_label = QLabel("Service:")
        service_combo = QComboBox()

        for service, value in self._io_services.items():
            provider_combo.addItem(service)

        provider_combo.currentTextChanged.connect(
            lambda: self.generate_service_combobox(provider_combo,
                                                   service_combo))
        self.generate_service_combobox(provider_combo, service_combo)

        add_service_button = QPushButton("Add")
        add_service_button.setAutoDefault(False)
        add_service_button.setIcon(QIcon.fromTheme("list-add"))

        service_layout = QHBoxLayout()
        service_layout.addWidget(provider_label)
        service_layout.addWidget(provider_combo)
        service_layout.addWidget(service_label)
        service_layout.addWidget(service_combo)
        service_layout.addWidget(add_service_button)

        request_label = QLabel("Services:")
        services_table = ParameterGetterTable(self._observed_services,
                                              self._observer_modified)
        self._service_tables.append(services_table)
        services_table.setColumnCount(5)

        services_table.setHorizontalHeaderLabels(
            ["Service", "Description", "Measure", "Unit", "Stamp"])

        services_table.verticalHeader().setSectionsMovable(True)
        services_table.verticalHeader().setDragEnabled(True)
        services_table.verticalHeader().setDragDropMode(
            QAbstractItemView.InternalMove)

        add_service_button.clicked.connect(
            lambda: self.add_service(provider_combo.currentText(
            ), service_combo.currentText(), services_table))

        main_layout = QVBoxLayout()
        main_layout.addLayout(service_layout)
        main_layout.addWidget(request_label)
        main_layout.addWidget(services_table)

        child.setLayout(main_layout)

        window.setWidget(child)
        window.setAttribute(Qt.WA_DeleteOnClose)

        if perspective is not None:
            window.move(perspective['pos_x'], perspective['pos_y'])
            window.resize(perspective['width'], perspective['height'])

            for service_id in reversed(perspective['services']):
                param_id_split = service_id.split(' -> ')
                provider = param_id_split[0]
                param_id = param_id_split[1]

                if provider in self._io_services:
                    if len([
                            param for param in self._io_services[provider]
                            if param.id == param_id
                    ]) > 0:
                        self.add_service(provider, param_id, services_table)
        else:
            window.adjustSize()

        services_table.setColumnWidth(0, window.width() * 0.2)
        services_table.setColumnWidth(1, window.width() * 0.2)
        services_table.setColumnWidth(2, window.width() * 0.2)
        services_table.setColumnWidth(3, window.width() * 0.2)
        services_table.setColumnWidth(4, window.width() * 0.2)

        window.show()

        window.destroyed.connect(lambda: self.closeEvent(services_table))

        self._context.rx['generate_perspective'].subscribe(
            on_next=lambda _: self._generate_perspective(
                window, services_table))

    def generate_service_combobox(self, provider_combo: QComboBox,
                                  service_combo: QComboBox) -> None:
        service_combo.clear()

        for parameter_info in self._io_services.get(
                provider_combo.currentText(), []):
            service_combo.addItem(parameter_info.id)

    def call_service(self, provider_id: str, service_id: str) -> None:
        self._context.rx['tc'].on_next(
            ServiceRequest(provider=provider_id,
                           id=service_id,
                           args=[],
                           type=ParameterType.get))

    def add_service(self, provider: str, service: str,
                    services_table: ParameterGetterTable) -> None:
        if (service == '') or (provider == ''):
            return

        parameter_info = \
            [parameter_info for parameter_info in self._io_services[provider]
             if parameter_info.id == service][0]

        for row in range(0, services_table.rowCount()
                         ):  # Do not allow 2 services with same name
            if services_table.cellWidget(
                    row, 0).text() == f'{provider} -> {service}':
                return

        services_table.insertRow(0)

        service_btn = QPushButton(f'{provider} -> {service}')
        bold_font = QFont()
        bold_font.setBold(True)
        service_btn.setFont(bold_font)

        service_btn.clicked.connect(
            lambda: self.call_service(provider, service))

        description_item = QTableWidgetItem(parameter_info.description)
        description_item.setFlags(Qt.ItemIsEnabled)

        measured_value = QTableWidgetItem("N/A")
        measured_value.setFlags(Qt.ItemIsEnabled)
        measured_value.setTextAlignment(Qt.AlignCenter)

        units = QTableWidgetItem("-")
        units.setFlags(Qt.ItemIsEnabled)
        units.setTextAlignment(Qt.AlignCenter)

        stamp = QTableWidgetItem("N/A")
        stamp.setFlags(Qt.ItemIsEnabled)
        stamp.setTextAlignment(Qt.AlignCenter)

        font = QFont()
        font.setBold(True)

        services_table.setCellWidget(0, 0, service_btn)
        services_table.setItem(0, 1, description_item)
        services_table.setItem(0, 2, measured_value)
        services_table.item(0, 2).setBackground(Qt.black)
        services_table.item(0, 2).setForeground(Qt.green)
        services_table.item(0, 2).setFont(font)
        services_table.setItem(0, 3, units)
        services_table.setItem(0, 4, stamp)
        services_table.item(0, 4).setFont(font)
        services_table.item(0, 4).setForeground(Qt.darkGray)

        if self._observed_services.get((provider, service)) is None:
            self._observed_services[(provider, service)] = 1
            self._observer_modified.on_next(None)
        else:
            self._observed_services[(provider, service)] += 1

    def _generate_perspective(self, window: QMdiSubWindow,
                              services_table: ParameterGetterTable) -> None:
        perspective = {
            'menu_title': self._configuration['menu'],
            'action_name': self._configuration['name'],
            'data': {
                'pos_x': window.pos().x(),
                'pos_y': window.pos().y(),
                'width': window.size().width(),
                'height': window.size().height(),
                'services': []
            }
        }

        for row in range(0, services_table.rowCount()):
            perspective['data']['services'].append(
                services_table.cellWidget(row, 0).text())

        self._context.rx['component_perspective'].on_next(perspective)

    def _io_service_signature(self,
                              parameters_info: List[ParameterInfo]) -> None:
        """ Entry point for processing the service signatures.

            Args:
                signatures: The io service signatures dictionary.
        """
        self._io_services[parameters_info[0].provider] = [
            param for param in parameters_info
            if param.type == ParameterType.get
        ]

    def _process_observer_modification(self, rx_value: Any) -> None:
        if self._io_result_subs is not None:
            self._io_result_subs.dispose()
        self._io_result_subs = self._context.rx['io_result'].pipe(
            op.filter(lambda value: value.type == ParameterType.get and
                      (value.provider, value.id) in self._observed_services)
        ).subscribe(on_next=self._process_io_result)

    def _process_io_result(self, rx_value: ServiceResponse) -> None:
        for table in self._service_tables:
            for row in range(0, table.rowCount()):
                service_id = table.cellWidget(row, 0).text()
                if service_id == f'{rx_value.provider} -> {rx_value.id}':
                    table.item(table.visualRow(row),
                               2).setText(str(rx_value.value))
                    table.item(table.visualRow(row),
                               4).setText(str(time.time()))
                    if rx_value.type == 'error':
                        table.item(table.visualRow(row),
                                   2).setBackground(Qt.red)
                        table.item(table.visualRow(row),
                                   2).setForeground(Qt.black)
                    else:
                        table.item(table.visualRow(row),
                                   2).setBackground(Qt.black)
                        table.item(table.visualRow(row),
                                   2).setForeground(Qt.green)

    def closeEvent(self, services_table: ParameterGetterTable) -> None:
        for row in range(0, services_table.rowCount()):
            param_text = services_table.cellWidget(
                services_table.visualRow(row), 0).text().split(' -> ')
            service = param_text[1]
            provider = param_text[0]

            self._observed_services[(provider, service)] -= 1

            if self._observed_services[(provider, service)] == 0:
                self._observed_services.pop((provider, service), None)

        self._service_tables.remove(services_table)
        self._observer_modified.on_next(None)
