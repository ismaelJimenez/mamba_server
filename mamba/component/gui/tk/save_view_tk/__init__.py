""" Save view component """

import os
import json

from rx.core.typing import Disposable

from typing import Optional, Dict, Any
import tkinter as tk
from tkinter.filedialog import asksaveasfilename

from mamba.core.component_base import GuiPlugin
from mamba.core.msg import Empty
from mamba.component.gui.msg import RunAction
from mamba.core.context import Context


class SaveViewComponent(GuiPlugin):
    """ Save view component in Tk """
    def __init__(self,
                 context: Context,
                 local_config: Optional[Dict[str, dict]] = None) -> None:
        super().__init__(os.path.dirname(__file__), context, local_config)

        # Define custom variables
        self._app: Optional[tk.Tk] = None
        self._views = []

    def save_views(self, file_name: str) -> None:
        if '.json' not in file_name:
            file_name = file_name + '.json'
        with open(file_name, 'w') as fout:
            json.dump(self._views, fout)

    def process_received_view(self, perspectives_observer: Disposable) -> None:
        perspectives_observer.dispose()

        file_name = asksaveasfilename(title="Save View",
                                      defaultextension=".json",
                                      filetypes=[("perspective", "*.json")])

        if file_name:
            self.save_views(file_name)

    def run(self, rx_value: RunAction) -> None:
        """ Entry point for running the plugin

            Args:
                rx_value (RunAction): The value published by the subject.
        """
        self._views = []

        perspectives_observer = self._context.rx[
            'component_perspective'].subscribe(
                on_next=self._process_component_perspective)

        self._app = tk.Tk()
        self._app.overrideredirect(1)
        self._app.withdraw()

        self._app.after(
            int(1000),
            lambda: self.process_received_view(perspectives_observer))

        self._context.rx['generate_perspective'].on_next(Empty())

    def _process_component_perspective(self, perspective: Dict[str,
                                                               Any]) -> None:
        self._views.append(perspective)
