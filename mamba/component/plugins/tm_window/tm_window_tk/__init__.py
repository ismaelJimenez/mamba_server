""" Plugin to show About message implemented in Qt5 """

import os
import time

from rx import operators as op
from rx.subject import Subject

import tkinter as tk

from mamba.component.plugins import PluginBase
from mamba.component.gui.msg import RunAction
from mamba.core.msg import Empty, ServiceResponse

from tkinter import Frame, N, S, W, E, Button
from tkinter.ttk import Treeview


class App(Frame):
    def __init__(self, parent, _io_services):
        Frame.__init__(self, parent)
        self.CreateUI(parent, _io_services)
        self.grid(sticky=(N, S, W, E))
        parent.grid_rowconfigure(0, weight=1)
        parent.grid_columnconfigure(0, weight=1)
        self._log_numer = 1
        self.observed_services = {}

    def selected_new_provider(self, _io_services):
        print("new provider")
        print(self.providerCombo.get())

        self.serviceCombo['values'] = ()

        for service, info in _io_services[self.providerCombo.get()].items():
            if info['signature'][
                    1] is not None and info['signature'][1] != 'None':
                self.serviceCombo['values'] = (*self.serviceCombo['values'],
                                               service)

    def CreateUI(self, parent, _io_services):
        label1 = tk.Label(self, text="Provider:")
        label1.grid(row=0, column=0, pady=(5, 0), sticky='nw')

        self.providerCombo = tk.ttk.Combobox(self)

        for service, value in _io_services.items():
            self.providerCombo['values'] = (*self.providerCombo['values'],
                                            service)

        self.providerCombo.grid(row=0, column=1, pady=(5, 0), sticky='nw')

        self.providerCombo.bind(
            "<<ComboboxSelected>>",
            lambda _: self.selected_new_provider(_io_services))

        tk.Label(self, text="   ").grid(row=0,
                                        column=2,
                                        pady=(5, 0),
                                        sticky='nw')

        label2 = tk.Label(self, text="Service:")
        label2.grid(row=0, column=3, pady=(5, 0), sticky='nw')

        self.serviceCombo = tk.ttk.Combobox(self)
        self.serviceCombo.grid(row=0, column=4, pady=(5, 0), sticky='nw')

        tk.Label(self, text="   ").grid(row=0,
                                        column=5,
                                        pady=(5, 0),
                                        sticky='nw')

        add_button = Button(self,
                            text="Add",
                            command=lambda: self._add_button(_io_services))
        add_button.grid(row=0, column=6, pady=(5, 0), sticky='nw')

        tv = Treeview(self)
        tv['columns'] = ('description', 'measure', 'unit', 'stamp')
        tv.heading("#0", text='Service', anchor='center')
        tv.column("#0", anchor="center", width=50)
        tv.heading('description', text='Description')
        tv.column('description', anchor='center', width=100)
        tv.heading('measure', text='Measure')
        tv.column('measure', anchor='center', width=100)
        tv.heading('unit', text='Unit')
        tv.column('unit', anchor='center', width=100)
        tv.heading('stamp', text='TimeStamp')
        tv.column('stamp', anchor='center', width=100)

        tv.grid(row=1, columnspan=7, sticky=(N, S, W, E))
        self.treeview = tv

        scrollbar = tk.Scrollbar(self, orient=tk.VERTICAL, command=tv.yview)
        tv.configure(yscrollcommand=scrollbar.set)
        scrollbar.grid(row=1, column=7, sticky='ns')

        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

    def _add_button(self, _io_services):
        service = self.serviceCombo.get()
        provider = self.providerCombo.get()

        if (service == '') or (provider == ''):
            return

        if service in self.observed_services:
            return
        else:
            self.observed_services[service] = True

        description_item = _io_services[provider][service]['description']

        self.treeview.insert('',
                             0,
                             text=self.serviceCombo.get(),
                             values=(description_item, 'N/A', '-', 'N/A'))
        #    log.message, str(log.level),
        #        log.source, str(time.time())))
        print("Add button")

    def onClickedDebug(self):
        # calling IntVar.get() returns the state
        # of the widget it is associated with
        print(self.debugCheckBox.get())

    def _process_io_result(self, rx_value: ServiceResponse):
        print("REC!!")
        print(rx_value.id)
        print(self.observed_services)
        if rx_value.id in self.observed_services:
            for children in self.treeview.get_children():
                if self.treeview.item(children)['text'] == rx_value.id:
                    self.treeview.item(
                        children,
                        text=rx_value.id,
                        values=(self.treeview.item(children)['values'][0],
                                rx_value.value,
                                self.treeview.item(children)['values'][2],
                                self.treeview.item(children)['values'][3],
                                str(time.time())))

                #
                # child = self.treeview.item(children)
                # if child['text'] == rx_value.id:
                #     child['measure'] = str(rx_value.value)
                #     child['stamp'] = str(time.time())

    def new_log(self, log):
        pass


class Plugin(PluginBase):
    """ Plugin to show About message implemented in Qt5 """
    def __init__(self, context, local_config=None):
        # Define custom variables
        self._app = None
        self._io_services = {}
        self._service_tables = []
        # self._observed_services = {}

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
            op.filter(lambda value: isinstance(value, ServiceResponse))
        ).subscribe(on_next=lambda _: print("PACO"))

    # def _process_io_result(self, rx_value: Telemetry):
    #    print('IO RESULT')
    # for table in self._service_tables:
    #     for row in range(0, table.rowCount()):
    #         service_id = table.item(table.visualRow(row), 0).text()
    #         if service_id == rx_value.id:
    #             table.item(table.visualRow(row),
    #                        2).setText(str(rx_value.value))
    #             table.item(table.visualRow(row),
    #                        4).setText(str(time.time()))
    #             if rx_value.type == 'error':
    #                 table.item(table.visualRow(row),
    #                            2).setBackground(Qt.red)
    #                 table.item(table.visualRow(row),
    #                            2).setForeground(Qt.black)
    #             else:
    #                 table.item(table.visualRow(row),
    #                            2).setBackground(Qt.black)
    #                 table.item(table.visualRow(row),
    #                            2).setForeground(Qt.green)

    def generate_service_combobox(self, providerCombo, serviceCombo):
        serviceCombo.clear()

        for service, info in self._io_services[
                providerCombo.currentText()].items():
            if info['signature'][
                    1] is not None and info['signature'][1] != 'None':
                serviceCombo.addItem(service)

    def add_service(self, provider, service, services_table):
        pass
        # services_table.insertRow(0)
        #
        # service_item = QTableWidgetItem(service)
        # service_item.setFlags(Qt.ItemIsEnabled)
        #
        # description_item = QTableWidgetItem(
        #     self._io_services[provider][service]['description'])
        # description_item.setFlags(Qt.ItemIsEnabled)
        #
        # measured_value = QTableWidgetItem("N/A")
        # measured_value.setFlags(Qt.ItemIsEnabled)
        # measured_value.setTextAlignment(Qt.AlignCenter)
        #
        # units = QTableWidgetItem("-")
        # units.setFlags(Qt.ItemIsEnabled)
        # units.setTextAlignment(Qt.AlignCenter)
        #
        # stamp = QTableWidgetItem("N/A")
        # stamp.setFlags(Qt.ItemIsEnabled)
        # stamp.setTextAlignment(Qt.AlignCenter)
        #
        # font = QFont()
        # font.setBold(True)
        #
        # services_table.setItem(0, 0, service_item)
        # services_table.setItem(0, 1, description_item)
        # services_table.setItem(0, 2, measured_value)
        # services_table.item(0, 2).setBackground(Qt.black)
        # services_table.item(0, 2).setForeground(Qt.green)
        # services_table.item(0, 2).setFont(font)
        # services_table.setItem(0, 3, units)
        # services_table.setItem(0, 4, stamp)
        # services_table.item(0, 4).setFont(font)
        # services_table.item(0, 4).setForeground(Qt.darkGray)
        #
        # if self._observed_services.get(service) is None:
        #     self._observed_services[service] = 1
        #     self._observer_modified.on_next(None)
        # else:
        #     self._observed_services[service] += 1

    def close(self, app):
        """ Entry point for closing application

            Args:
                rx_value (Empty): The value published by the subject.
        """
        # INFO: quit() stops the TCL interpreter, so the Tkinter - app will
        # stop. destroy() just terminates the mainloop and deletes all
        # widgets.

        app.destroy()

    def _new_window(self, perspective):
        app = tk.Tk()
        app.protocol("WM_DELETE_WINDOW", lambda: self.close(app))
        app.title(self._configuration['name'])
        self.log_table = App(app, self._io_services)

        self._io_result_subs = self._context.rx['io_result'].pipe(
            op.filter(lambda value: isinstance(value, ServiceResponse))
        ).subscribe(on_next=self.log_table._process_io_result)

    def _generate_perspective(self, window, services_table):
        # perspective = {
        #     'menu_title': self._configuration['menu'],
        #     'action_name': self._configuration['name'],
        #     'data': {
        #         'pos_x': window.pos().x(),
        #         'pos_y': window.pos().y(),
        #         'width': window.size().width(),
        #         'height': window.size().height(),
        #         'services': []
        #     }
        # }
        #
        # for row in range(0, services_table.rowCount()):
        #     perspective['data']['services'].append(
        #         services_table.item(row, 0).text())

        perspective = {}
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

    def run(self, rx_value: RunAction):
        """ Entry point for running the plugin

            Args:
                rx_value (RunAction): The value published by the subject.
        """
        self._new_window(rx_value.perspective)
