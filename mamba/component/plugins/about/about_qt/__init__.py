""" Plugin to show About message implemented in Qt5 """

import os
import pkgutil

from PySide2.QtWidgets import QMessageBox, QWidget, QApplication
from PySide2.QtGui import QIcon

from mamba.component.plugins import PluginBase
from mamba.component.gui.msg import RunAction


class Plugin(PluginBase):
    """ Plugin to show About message implemented in Qt5 """
    def __init__(self, context, local_config=None):
        super(Plugin, self).__init__(os.path.dirname(__file__), context,
                                     local_config)

        # Define custom variables
        self._version = None
        self._box_message = None
        self._app = None

    def initialize(self):
        super(Plugin, self).initialize()

        # Initialize custom variables
        self._app = QApplication(
            []) if QApplication.instance() is None else QApplication.instance(
            )

        self._version = pkgutil.get_data('mamba',
                                         'VERSION').decode('ascii').strip()
        self._box_message = f"Mamba Server v{self._version}"
        self._app.setWindowIcon(
            QIcon(
                os.path.join(self._context.get('mamba_dir'), 'artwork',
                             'mamba_icon.png')))

    def run(self, rx_value: RunAction):
        """ Entry point for running the plugin

            Args:
                rx_value (RunAction): The value published by the subject.
        """
        def center(widget):
            frame_gm = widget.frameGeometry()
            screen = QApplication.desktop().screenNumber(
                QApplication.desktop().cursor().pos())
            center_point = QApplication.desktop().screenGeometry(
                screen).center()
            frame_gm.moveCenter(center_point)
            widget.move(frame_gm.topLeft())

        widget = QWidget()
        center(widget)
        QMessageBox.about(widget, self._configuration['message_box_title'],
                          self._box_message)
