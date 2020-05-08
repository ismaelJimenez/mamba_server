from PySide2.QtWidgets import QWidget
import os
import json


class GuiComponentBase(QWidget):
    def __init__(self):
        super(GuiComponentBase, self).__init__()

        script_dir = os.path.dirname(__file__)
        rel_path = "../gui/about/component.config.json"

        with open(os.path.join(script_dir, rel_path)) as f:
            self.info = json.load(f)

    def status_tip(self):
        return self.info['statustip']
