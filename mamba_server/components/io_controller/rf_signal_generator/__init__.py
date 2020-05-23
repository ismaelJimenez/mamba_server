""" RF Signal Generator IO Controller"""

import os

from mamba_server.components.observable_types import IoServiceRequest,\
    Telemetry
from mamba_server.components.io_controller import VisaControllerBase


class RfSignalGenerator(VisaControllerBase):
    """ RF Signal Generator IO Controller class """
    def __init__(self, context, local_config=None):
        super(RfSignalGenerator, self).__init__(os.path.dirname(__file__),
                                                context, local_config)

        # Initialize custom variables
        self._custom_process = [
        ]  # All the services that require custom processing

    def _service_preprocessing(self, service_request: IoServiceRequest,
                               result: Telemetry):
        """ Entry point for running a component service """
