""" RF Signal Generator IO Controller"""
from typing import Optional
import os

from mamba.core.context import Context
from mamba.core.component_base import VisaController


class SignalGeneratorSmb100b(VisaController):
    """ RF Signal Generator IO Controller class """
    def __init__(self,
                 context: Context,
                 local_config: Optional[dict] = None) -> None:
        super().__init__(os.path.dirname(__file__), context, local_config)
