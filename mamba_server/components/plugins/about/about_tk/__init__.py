""" Plugin to show About message implemented in TkInter """

import os
import pkgutil

import tkinter as tk
from tkinter import messagebox

from mamba_server.components.component_base import ComponentBase
from mamba_server.exceptions import ComponentConfigException

from mamba_server.components.gui.main_window.observable_types.register_action\
    import RegisterAction
from mamba_server.components.gui.main_window.observable_types.run_action\
    import RunAction


class GuiPlugin(ComponentBase):
    """ Plugin to show About message implemented in TkInter """
    def __init__(self, context):
        super(GuiPlugin, self).__init__(os.path.dirname(__file__), context)

        # Initialize observables
        self._register_observables()

        # Initialize custom variables
        self._version = None
        self._box_message = None

    def _register_observables(self):
        self._context.rx.subscribe(
            subject_name='run_plugin',
            on_next=self.run,
            op_filter=lambda rx: isinstance(
                rx, RunAction) and rx.menu_title == self._configuration[
                    'menu'] and rx.action_name == self._configuration['name'])

    def initialize(self):
        self._version = pkgutil.get_data('mamba_server',
                                         'VERSION').decode('ascii').strip()
        self._box_message = f"Mamba Server v{self._version}"

        if not all(key in self._configuration for key in ['menu', 'name']):
            raise ComponentConfigException(
                "Missing required elements in component configuration")

        self._context.rx.on_next(
            'register_action',
            RegisterAction(menu_title=self._configuration['menu'],
                           action_name=self._configuration['name'],
                           shortcut=self._configuration['shortcut']
                           if 'shortcut' in self._configuration else None,
                           status_tip=self._configuration['status_tip']
                           if 'status_tip' in self._configuration else None))

    def run(self, rx_value):
        """ Entry point for running the plugin

            Args:
                rx_value (RunAction): The value published by the subject.
        """
        app = tk.Tk()
        app.overrideredirect(1)
        app.withdraw()

        messagebox.showinfo(self._configuration['message_box_title'],
                            self._box_message)
