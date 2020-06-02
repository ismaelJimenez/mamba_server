""" Digitizer IO Controller"""

import os

from mamba.core.msg import ServiceRequest,\
    ServiceResponse
from mamba.component.io_controller import VisaControllerBase


class PowerSupply(VisaControllerBase):
    """ Digitizer IO Controller class """
    def __init__(self, context, local_config=None):
        super(PowerSupply, self).__init__(os.path.dirname(__file__), context,
                                          local_config)
