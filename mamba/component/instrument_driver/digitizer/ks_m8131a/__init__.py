""" Keysight m8131a Digitizer Controller"""

import os
from typing import Optional

from mamba.core.context import Context
from mamba.core.component_base import VisaInstrumentDriver


class DigitizerKsm8131A(VisaInstrumentDriver):
    """ Keysight m8131a Digitizer Controller class """
    def __init__(self,
                 context: Context,
                 local_config: Optional[dict] = None) -> None:
        super().__init__(os.path.dirname(__file__), context, local_config)
