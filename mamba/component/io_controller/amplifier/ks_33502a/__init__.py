""" Digitizer IO Controller"""

import os

from mamba.core.msg import ServiceRequest,\
    ServiceResponse
from mamba.core.component_base import VisaController


class PowerSupply(VisaController):
    """ Digitizer IO Controller class """
    def __init__(self, context, local_config=None):
        super(PowerSupply, self).__init__(os.path.dirname(__file__), context,
                                          local_config)
