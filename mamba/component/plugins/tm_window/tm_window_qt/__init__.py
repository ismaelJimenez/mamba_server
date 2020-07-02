""" Plugin to show About message implemented in Qt5 """

import os
import time
from typing import List, Dict

from rx import operators as op
from rx.subject import Subject

from PySide2.QtWidgets import QLabel, QWidget, QApplication, QComboBox, \
    QHBoxLayout, QMdiSubWindow, QPushButton, QTableWidget, QMenu, QVBoxLayout,\
    QAbstractItemView, QTableWidgetItem
from PySide2.QtCore import Qt
from PySide2.QtGui import QIcon, QCursor, QFont

from mamba.core.component_base import GuiPlugin
from mamba.component.gui.msg import RunAction
from mamba.core.msg import Empty, ServiceResponse, ParameterInfo, \
    ParameterType, ServiceRequest


class CustomTable(QTableWidget):
    def __init__(self, parent, *args, **kwargs):
        QTableWidget.__init__(self, *args, **kwargs)
        self.parent = parent

    def mousePressEvent(self, event):
        print('PRESS EVENT')
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

                    self.parent._observed_services[(provider, service)] -= 1

                    if self.parent._observed_services[(provider,
                                                       service)] == 0:
                        self.parent._observed_services.pop((provider, service),
                                                           None)
                        self.parent._observer_modified.on_next(None)

                    self.removeRow(it.row())

        QTableWidget.mousePressEvent(self, event)


class Plugin(GuiPlugin):
    """ Plugin to show About message implemented in Qt5 """
    def __init__(self, context, local_config=None):
        # Define custom variables
        self._app = None
        self._io_services: Dict[str, List[ParameterInfo]] = {}
        self._service_tables = []
        self._observed_services = {}

        self._observer_modified = Subject()
        self._io_result_subs = None

        super().__init__(os.path.dirname(__file__), context, local_config)

    def _register_observers(self):
        super()._register_observers()

        # Register to the topic provided by the io_controller services
        self._context.rx['io_service_signature'].subscribe(
            on_next=self._io_service_signature)

        self._observer_modified.subscribe(
            on_next=self._process_observer_modification)

    def _process_observer_modification(self, rx_value):
        if self._io_result_subs is not None:
            self._io_result_subs.dispose()

        self._io_result_subs = self._context.rx['io_result'].pipe(
            op.filter(lambda value: value.type == ParameterType.get and
                      (value.provider, value.id) in self._observed_services)
        ).subscribe(on_next=self._process_io_result)

    def _process_io_result(self, rx_value: ServiceResponse):
        print('IO RESULT')

        parameter_text = f'{rx_value.provider} -> {rx_value.id}'

        for table in self._service_tables:
            for row in range(0, table.rowCount()):
                service_id = table.cellWidget(row, 0).text()
                if service_id == parameter_text:
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

    def generate_service_combobox(self, providerCombo, serviceCombo):
        serviceCombo.clear()

        for parameter_info in self._io_services[providerCombo.currentText()]:
            serviceCombo.addItem(parameter_info.id)

    def call_service(self, provider_id, service_id, services_table):
        self._context.rx['tc'].on_next(
            ServiceRequest(provider=provider_id,
                           id=service_id,
                           args=[],
                           type=ParameterType.get))

    def add_service(self, provider, service, services_table):
        parameter_info = \
            [parameter_info for parameter_info in self._io_services[provider]
             if parameter_info.id == service][0]

        parameter_text = f'{provider} -> {service}'

        if (service == '') or (provider == ''):
            return

        for row in range(0, services_table.rowCount()
                         ):  # Do not allow 2 services with same name
            if services_table.cellWidget(row, 0).text() == parameter_text:
                return

        services_table.insertRow(0)

        service_btn = QPushButton(f'{provider} -> {service}')
        bold_font = QFont()
        bold_font.setBold(True)
        service_btn.setFont(bold_font)

        service_btn.clicked.connect(
            lambda: self.call_service(provider, service, services_table))

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

    def _new_window(self, perspective):
        window = QMdiSubWindow()
        self._context.rx['register_window'].on_next(window)
        window.setWindowTitle('Parameter Getter')

        child = QWidget()
        providerLabel = QLabel("Provider:")
        providerCombo = QComboBox()

        serviceLabel = QLabel("Service:")
        serviceCombo = QComboBox()

        for service, value in self._io_services.items():
            providerCombo.addItem(service)

        providerCombo.currentTextChanged.connect(
            lambda: self.generate_service_combobox(providerCombo, serviceCombo
                                                   ))
        self.generate_service_combobox(providerCombo, serviceCombo)

        addServiceButton = QPushButton("Add")
        addServiceButton.setAutoDefault(False)
        addServiceButton.setIcon(QIcon.fromTheme("list-add"))

        serviceLayout = QHBoxLayout()
        serviceLayout.addWidget(providerLabel)
        serviceLayout.addWidget(providerCombo)
        serviceLayout.addWidget(serviceLabel)
        serviceLayout.addWidget(serviceCombo)
        serviceLayout.addWidget(addServiceButton)

        requestLabel = QLabel("Services:")
        services_table = CustomTable(self)
        self._service_tables.append(services_table)
        services_table.setColumnCount(5)

        services_table.setHorizontalHeaderLabels(
            ["Service", "Description", "Measure", "Unit", "Stamp"])

        services_table.verticalHeader().setSectionsMovable(True)
        services_table.verticalHeader().setDragEnabled(True)
        services_table.verticalHeader().setDragDropMode(
            QAbstractItemView.InternalMove)

        addServiceButton.clicked.connect(
            lambda: self.add_service(providerCombo.currentText(
            ), serviceCombo.currentText(), services_table))

        mainLayout = QVBoxLayout()
        mainLayout.addLayout(serviceLayout)
        mainLayout.addWidget(requestLabel)
        mainLayout.addWidget(services_table)

        child.setLayout(mainLayout)

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

    def _generate_perspective(self, window: QMdiSubWindow, services_table):
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

        print(perspective)

        self._context.rx['component_perspective'].on_next(perspective)

    def closeEvent(self, services_table):
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

    def _io_service_signature(self, parameters_info: List[ParameterInfo]):
        """ Entry point for processing the service signatures.

            Args:
                signatures: The io service signatures dictionary.
        """
        self._io_services[parameters_info[0].provider] = [
            param for param in parameters_info
            if param.type == ParameterType.get
        ]

    def initialize(self):
        super().initialize()

        # Initialize custom variables
        self._app = QApplication(
            []) if QApplication.instance() is None else QApplication.instance(
            )

    def run(self, rx_value: RunAction):
        """ Entry point for running the plugin

            Args:
                rx_value (RunAction): The value published by the subject.
        """
        self._new_window(rx_value.perspective)
