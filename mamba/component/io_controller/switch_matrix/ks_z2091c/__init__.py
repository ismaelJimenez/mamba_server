""" Digitizer IO Controller"""

import os
from typing import Optional

from mamba.core.context import Context
from mamba.core.component_base import VisaController


class SwitchMatrixKsZ2091c(VisaController):
    """ Digitizer IO Controller class """
    def __init__(self,
                 context: Context,
                 local_config: Optional[dict] = None) -> None:
        super().__init__(os.path.dirname(__file__), context, local_config)