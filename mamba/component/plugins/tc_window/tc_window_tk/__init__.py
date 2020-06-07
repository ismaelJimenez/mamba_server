""" Plugin to show About message implemented in Qt5 """

import os
import time
from typing import List, Dict

from rx import operators as op
from rx.subject import Subject

import tkinter as tk

from mamba.component.plugins import PluginBase
from mamba.component.gui.msg import RunAction
from mamba.core.msg import Empty, \
    ServiceResponse, ServiceRequest, ParameterInfo, ParameterType

from tkinter import Frame, N, S, W, E, Button, Toplevel, END
from tkinter.ttk import Treeview


class App(Frame):
    def __init__(self, parent, _io_services, rx):
        Frame.__init__(self, parent)
        self._rx = rx
        self.CreateUI(parent, _io_services)
        self.grid(sticky=(N, S, W, E))
        parent.grid_rowconfigure(0, weight=1)
        parent.grid_columnconfigure(0, weight=1)
        self._log_numer = 1
        self.observed_services = {}

    def selected_new_provider(self, _io_services):
        self.serviceCombo['values'] = ()

        for parameter_info in _io_services[self.providerCombo.get()]:
            self.serviceCombo['values'] = (*self.serviceCombo['values'],
                                           parameter_info.id)

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
        tv['columns'] = ('description', 'param_1', 'param_2', 'param_3',
                         'param_4')
        tv.heading("#0", text='Service', anchor='center')
        tv.column("#0", anchor="center", width=50)
        tv.heading('description', text='Description')
        tv.column('description', anchor='center', width=100)
        tv.heading('param_1', text='Param_1')
        tv.column('param_1', anchor='center', width=100)
        tv.heading('param_2', text='Param_2')
        tv.column('param_2', anchor='center', width=100)
        tv.heading('param_3', text='Param_3')
        tv.column('param_3', anchor='center', width=100)
        tv.heading('param_4', text='Param_4')
        tv.column('param_4', anchor='center', width=100)

        tv.grid(row=1, columnspan=7, sticky=(N, S, W, E))
        self.treeview = tv

        scrollbar = tk.Scrollbar(self, orient=tk.VERTICAL, command=tv.yview)
        tv.configure(yscrollcommand=scrollbar.set)
        scrollbar.grid(row=1, column=7, sticky='ns')

        self.buttons_frame = Frame(self)
        self.buttons_frame.grid(row=2)

        self.call_button = Button(self.buttons_frame,
                                  text='Call',
                                  command=self.call)

        self.call_button.grid(row=0, column=1, columnspan=5)

        self.remove_button = Button(self.buttons_frame,
                                    text='Remove',
                                    command=self.remove_item)

        self.remove_button.grid(row=0, column=6)

        self.treeview.bind(
            "<<TreeviewSelect>>", self.OnDoubleClick
        )  # single click, without "index out of range" error

        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

    def OnDoubleClick(self, event):
        param_text = self.treeview.item(self.treeview.selection()[0],
                                        "text").split(' -> ')
        provider = param_text[0]
        service = param_text[1]

        parameters = self.observed_services[(provider, service)]
        num_parameter = 4 - parameters.count('-')

        if num_parameter == 0:
            return

        self.item_dialog = Toplevel(self.master)

        self.item_dialog.title(
            self.treeview.item(self.treeview.selection()[0], "text"))

        if num_parameter > 0:
            tk.Label(self.item_dialog, text="Parameter 1").grid(row=0)
            self.e1 = tk.Entry(self.item_dialog)
            self.e1.grid(row=0, column=1)
            self.e1.insert(END, str(parameters[0]))

        if num_parameter > 1:
            tk.Label(self.item_dialog, text="Parameter 2").grid(row=1)
            self.e2 = tk.Entry(self.item_dialog)
            self.e2.grid(row=1, column=1)
            self.e2.insert(END, str(parameters[1]))

        if num_parameter > 2:
            tk.Label(self.item_dialog, text="Parameter 3").grid(row=2)
            self.e3 = tk.Entry(self.item_dialog)
            self.e3.grid(row=2, column=1)
            self.e3.insert(END, str(parameters[2]))

        if num_parameter > 3:
            tk.Label(self.item_dialog, text="Parameter 4").grid(row=3)
            self.e4 = tk.Entry(self.item_dialog)
            self.e4.grid(row=3, column=1)
            self.e4.insert(END, str(parameters[3]))

        self.item_dialog_buttons_frame = Frame(self.item_dialog)
        self.item_dialog_buttons_frame.grid(row=4)

        self.item_dialog_ok_button = Button(
            self.item_dialog_buttons_frame,
            width=9,
            text='OK',
            command=lambda: self.modify_parameters(
                self.treeview.item(self.treeview.selection()[0], "text"),
                num_parameter))
        self.item_dialog_ok_button.grid(row=0, column=0)

        self.item_dialog_cancel_button = Button(self.item_dialog_buttons_frame,
                                                width=9,
                                                text='Cancel',
                                                command=self.close_item_dialog)
        self.item_dialog_cancel_button.grid(row=0, column=4)

        self.item_dialog.wait_window()

    def modify_parameters(self, id, num_params):
        result = [None] * 4

        if num_params > 0:
            result[0] = self.e1.get()
        else:
            result[0] = '-'

        if num_params > 1:
            result[1] = self.e2.get()
        else:
            result[1] = '-'

        if num_params > 2:
            result[2] = self.e3.get()
        else:
            result[2] = '-'

        if num_params > 3:
            result[3] = self.e4.get()
        else:
            result[3] = '-'

        id_split = id.split(' -> ')

        self.observed_services[(id_split[0], id_split[1])] = result

        listOfEntriesInTreeView = self.treeview.get_children()

        for each in listOfEntriesInTreeView:
            if self.treeview.item(each)['text'] == id:
                self.treeview.item(
                    each,
                    text=id,
                    values=(self.treeview.item(each)['values'][0], result[0],
                            result[1], result[2], result[3]))

        self.close_item_dialog()

    def close_item_dialog(self):
        self.item_dialog.destroy()

    def call(self):
        id = self.treeview.item(self.treeview.selection()[0],
                                "text").split(' -> ')
        args = [n for n in self.observed_services[(id[0], id[1])] if n != '-']

        self._rx['tc'].on_next(
            ServiceRequest(provider=id[0],
                           id=id[1],
                           args=args,
                           type=ParameterType.set))

    def remove_item(self):
        selected_items = self.treeview.selection()
        for selected_item in selected_items:
            id = self.treeview.item(self.treeview.selection()[0],
                                    "text").split(' -> ')

            self.observed_services.pop((id[0], id[1]), None)
            self.treeview.delete(selected_item)

    def _add_button(self, _io_services):
        provider = self.providerCombo.get()
        service = self.serviceCombo.get()

        parameter_info = [
            parameter_info for parameter_info in _io_services[provider]
            if parameter_info.id == service
        ][0]

        parameters = parameter_info.signature[0]
        num_params = len(parameters)

        if (service == '') or (provider == ''):
            return

        if (provider, service) in self.observed_services:
            return
        else:
            args = [''] * num_params + ['-'] * (4 - num_params)
            self.observed_services[(provider, service)] = args

        description_item = parameter_info.description

        self.treeview.insert('',
                             0,
                             text=f'{provider} -> {service}',
                             values=(description_item, args[0], args[1],
                                     args[2], args[3]))
        #    log.message, str(log.level),
        #        log.source, str(time.time())))
        print("Add button")

    def onClickedDebug(self):
        # calling IntVar.get() returns the state
        # of the widget it is associated with
        print(self.debugCheckBox.get())

    def _process_io_result(self, rx_value: ServiceResponse):
        if (rx_value.provider, rx_value.id) in self.observed_services:
            for children in self.treeview.get_children():
                child = self.treeview.item(children)
                if child['text'] == rx_value.id:
                    child['measure'] = str(rx_value.value)
                    child['stamp'] = str(time.time())


class Plugin(PluginBase):
    """ Plugin to show About message implemented in Qt5 """
    def __init__(self, context, local_config=None):
        # Define custom variables
        self._app = None
        self._io_services: Dict[str, List[ParameterInfo]] = {}
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
        self._context.rx['io_service_signature'].subscribe(
            on_next=self._io_service_signature)

        self._observer_modified.subscribe(
            on_next=self._process_observer_modification)

    def _process_observer_modification(self, rx_value):
        if self._io_result_subs is not None:
            self._io_result_subs.dispose()

        self._io_result_subs = self._context.rx['io_result'].pipe(
            op.filter(lambda value: isinstance(value, ServiceResponse) and
                      (value.provider, value.id) in self._observed_services)
        ).subscribe(on_next=self.log_table._process_io_result)

    def _process_io_result(self, rx_value: ServiceResponse):
        print('IO RESULT')
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
        self.log_table = App(app, self._io_services, self._context.rx)

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
            id = services_table.item(services_table.visualRow(row),
                                     0).text().split(' -> ')

            self._observed_services[(id[0], id[1])] -= 1

            if self._observed_services[(id[0], id[1])] == 0:
                self._observed_services.pop((id[0], id[1]), None)

            self._service_tables.remove(services_table)
            self._observer_modified.on_next(None)

    def _io_service_signature(self, parameters_info: List[ParameterInfo]):
        """ Entry point for processing the service signatures.

            Args:
                signatures: The io service signatures dictionary.
        """
        self._io_services[parameters_info[0].provider] = [
            param for param in parameters_info
            if param.type == ParameterType.set
        ]

    def initialize(self):
        super(Plugin, self).initialize()

    def run(self, rx_value: RunAction):
        """ Entry point for running the plugin

            Args:
                rx_value (RunAction): The value published by the subject.
        """
        # Generate_window is received to generate a new MDI window
        self._new_window(rx_value.perspective)
