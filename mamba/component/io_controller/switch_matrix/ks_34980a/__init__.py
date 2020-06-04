""" Digitizer IO Controller"""

import os
from mamba.core.component_base import VisaController


class SwitchMatrixKs34980a(VisaController):
    """ Digitizer IO Controller class """
    def __init__(self, context, local_config=None):
        super().__init__(os.path.dirname(__file__), context, local_config)
