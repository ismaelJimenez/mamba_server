""" New Project component """

import os

from typing import Optional, Dict, Any
from PySide2.QtWidgets import QApplication, QWidget, QFileDialog
from PySide2.QtCore import QCoreApplication

from mamba.core.component_base import GuiPlugin
from mamba.component.gui.msg import RunAction
from mamba.core.context import Context
from mamba.commands.start import Command as NewProjectCommand
from mamba.core.composer_parser import compose_parser


class NewProjectComponent(GuiPlugin):
    """ New Project component in Qt5 """
    def __init__(self,
                 context: Context,
                 local_config: Optional[Dict[str, dict]] = None) -> None:
        super().__init__(os.path.dirname(__file__), context, local_config)

        # Define custom variables
        self._app: Optional[QCoreApplication] = None

    def initialize(self):
        super().initialize()

        # Initialize custom variables
        self._app = QApplication(
            []) if QApplication.instance() is None else QApplication.instance(
            )

    def publish_views(self, profiles: Dict[str, Any]) -> None:
        for profile in profiles:
            self._context.rx['run_plugin'].on_next(
                RunAction(menu_title=profile['menu_title'],
                          action_name=profile['action_name'],
                          perspective=profile['data']))

    def generate_new_project(self, dir):
        class Argument:
            project_name = dir
        new_project_command = NewProjectCommand()
        new_project_command.run(Argument, self._context.get('mamba_dir'), dir, self._log_error)

    def run(self, rx_value: RunAction) -> None:
        """ Entry point for running the plugin

            Args:
                rx_value (RunAction): The value published by the subject.
        """
        dir = QFileDialog.getExistingDirectory(QWidget(), 'New Mamba Project',
                                               os.getcwd(),
                                               QFileDialog.ShowDirsOnly
                                               | QFileDialog.DontResolveSymlinks)
        if dir:
            self.generate_new_project(dir)
            compose_parser(os.path.join(dir, 'composer', 'project-compose.yml'), self._context.get('mamba_dir'), dir)
