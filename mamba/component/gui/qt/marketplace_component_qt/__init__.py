""" Open Project component """

import os

from typing import Optional, Dict, Any
from PySide2.QtWidgets import QApplication, QWidget
from PySide2.QtCore import QCoreApplication

from mamba.core.component_base import GuiPlugin
from mamba.component.gui.msg import RunAction
from mamba.core.context import Context

from .marketplace_component_dialog import MarketComponentDialog


class OpenProjectComponent(GuiPlugin):
    """ Open Project component in Qt5 """
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

    def run(self, rx_value: RunAction) -> None:
        """ Entry point for running the plugin

            Args:
                rx_value (RunAction): The value published by the subject.
        """
        market = MarketComponentDialog(self._context.get('mamba_dir'), os.path.join(self._context.get('mamba_dir'), 'marketplace', 'components'), QWidget())
        return market.exec_()
