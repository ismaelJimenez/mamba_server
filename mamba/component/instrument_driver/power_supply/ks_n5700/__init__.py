""" Keysight Series N5700 DC Power Supply Controller"""
from typing import Optional
import os

from mamba.core.context import Context
from mamba.core.component_base import VisaInstrumentDriver


class PowerSupplyKsN5700(VisaInstrumentDriver):
    """ Keysight Series N5700 DC Power Supply Controller class """
    def __init__(self,
                 context: Context,
                 local_config: Optional[dict] = None) -> None:
        super().__init__(os.path.dirname(__file__), context, local_config)
