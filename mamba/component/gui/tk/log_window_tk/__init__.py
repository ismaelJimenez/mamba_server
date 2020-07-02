""" Log window GUI Component """

import os
import time

from rx.core.typing import Disposable
from typing import Optional, Dict, List

import tkinter as tk
from tkinter import Frame, N, S, W, E
from tkinter.ttk import Treeview

from mamba.core.component_base import GuiPlugin
from mamba.component.gui.msg import RunAction
from mamba.core.msg import Log, LogLevel
from mamba.core.context import Context


class LogWindowFrame(Frame):
    def __init__(self, parent: tk.Tk) -> None:
        Frame.__init__(self, parent)

        self.tree_view: Optional[Treeview] = None

        self._debug_cb: Optional[tk.Checkbutton] = None
        self.debug_cb_selected = False

        self._info_cb: Optional[tk.Checkbutton] = None
        self.info_cb_selected = False

        self._error_cb: Optional[tk.Checkbutton] = None
        self.error_cb_selected = False

        self._critical_cb: Optional[tk.Checkbutton] = None
        self.critical_cb_selected = False

        self.create_ui()
        self.grid(sticky=(N, S, W, E))
        parent.grid_rowconfigure(0, weight=1)
        parent.grid_columnconfigure(0, weight=1)
        self._log_number = 1

    def create_ui(self) -> None:
        label1 = tk.Label(self, text="Mamba Log:")
        label1.grid(row=0, column=0, pady=(5, 0), sticky='nw')

        tv = Treeview(self)
        tv['columns'] = ('message', 'severity', 'node', 'stamp')
        tv.heading("#0", text='#', anchor='center')
        tv.column("#0", anchor="center", width=50)
        tv.heading('message', text='Message')
        tv.column('message', anchor='center', width=100)
        tv.heading('severity', text='Severity')
        tv.column('severity', anchor='center', width=100)
        tv.heading('node', text='Node')
        tv.column('node', anchor='center', width=100)
        tv.heading('stamp', text='TimeStamp')
        tv.column('stamp', anchor='center', width=100)

        tv.grid(sticky=(N, S, W, E))
        self.tree_view = tv

        scrollbar = tk.Scrollbar(self, orient=tk.VERTICAL, command=tv.yview)
        tv.configure(yscrollcommand=scrollbar.set)
        scrollbar.grid(row=1, column=1, sticky='ns')

        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        label3 = tk.Label(self, text="Exclude Messages:")
        label3.grid(row=2, column=0, pady=(5, 0), sticky='nw')

        self._debug_cb = tk.Checkbutton(
            self,
            text='Debug',
            command=lambda: self.set_debug_state(not self.debug_cb_selected))
        self._debug_cb.grid(row=3, sticky=W)

        self._info_cb = tk.Checkbutton(
            self,
            text='Info',
            command=lambda: self.set_info_state(not self.info_cb_selected))
        self._info_cb.grid(row=4, sticky=W)

        self._error_cb = tk.Checkbutton(
            self,
            text='Error',
            command=lambda: self.set_error_state(not self.error_cb_selected))
        self._error_cb.grid(row=5, sticky=W)

        self._critical_cb = tk.Checkbutton(
            self,
            text='Critical',
            command=lambda: self.set_critical_state(not self.
                                                    critical_cb_selected))
        self._critical_cb.grid(row=6, sticky=W)

    def set_debug_state(self, state: bool) -> None:
        if state:
            self.debug_cb_selected = True
            if self._debug_cb is not None:
                self._debug_cb.select()
        else:
            self.debug_cb_selected = False
            if self._debug_cb is not None:
                self._debug_cb.deselect()

    def set_info_state(self, state: bool) -> None:
        if state:
            self.info_cb_selected = True
            if self._info_cb is not None:
                self._info_cb.select()
        else:
            self.info_cb_selected = False
            if self._info_cb is not None:
                self._info_cb.deselect()

    def set_error_state(self, state: bool) -> None:
        if state:
            self.error_cb_selected = True
            if self._error_cb is not None:
                self._error_cb.select()
        else:
            self.error_cb_selected = False
            if self._error_cb is not None:
                self._error_cb.deselect()

    def set_critical_state(self, state: bool) -> None:
        if state:
            self.critical_cb_selected = True
            if self._critical_cb is not None:
                self._critical_cb.select()
        else:
            self.critical_cb_selected = False
            if self._critical_cb is not None:
                self._critical_cb.deselect()

    def new_log(self, log: Log) -> None:
        if (log.level == LogLevel.Dev and
            not self.debug_cb_selected) or \
                (log.level == LogLevel.Info
                 and not self.info_cb_selected) or \
                (log.level == LogLevel.Warning
                 and not self.error_cb_selected) or \
                (log.level == LogLevel.Error
                 and not self.critical_cb_selected):
            if self.tree_view is not None:
                self.tree_view.insert('',
                                      0,
                                      text=str(self._log_number),
                                      values=(log.msg, str(log.level), log.src,
                                              str(time.time())))

            self._log_number += 1


class LogWindowComponent(GuiPlugin):
    """ Log window GUI Component in Qt5 """
    def __init__(self,
                 context: Context,
                 local_config: Optional[Dict[str, dict]] = None) -> None:
        super().__init__(os.path.dirname(__file__), context, local_config)

        # Define custom variables
        self._windows: List[tk.Tk] = []

    def _received_log(self, log: Log, log_table: LogWindowFrame) -> None:
        """ Entry point for processing a new msg telecommand coming from the
            socket server.

            Args:
                raw_tc (Log): The msg telecommand coming from
                                         the socket.
        """
        log_table.new_log(log)

    def close(self, app: tk.Tk, log_observer: Disposable,
              generate_pers: Disposable) -> None:
        log_observer.dispose()
        generate_pers.dispose()
        app.destroy()

    def run(self, rx_value: RunAction) -> None:
        """ Entry point for running the plugin

            Args:
                rx_value (RunAction): The value published by the subject.
        """
        perspective = rx_value.perspective

        app = tk.Tk()
        app.title(self._configuration['name'])
        log_table = LogWindowFrame(app)

        if perspective is not None:
            if perspective['exclude_debug']:
                log_table.set_debug_state(True)

            if perspective['exclude_info']:
                log_table.set_info_state(True)

            if perspective['exclude_error']:
                log_table.set_error_state(True)

            if perspective['exclude_critical']:
                log_table.set_critical_state(True)

            app.geometry('%dx%d+%d+%d' %
                         (perspective['width'], perspective['height'],
                          perspective['pos_x'], perspective['pos_y']))

        app.update()
        app.deiconify()

        self._windows.append(app)

        # Register to the topic provided by the io_controller services
        log_observer = self._context.rx['log'].subscribe(
            on_next=lambda _: self._received_log(_, log_table))

        generate_pers = self._context.rx['generate_perspective'].subscribe(
            on_next=lambda _: self._generate_perspective(log_table))

        app.protocol("WM_DELETE_WINDOW",
                     lambda: self.close(app, log_observer, generate_pers))

    def _generate_perspective(self, log_table: LogWindowFrame) -> None:
        perspective = {
            'menu_title': self._configuration['menu'],
            'action_name': self._configuration['name'],
            'data': {
                'pos_x': log_table.winfo_rootx(),
                'pos_y': log_table.winfo_rooty(),
                'width': log_table.winfo_width(),
                'height': log_table.winfo_height(),
                'exclude_debug': log_table.debug_cb_selected,
                'exclude_info': log_table.info_cb_selected,
                'exclude_error': log_table.error_cb_selected,
                'exclude_critical': log_table.critical_cb_selected
            }
        }

        self._context.rx['component_perspective'].on_next(perspective)
