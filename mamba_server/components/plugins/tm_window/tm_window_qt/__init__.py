""" Plugin to show About message implemented in Qt5 """

import os
import pkgutil
import time

from rx import operators as op
from rx.subject import Subject

from PySide2.QtWidgets import QLabel, QWidget, QApplication, QComboBox, \
    QHBoxLayout, QMdiSubWindow, QPushButton, QTableWidget, QMenu, QVBoxLayout,\
    QAbstractItemView, QTableWidgetItem
from PySide2.QtCore import QTimer, Qt
from PySide2.QtGui import QIcon, QCursor, QFont, QColor

from mamba_server.components.plugins import PluginBase
from mamba_server.components.main.observable_types import RunAction
from mamba_server.components.observable_types import Empty, Telemetry
from mamba_server.exceptions import ComponentConfigException


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
                    self.parent._observed_services[self.itemAt(it.row(),
                                                               0).text()] -= 1

                    if self.parent._observed_services[self.itemAt(
                            it.row(), 0).text()] == 0:
                        self.parent._observed_services.pop(
                            self.itemAt(it.row(), 0).text(), None)
                        self.parent._observer_modified.on_next(None)

                    self.removeRow(it.row())

        QTableWidget.mousePressEvent(self, event)


class Plugin(PluginBase):
    """ Plugin to show About message implemented in Qt5 """
    def __init__(self, context, local_config=None):
        # Define custom variables
        self._app = None
        self._io_services = {}
        self._service_tables = []
        self._observed_services = {}

        self._observer_modified = Subject()
        self._io_result_subs = None
        self._new_window_observer = None

        super(Plugin, self).__init__(os.path.dirname(__file__), context,
                                     local_config)

    def _register_observers(self):
        super(Plugin, self)._register_observers()

        # Register to the topic provided by the io_controller services
        self._context.rx['io_service_signature'].pipe(
            op.filter(lambda value: isinstance(value, dict))).subscribe(
                on_next=self._io_service_signature)

        self._observer_modified.subscribe(
            on_next=self._process_observer_modification)

    def _process_observer_modification(self, rx_value):
        if self._io_result_subs is not None:
            self._io_result_subs.dispose()

        self._io_result_subs = self._context.rx['io_result'].pipe(
            op.filter(lambda value: isinstance(value, Telemetry) and value.id
                      in self._observed_services)).subscribe(
                          on_next=self._process_io_result)

    def _process_io_result(self, rx_value: Telemetry):
        print('IO RESULT')
        for table in self._service_tables:
            for row in range(0, table.rowCount()):
                service_id = table.item(table.visualRow(row), 0).text()
                if service_id == rx_value.id:
                    table.item(table.visualRow(row), 2).setText(rx_value.value)
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

        for service, info in self._io_services[
                providerCombo.currentText()].items():
            if info['signature'][
                    1] is not None and info['signature'][1] != 'None':
                serviceCombo.addItem(service)

    def add_service(self, provider, service, services_table):
        if (service == '') or (provider == ''):
            return

        for row in range(0, services_table.rowCount()
                         ):  # Do not allow 2 services with same name
            if services_table.item(row, 0).text() == service:
                return

        services_table.insertRow(0)

        service_item = QTableWidgetItem(service)
        service_item.setFlags(Qt.ItemIsEnabled)

        description_item = QTableWidgetItem(
            self._io_services[provider][service]['description'])
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

        services_table.setItem(0, 0, service_item)
        services_table.setItem(0, 1, description_item)
        services_table.setItem(0, 2, measured_value)
        services_table.item(0, 2).setBackground(Qt.black)
        services_table.item(0, 2).setForeground(Qt.green)
        services_table.item(0, 2).setFont(font)
        services_table.setItem(0, 3, units)
        services_table.setItem(0, 4, stamp)
        services_table.item(0, 4).setFont(font)
        services_table.item(0, 4).setForeground(Qt.darkGray)

        if self._observed_services.get(service) is None:
            self._observed_services[service] = 1
            self._observer_modified.on_next(None)
        else:
            self._observed_services[service] += 1

    def _new_window(self, window: QMdiSubWindow, perspective):
        self._new_window_observer.dispose()

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
                for provider, services in self._io_services.items():
                    if service_id in services:
                        self.add_service(provider, service_id, services_table)
                        break
        else:
            window.adjustSize()

        services_table.setColumnWidth(0, window.width() * 0.2)
        services_table.setColumnWidth(1, window.width() * 0.2)
        services_table.setColumnWidth(2, window.width() * 0.2)
        services_table.setColumnWidth(3, window.width() * 0.2)
        services_table.setColumnWidth(4, window.width() * 0.2)

        window.show()

        window.destroyed.connect(lambda: self.closeEvent(services_table))

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
                services_table.item(row, 0).text())

        print(perspective)

        self._context.rx['component_perspective'].on_next(perspective)

    def closeEvent(self, services_table):
        for row in range(0, services_table.rowCount()):
            service_id = services_table.item(services_table.visualRow(row),
                                             0).text()

            self._observed_services[services_table.item(
                services_table.visualRow(row), 0).text()] -= 1

            if self._observed_services[services_table.item(
                    services_table.visualRow(row), 0).text()] == 0:
                self._observed_services.pop(
                    services_table.item(services_table.visualRow(row),
                                        0).text(), None)

            self._service_tables.remove(services_table)
            self._observer_modified.on_next(None)

    def _io_service_signature(self, signatures: dict):
        """ Entry point for processing the service signatures.

            Args:
                signatures: The io service signatures dictionary.
        """
        self._io_services.update(
            {signatures['provider']: signatures['services']})

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
