""" Plugin to show About message implemented in Qt5 """

import os

from rx import operators as op
from typing import List, Dict

from PySide2.QtWidgets import QLabel, QWidget, QApplication, QComboBox, \
    QHBoxLayout, QMdiSubWindow, QPushButton, QTableWidget, QMenu, QVBoxLayout,\
    QAbstractItemView, QTableWidgetItem
from PySide2.QtCore import Qt
from PySide2.QtGui import QIcon, QCursor, QFont

from mamba.component.plugins import PluginBase
from mamba.component.gui.msg import RunAction
from mamba.core.msg import Empty, ServiceRequest, ParameterInfo, ParameterType


class CustomTable(QTableWidget):
    def __init__(self, *args, **kwargs):
        QTableWidget.__init__(self, *args, **kwargs)

    def mousePressEvent(self, event):
        if event.button() == Qt.RightButton:
            it = self.itemAt(event.pos())

            if it is not None:
                menu = QMenu(self)
                remove_action = menu.addAction("Remove")
                action = menu.exec_(QCursor.pos())

                if action == remove_action:
                    self.removeRow(it.row())

        QTableWidget.mousePressEvent(self, event)


class Plugin(PluginBase):
    """ Plugin to show About message implemented in Qt5 """
    def __init__(self, context, local_config=None):
        # Define custom variables
        self._app = None
        self._io_services: Dict[str, List[ParameterInfo]] = {}

        super().__init__(os.path.dirname(__file__), context, local_config)

    def _register_observers(self):
        super()._register_observers()

        # Register to the topic provided by the io_controller services
        self._context.rx['io_service_signature'].subscribe(
            on_next=self._io_service_signature)

    def generate_service_combobox(self, providerCombo, serviceCombo):
        serviceCombo.clear()

        for parameter_info in self._io_services[providerCombo.currentText()]:
            if parameter_info.type == ParameterType.Set:
                serviceCombo.addItem(parameter_info.id)

    def call_service(self, provider_id, service_id, services_table):
        args = []

        parameter_text = f'{provider_id} -> {service_id}'

        for row in range(0, services_table.rowCount()):
            if services_table.cellWidget(row, 0).text() == parameter_text:
                for param_index in range(2, 6):
                    param = services_table.item(row, param_index).text()
                    if (param == '-') or (param == ''):
                        break
                    else:
                        args.append(param)

        self._context.rx['tc'].on_next(
            ServiceRequest(provider=provider_id,
                           id=service_id,
                           args=args,
                           type='set'))

    def add_service(self, provider, service, services_table):
        parameter_info = [
            parameter_info for parameter_info in self._io_services[provider]
            if parameter_info.id == service
        ][0]

        parameters = parameter_info.signature[0]
        num_params = len(parameters)

        services_table.insertRow(0)

        service_btn = QPushButton(f'{provider} -> {service}')
        bold_font = QFont()
        bold_font.setBold(True)
        service_btn.setFont(bold_font)

        service_btn.clicked.connect(
            lambda: self.call_service(provider, service, services_table))

        description_item = QTableWidgetItem(parameter_info.description)
        description_item.setFlags(Qt.ItemIsEnabled)

        if num_params > 0:
            param = parameters[0]

            param_1 = QTableWidgetItem("")
            param_1.setTextAlignment(Qt.AlignCenter)

            param_1.setToolTip(str(param))
        else:
            param_1 = QTableWidgetItem("-")
            param_1.setTextAlignment(Qt.AlignCenter)
            param_1.setFlags(Qt.ItemIsEnabled)

        if num_params > 1:
            param = parameters[1]

            param_2 = QTableWidgetItem("")
            param_2.setTextAlignment(Qt.AlignCenter)

            param_2.setToolTip(str(param))
        else:
            param_2 = QTableWidgetItem("-")
            param_2.setTextAlignment(Qt.AlignCenter)
            param_2.setFlags(Qt.ItemIsEnabled)

        if num_params > 2:
            param = parameters[2]

            param_3 = QTableWidgetItem("")
            param_3.setTextAlignment(Qt.AlignCenter)

            param_3.setToolTip(str(param))
        else:
            param_3 = QTableWidgetItem("-")
            param_3.setTextAlignment(Qt.AlignCenter)
            param_3.setFlags(Qt.ItemIsEnabled)

        if num_params > 3:
            param = parameters[3]

            param_4 = QTableWidgetItem("")
            param_4.setTextAlignment(Qt.AlignCenter)

            param_4.setToolTip(str(param))
        else:
            param_4 = QTableWidgetItem("-")
            param_4.setTextAlignment(Qt.AlignCenter)
            param_4.setFlags(Qt.ItemIsEnabled)

        services_table.setCellWidget(0, 0, service_btn)
        services_table.setItem(0, 1, description_item)
        services_table.setItem(0, 2, param_1)
        services_table.setItem(0, 3, param_2)
        services_table.setItem(0, 4, param_3)
        services_table.setItem(0, 5, param_4)

    def _new_window(self, perspective):
        window = QMdiSubWindow()
        self._context.rx['register_window'].on_next(window)
        window.setWindowTitle('Parameter Setter')

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
        services_table = CustomTable()
        services_table.setColumnCount(6)

        services_table.setHorizontalHeaderLabels([
            "Service", "Description", "Param#1", "Param#2", "Param#3",
            "Param#4"
        ])

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
                        break
        else:
            window.adjustSize()

        services_table.setColumnWidth(0, window.width() * 0.3)
        services_table.setColumnWidth(1, window.width() * 0.4)
        services_table.setColumnWidth(2, window.width() * 0.2)
        services_table.setColumnWidth(3, window.width() * 0.2)
        services_table.setColumnWidth(4, window.width() * 0.2)
        services_table.setColumnWidth(5, window.width() * 0.2)

        window.show()

        self._context.rx['generate_perspective'].pipe(
            op.filter(lambda value: isinstance(value, Empty))).subscribe(
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

    def _io_service_signature(self, parameters_info: List[ParameterInfo]):
        """ Entry point for processing the service signatures.

            Args:
                signatures: The io service signatures dictionary.
        """
        self._io_services[parameters_info[0].provider] = parameters_info

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
