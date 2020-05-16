""" Plugin to show About message implemented in TkInter """

import os
import pkgutil

import tkinter as tk
from tkinter import messagebox

from mamba_server.components.gui.plugins.interface import GuiPluginInterface


class GuiPlugin(GuiPluginInterface):
    """ Plugin to show About message implemented in TkInter """
    def __init__(self, context):
        super(GuiPlugin, self).__init__(os.path.dirname(__file__), context)

        self._box_message = "Mamba Server v{}"
        self._version = pkgutil.get_data('mamba_server',
                                         'VERSION').decode('ascii').strip()

    def execute(self):
        app = tk.Tk()
        app.overrideredirect(1)
        app.withdraw()

        messagebox.showinfo(self._configuration['message_box_title'],
                            self._box_message.format(self._version))
