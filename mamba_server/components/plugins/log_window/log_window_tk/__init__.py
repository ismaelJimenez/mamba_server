""" Plugin to show About message implemented in TkInter """

import os
import tkinter as tk
from tkinter import *
from tkinter.ttk import *
import time

from rx import operators as op

from PySide2.QtWidgets import QLabel, QWidget, QApplication, QMdiSubWindow,\
    QTableWidget, QVBoxLayout, QGroupBox, QCheckBox, QTableWidgetItem
from PySide2.QtCore import Qt

from mamba_server.components.plugins import PluginBase
from mamba_server.components.main.observable_types import RunAction
from mamba_server.components.observable_types import Empty, Log, LogLevel


class App(Frame):
    def __init__(self, parent):
        Frame.__init__(self, parent)
        self.CreateUI(parent)
        self.grid(sticky=(N, S, W, E))
        parent.grid_rowconfigure(0, weight=1)
        parent.grid_columnconfigure(0, weight=1)
        self._log_numer = 1

    def CreateUI(self, parent):
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
        self.treeview = tv

        scrollbar = tk.Scrollbar(self, orient=tk.VERTICAL, command=tv.yview)
        tv.configure(yscrollcommand=scrollbar.set)
        scrollbar.grid(row=1, column=1, sticky='ns')

        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        label3 = tk.Label(self, text="Exclude Messages:")
        label3.grid(row=2, column=0, pady=(5, 0), sticky='nw')

        self.debugCheckBox = IntVar()
        Checkbutton(self, text="Debug", variable=self.debugCheckBox, command = self.onClickedDebug).grid(row=3, sticky=W)
        self.infoCheckBox = IntVar()
        Checkbutton(self, text="Info", variable=self.infoCheckBox).grid(row=4, sticky=W)
        self.errorCheckBox = IntVar()
        Checkbutton(self, text="Error", variable=self.errorCheckBox).grid(row=5, sticky=W)
        self.criticalCheckBox = IntVar()
        Checkbutton(self, text="Critical", variable=self.criticalCheckBox).grid(row=6, sticky=W)


    def onClickedDebug(self):
        # calling IntVar.get() returns the state
        # of the widget it is associated with
        print(self.debugCheckBox.get())

    def new_log(self, log: Log):
        if (log.level == LogLevel.Dev and
            not self.debugCheckBox.get()) or \
                (log.level == LogLevel.Info
                 and not self.infoCheckBox.get()) or \
                (log.level == LogLevel.Warning
                 and not self.errorCheckBox.get()) or \
                (log.level == LogLevel.Error
                 and not self.criticalCheckBox.get()):
            self.treeview.insert('',
                                 0,
                                 text=str(self._log_numer),
                                 values=(log.message, str(log.level), log.source, str(time.time())))

            self._log_numer += 1

class Plugin(PluginBase):
    """ Plugin to show About message implemented in TkInter """
    def __init__(self, context, local_config=None):
        # Define custom variables
        #self._app = None
        #self._log_numer = 1

        #self._new_window_observer = None

        super(Plugin, self).__init__(os.path.dirname(__file__), context,
                                     local_config)

    def _received_log(self, log: Log, log_table):
        """ Entry point for processing a new raw telecommand coming from the
            socket server.

            Args:
                raw_tc (Log): The raw telecommand coming from
                                         the socket.
        """
        log_table.new_log(log)

    def _show(self):
        """ Entry point for showing main screen """
        self._app.update()
        self._app.deiconify()

    def close(self):
        """ Entry point for closing application

            Args:
                rx_value (Empty): The value published by the subject.
        """
        # INFO: quit() stops the TCL interpreter, so the Tkinter - app will
        # stop. destroy() just terminates the mainloop and deletes all
        # widgets.

        self.closeEvent(self.log_observer)
        self._app.destroy()
        self._app = None

    def _close(self, rx_value: Empty):
        """ Entry point for closing application

            Args:
                rx_value (Empty): The value published by the subject.
        """
        # INFO: quit() stops the TCL interpreter, so the Tkinter - app will
        # stop. destroy() just terminates the mainloop and deletes all
        # widgets.
        print("A TOMAR POR CULO")
        self.close()

    #def _new_window(self, window: QMdiSubWindow, perspective):
    def _new_window(self, perspective):
        self._app = tk.Tk()
        self._app.protocol("WM_DELETE_WINDOW", self.close)
        self._app.title(self._configuration['name'])

        self._show()

        log_table = App(self._app)
        self.log_table = log_table

        # if perspective is not None:
        # #     window.move(perspective['pos_x'], perspective['pos_y'])
        # #     window.resize(perspective['width'], perspective['height'])
        # #
        #
        #     log_table.debugCheckBox.set(int(perspective['exclude_debug']))
        #     log_table.infoCheckBox.set(int(perspective['exclude_info']))
        #     log_table.errorCheckBox.set(int(perspective['exclude_error']))
        #     log_table.criticalCheckBox.set(int(perspective['exclude_critical']))

        # else:
        #     window.adjustSize()
        #
        # window.show()
        #
        # Register to the topic provided by the io_controller services
        self.log_observer = self._context.rx['log'].pipe(
            op.filter(lambda value: isinstance(value, Log))).subscribe(
                on_next=lambda _: self._received_log(
                    _, log_table))

        # window.destroyed.connect(lambda: self.closeEvent(log_observer))

        self._context.rx['generate_perspective'].pipe(
            op.filter(lambda value: isinstance(value, Empty))).subscribe(
                on_next=lambda _: self._generate_perspective(log_table))

    def _generate_perspective(self, log_table):
        perspective = {
            'menu_title': self._configuration['menu'],
            'action_name': self._configuration['name'],
            'data': {
        #         'pos_x': window.pos().x(),
        #         'pos_y': window.pos().y(),
        #         'width': window.size().width(),
        #         'height': window.size().height(),
                'exclude_debug': str(log_table.debugCheckBox.get()),
                'exclude_info': str(log_table.infoCheckBox.get()),
                'exclude_error': str(log_table.errorCheckBox.get()),
                'exclude_critical': str(log_table.criticalCheckBox.get())
            }
        }

        #print("GENERATING PERSPECTIVE")

        #perspective = {}

        self._context.rx['component_perspective'].on_next(perspective)

    def closeEvent(self, log_observer):
        log_observer.dispose()

    def initialize(self):
        super(Plugin, self).initialize()

        # Initialize custom variables
        # self._app = QApplication(
        #     []) if QApplication.instance() is None else QApplication.instance(
        #     )

    def run(self, rx_value: RunAction):
        """ Entry point for running the plugin

            Args:
                rx_value (RunAction): The value published by the subject.
        """
        # Generate_window is received to generate a new MDI window
        # self._new_window_observer = self._context.rx['new_window_widget'].pipe(
        #     op.filter(lambda value: isinstance(value, QMdiSubWindow))
        # ).subscribe(
        #     on_next=lambda _: self._new_window(_, rx_value.perspective))
        #
        # self._context.rx['new_window'].on_next(Empty())
        self._new_window(rx_value.perspective)
