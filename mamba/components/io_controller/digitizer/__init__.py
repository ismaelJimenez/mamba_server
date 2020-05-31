""" Digitizer IO Controller"""

import os

from mamba.core.msg import IoServiceRequest,\
    Telemetry
from mamba.components.io_controller import VisaControllerBase


class Digitizer(VisaControllerBase):
    """ Digitizer IO Controller class """
    def __init__(self, context, local_config=None):
        super(Digitizer, self).__init__(os.path.dirname(__file__), context,
                                        local_config)

    def _service_preprocessing(self, service_request: IoServiceRequest,
                               result: Telemetry) -> None:
        """Perform preprocessing of the services listed in _custom_process.
        Note: This step is useful in case a merge of multiple arguments into
        one unique argument is needed. If the 'command' argument is not
        defined for the service, then no further processing will be done.
        Args:
            service_request: The current service request.
            result: The result to be published.
        """
