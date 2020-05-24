""" RF Signal Generator IO Controller"""
from typing import Optional, List
import os

from mamba_server.context import Context
from mamba_server.components.observable_types import IoServiceRequest,\
    Telemetry
from mamba_server.components.io_controller import VisaControllerBase


class RfSignalGenerator(VisaControllerBase):
    """ RF Signal Generator IO Controller class """
    def __init__(self,
                 context: Context,
                 local_config: Optional[dict] = None) -> None:
        super(RfSignalGenerator, self).__init__(os.path.dirname(__file__),
                                                context, local_config)

        # List of service ids that require custom processing
        self._custom_process: List[str] = []

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
