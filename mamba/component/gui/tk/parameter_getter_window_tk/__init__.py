################################################################################################
##
##  Copyright (c) Mamba Developers. All rights reserved.
##  Licensed under the MIT License. See License.txt in the project root for license information.
##
################################################################################################

""" Parameter Setter window GUI Component """

import os
import time

from typing import List, Dict, Optional, Any

import tkinter as tk
from tkinter import Frame, N, S, W, E, Button
from tkinter.ttk import Treeview

from rx import operators as op
from rx.core.typing import Disposable
from rx.subject import Subject

from mamba.core.component_base import GuiPlugin
from mamba.component.gui.msg import RunAction
from mamba.core.msg import ServiceRequest, ParameterInfo, ParameterType, \
    ServiceResponse
from mamba.core.context import Context
from mamba.core.subject_factory import SubjectFactory


class ParameterGetterFrame(Frame):
    def __init__(self, parent: tk.Tk, io_services: Dict[str,
                                                        List[ParameterInfo]],
                 rx: SubjectFactory, observer_modified: Subject) -> None:
        Frame.__init__(self, parent)

        self._rx = rx
        self.provider_combo: Optional[tk.ttk.Combobox] = None
        self.service_combo: Optional[tk.ttk.Combobox] = None
        self.tree_view: Optional[Treeview] = None
        self.buttons_frame: Optional[Frame] = None
        self.call_button: Optional[Button] = None
        self.remove_button: Optional[Button] = None
        self._observer_modified = observer_modified

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

            self._rx['tc'].on_next(
                ServiceRequest(provider=id[0],
                               id=id[1],
                               args=[],
                               type=ParameterType.get))

    def remove_item(self):
        selected_items = self.tree_view.selection()
        for selected_item in selected_items:
            id = self.tree_view.item(self.tree_view.selection()[0],
                                     "text").split(' -> ')

            self.observed_services.pop((id[0], id[1]), None)
            self.tree_view.delete(selected_item)
        self._observer_modified.on_next(None)

    def add_service(self, provider, service, _io_services):
        if (service == '') or (provider == ''):
            return

        parameter_info = [
            parameter_info for parameter_info in _io_services[provider]
            if parameter_info.id == service
        ][0]

        if (provider, service) in self.observed_services:
            return
        else:
            self.observed_services[(provider, service)] = True

        description_item = parameter_info.description

        self.tree_view.insert('',
                              0,
                              text=f'{provider} -> {service}',
                              values=(description_item, 'N/A', '-', 'N/A'))
        self._observer_modified.on_next(None)

    def _process_io_result(self, rx_value: ServiceResponse):
        if (rx_value.provider, rx_value.id) in self.observed_services:
            for children in self.tree_view.get_children():
                if self.tree_view.item(children)[
                        'text'] == f'{rx_value.provider} -> {rx_value.id}':
                    self.tree_view.item(
                        children,
                        text=f'{rx_value.provider} -> {rx_value.id}',
                        values=(self.tree_view.item(children)['values'][0],
                                rx_value.value,
                                self.tree_view.item(children)['values'][2],
                                str(time.time())))


class ParameterGetterComponent(GuiPlugin):
    """ Parameter Setter window GUI Component in Qt5 """
    def __init__(self,
                 context: Context,
                 local_config: Optional[Dict[str, dict]] = None) -> None:

        self._observer_modified = Subject()

        super().__init__(os.path.dirname(__file__), context, local_config)

        # Define custom variables
        self._windows: List[tk.Tk] = []
        self._io_services: Dict[str, List[ParameterInfo]] = {}

        self._service_tables: List[ParameterGetterFrame] = []
        self._io_result_subs: List[Disposable] = []

    def _register_observers(self) -> None:
        super()._register_observers()

        # Register to the topic provided by the io_controller services
        self._context.rx['io_service_signature'].subscribe(
            on_next=self._io_service_signature)

        self._observer_modified.subscribe(
            on_next=self._process_observer_modification)

    def _process_observer_modification(self, rx_value: Any) -> None:
        for io_sub in self._io_result_subs:
            io_sub.dispose()
        self._io_result_subs = []

        for service_table in self._service_tables:
            io_sub = self._context.rx['io_result'].pipe(
                op.filter(lambda value: value.type == ParameterType.get)
            ).subscribe(on_next=service_table._process_io_result)

            self._io_result_subs.append(io_sub)

    def run(self, rx_value: RunAction) -> None:
        """ Entry point for running the plugin

            Args:
                rx_value (RunAction): The value published by the subject.
        """
        perspective = rx_value.perspective

        app = tk.Tk()
        app.title(self._configuration['name'])
        table = ParameterGetterFrame(app, self._io_services, self._context.rx,
                                     self._observer_modified)
        self._service_tables.append(table)

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
                     lambda: self.close(app, generate_pers, table))

    def close(self, app: tk.Tk, generate_pers: Disposable,
              table: ParameterGetterFrame) -> None:
        self._service_tables.remove(table)
        self._observer_modified.on_next(None)

        generate_pers.dispose()
        app.destroy()

    def _generate_perspective(self, log_table: ParameterGetterFrame) -> None:
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
            if param.type == ParameterType.get
        ]
