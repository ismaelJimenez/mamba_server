""" TCP Instrument driver controller base """
from typing import Optional
import xmlrpc

from mamba.core.context import Context
from mamba.core.exceptions import ComponentConfigException
from mamba.core.component_base import InstrumentDriver
from mamba.core.msg import ServiceRequest, \
    ServiceResponse, ParameterType, Empty


class XmlRpcInstrumentDriver(InstrumentDriver):
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

    def _instrument_connect(self,
                            result: Optional[ServiceResponse] = None) -> None:
        try:
            server_addr = f'http://{self._instrument.address}:' \
                          f'{self._instrument.port}'
            self._inst = xmlrpc.client.ServerProxy(server_addr)

            if result.id in self._shared_memory_setter:
                self._shared_memory[self._shared_memory_setter[result.id]] = 1

            self._log_dev("Established connection to Instrument")

        except ConnectionRefusedError:
            error = 'Instrument is unreachable'
            if result is not None:
                result.type = ParameterType.error
                result.value = error
            self._log_error(error)

    def _instrument_disconnect(self,
                               result: Optional[ServiceResponse] = None
                               ) -> None:
        if self._inst is not None:
            self._inst = None

            if result is not None and result.id in self._shared_memory_setter:
                self._shared_memory[self._shared_memory_setter[result.id]] = 0
            self._log_dev("Closed connection to Instrument")

    def _process_inst_command(self, cmd_type: str, cmd: str,
                              service_request: ServiceRequest,
                              result: ServiceResponse) -> None:
        if self._inst is not None:
            try:
                if cmd_type == 'query':
                    value = self._inst.query(cmd.format(*service_request.args))

                    if service_request.type == ParameterType.set:
                        self._shared_memory[self._shared_memory_setter[
                            service_request.id]] = value
                    else:
                        result.value = value

                elif cmd_type == 'write':
                    self._inst.write(cmd.format(*service_request.args))

            except ConnectionRefusedError:
                result.type = ParameterType.error
                result.value = 'Not possible to communicate to the' \
                               ' instrument'
                self._log_error(result.value)
        else:
            result.type = ParameterType.error
            result.value = 'Not possible to perform command before ' \
                           'connection is established'
            self._log_error(result.value)
