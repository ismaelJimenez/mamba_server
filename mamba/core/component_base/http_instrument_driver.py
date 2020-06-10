""" TCP Instrument driver controller base """
from typing import Optional
import http

from mamba.core.context import Context
from mamba.core.exceptions import ComponentConfigException
from mamba.core.component_base import InstrumentDriver
from mamba.core.msg import ServiceRequest, \
    ServiceResponse, ParameterType, Empty


class HttpInstrumentDriver(InstrumentDriver):
    """ VISA Instrument driver controller class """
    def __init__(self,
                 config_folder: str,
                 context: Context,
                 local_config: Optional[dict] = None) -> None:
        super().__init__(config_folder, context, local_config)

        if (self._instrument.port is None and self._instrument.tc_port is None
                and self._instrument.tm_port is None):
            raise ComponentConfigException(
                'Missing port in Instrument Configuration')

    def initialize(self) -> None:
        super().initialize()
        self._inst = 0

    def _process_inst_command(self, cmd_type: str, cmd: str,
                              service_request: ServiceRequest,
                              result: ServiceResponse) -> None:
        try:
            conn = http.client.HTTPConnection(self._instrument.address,
                                              self._instrument.port)
            if cmd_type == 'query':
                conn.request(
                    "GET", f"/query?param={cmd.format(*service_request.args)}")
                response = conn.getresponse()
                value = response.read().decode(self._instrument.encoding)

                if service_request.type == ParameterType.set:
                    self._shared_memory[self._shared_memory_setter[
                        service_request.id]] = value
                else:
                    result.value = value

            elif cmd_type == 'write':
                conn.request(
                    "PUT", f"/write?param={cmd.format(*service_request.args)}")

        except ConnectionRefusedError:
            result.type = ParameterType.error
            result.value = 'Not possible to communicate to the' \
                           ' instrument'
            self._log_error(result.value)
