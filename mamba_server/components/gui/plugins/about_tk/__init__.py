import os
import pkgutil

import tkinter as tk
from tkinter import messagebox

from mamba_server.components.gui.plugins.interface import GuiPluginInterface


class GuiPlugin(GuiPluginInterface):
    def __init__(self, context=None):
        super(GuiPlugin, self).__init__(os.path.dirname(__file__), context)
        self.box_message = "Mamba Server v{}"
        self.version = ""

    def execute(self):
        root = tk.Tk()
        root.overrideredirect(1)
        root.withdraw()
        self.version = pkgutil.get_data('mamba_server',
                                        'VERSION').decode('ascii').strip()
        messagebox.showinfo(self.configuration['message_box_title'], self.box_message.format(self.version))


if __name__ == '__main__':
    root = tk.Tk()
    plugin = GuiPlugin()
    plugin.execute()