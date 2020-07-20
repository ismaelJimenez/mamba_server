################################################################################################
##
##  Copyright (c) Mamba Developers. All rights reserved.
##  Licensed under the MIT License. See License.txt in the project root for license information.
##
################################################################################################

""" Parameter Setter window GUI Component """

import os
import time

from typing import List, Dict, Optional

import tkinter as tk
from tkinter import Frame, N, S, W, E, Button, Toplevel, END
from tkinter.ttk import Treeview

from rx.core.typing import Disposable

from mamba.core.component_base import GuiPlugin
from mamba.component.gui.msg import RunAction
from mamba.core.msg import ServiceRequest, ParameterInfo, ParameterType
from mamba.core.context import Context
from mamba.core.subject_factory import SubjectFactory


class ParameterSetterFrame(Frame):
    def __init__(self, parent: tk.Tk, io_services: Dict[str,
                                                        List[ParameterInfo]],
                 rx: SubjectFactory) -> None:
        Frame.__init__(self, parent)

        self._rx = rx
        self.provider_combo: Optional[tk.ttk.Combobox] = None
        self.service_combo: Optional[tk.ttk.Combobox] = None
        self.tree_view: Optional[Treeview] = None
        self.buttons_frame: Optional[Frame] = None
        self.call_button: Optional[Button] = None
        self.remove_button: Optional[Button] = None

        self.create_ui(io_services)
        self.grid(sticky=(N, S, W, E))
        parent.grid_rowconfigure(0, weight=1)
        parent.grid_columnconfigure(0, weight=1)
        self.observed_services = {}

    def create_ui(self, io_services: Dict[str, List[ParameterInfo]]) -> None:
        label1 = tk.Label(self, text="Provider:")
        label1.grid(row=0, column=0, pady=(5, 0), sticky='nw')

        self.provider_combo = tk.ttk.Combobox(self)

        for service, value in io_services.items():
            self.provider_combo['values'] = (*self.provider_combo['values'],
                                             service)

        self.provider_combo.grid(row=0, column=1, pady=(5, 0), sticky='nw')

        self.provider_combo.bind(
            "<<ComboboxSelected>>",
            lambda _: self.selected_new_provider(io_services))

        tk.Label(self, text="   ").grid(row=0,
                                        column=2,
                                        pady=(5, 0),
                                        sticky='nw')

        label2 = tk.Label(self, text="Service:")
        label2.grid(row=0, column=3, pady=(5, 0), sticky='nw')

        self.service_combo = tk.ttk.Combobox(self)
        self.service_combo.grid(row=0, column=4, pady=(5, 0), sticky='nw')

        tk.Label(self, text="   ").grid(row=0,
                                        column=5,
                                        pady=(5, 0),
                                        sticky='nw')

        add_button = Button(
            self,
            text="Add",
            command=lambda: self.add_service(self.provider_combo.get(
            ), self.service_combo.get(), io_services))

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
        self.tree_view = tv

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

        self.tree_view.bind(
            "<<TreeviewSelect>>", self.OnDoubleClick
        )  # single click, without "index out of range" error

        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

    def selected_new_provider(self, io_services):
        self.service_combo['values'] = ()

        for parameter_info in io_services[self.provider_combo.get()]:
            self.service_combo['values'] = (*self.service_combo['values'],
                                            parameter_info.id)

    def call(self):
        if len(self.tree_view.selection()) > 0:
            id = self.tree_view.item(self.tree_view.selection()[0],
                                     "text").split(' -> ')
            args = [
                n for n in self.observed_services[(id[0], id[1])] if n != '-'
            ]

            self._rx['tc'].on_next(
                ServiceRequest(provider=id[0],
                               id=id[1],
                               args=args,
                               type=ParameterType.set))

    def remove_item(self):
        selected_items = self.tree_view.selection()
        for selected_item in selected_items:
            id = self.tree_view.item(self.tree_view.selection()[0],
                                     "text").split(' -> ')

            self.observed_services.pop((id[0], id[1]), None)
            self.tree_view.delete(selected_item)

    def OnDoubleClick(self, event):
        param_text = self.tree_view.item(self.tree_view.selection()[0],
                                         "text").split(' -> ')
        provider = param_text[0]
        service = param_text[1]

        parameters = self.observed_services[(provider, service)]
        num_parameter = 4 - parameters.count('-')

        if num_parameter == 0:
            return

        self.item_dialog = Toplevel(self.master)

        self.item_dialog.title(
            self.tree_view.item(self.tree_view.selection()[0], "text"))

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
                self.tree_view.item(self.tree_view.selection()[0], "text"),
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

        listOfEntriesInTreeView = self.tree_view.get_children()

        for each in listOfEntriesInTreeView:
            if self.tree_view.item(each)['text'] == id:
                self.tree_view.item(
                    each,
                    text=id,
                    values=(self.tree_view.item(each)['values'][0], result[0],
                            result[1], result[2], result[3]))

        self.close_item_dialog()

    def close_item_dialog(self):
        self.item_dialog.destroy()

    def add_service(self, provider, service, _io_services):
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

        self.tree_view.insert('',
                              0,
                              text=f'{provider} -> {service}',
                              values=(description_item, args[0], args[1],
                                      args[2], args[3]))


class ParameterSetterComponent(GuiPlugin):
    """ Parameter Setter window GUI Component in Qt5 """
    def __init__(self,
                 context: Context,
                 local_config: Optional[Dict[str, dict]] = None) -> None:
        super().__init__(os.path.dirname(__file__), context, local_config)

        # Define custom variables
        self._windows: List[tk.Tk] = []
        self._io_services: Dict[str, List[ParameterInfo]] = {}

    def _register_observers(self) -> None:
        super()._register_observers()

        # Register to the topic provided by the io_controller services
        self._context.rx['io_service_signature'].subscribe(
            on_next=self._io_service_signature)

    def run(self, rx_value: RunAction) -> None:
        """ Entry point for running the plugin

            Args:
                rx_value (RunAction): The value published by the subject.
        """
        perspective = rx_value.perspective

        app = tk.Tk()
        app.title(self._configuration['name'])
        table = ParameterSetterFrame(app, self._io_services, self._context.rx)

        if perspective is not None:
            for service_id in perspective['services']:
                param_id_split = service_id.split(' -> ')
                provider = param_id_split[0]
                param_id = param_id_split[1]

                if provider in self._io_services:
                    if len([
                            param for param in self._io_services[provider]
                            if param.id == param_id
                    ]) > 0:
                        table.add_service(provider, param_id,
                                          self._io_services)

            app.geometry('%dx%d+%d+%d' %
                         (perspective['width'], perspective['height'],
                          perspective['pos_x'], perspective['pos_y']))

        app.update()
        app.deiconify()

        self._windows.append(app)

        generate_pers = self._context.rx['generate_perspective'].subscribe(
            on_next=lambda _: self._generate_perspective(table))

        app.protocol("WM_DELETE_WINDOW",
                     lambda: self.close(app, generate_pers))

    def close(self, app: tk.Tk, generate_pers: Disposable) -> None:
        generate_pers.dispose()
        app.destroy()

    def _generate_perspective(self, log_table: ParameterSetterFrame) -> None:
        perspective = {
            'menu_title': self._configuration['menu'],
            'action_name': self._configuration['name'],
            'data': {
                'pos_x': log_table.winfo_rootx(),
                'pos_y': log_table.winfo_rooty(),
                'width': log_table.winfo_width(),
                'height': log_table.winfo_height(),
                'services': []
            }
        }

        for key, value in log_table.observed_services.items():
            perspective['data']['services'].append(f'{key[0]} -> {key[1]}')

        self._context.rx['component_perspective'].on_next(perspective)

    def _io_service_signature(self,
                              parameters_info: List[ParameterInfo]) -> None:
        """ Entry point for processing the service signatures.

            Args:
                signatures: The io service signatures dictionary.
        """
        self._io_services[parameters_info[0].provider] = [
            param for param in parameters_info
            if param.type == ParameterType.set
        ]
