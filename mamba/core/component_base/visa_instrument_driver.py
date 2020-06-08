""" VISA Instrument driver controller base """
from typing import Optional, Dict, Union
import os
import pyvisa

from rx import operators as op

from mamba.core.context import Context
from mamba.core.component_base import InstrumentDriver
from mamba.core.exceptions import ComponentConfigException
from mamba.core.msg import ServiceRequest, \
    ServiceResponse, Empty, ParameterInfo, ParameterType
from mamba.core.utils import path_from_string


def get_visa_sim_file(sim_path, mamba_dir) -> str:
    if sim_path is not None:
        if os.path.exists(sim_path):
            return sim_path
        elif os.path.exists(os.path.join(mamba_dir,
                                         path_from_string(sim_path))):
            return os.path.join(mamba_dir, path_from_string(sim_path))
        else:
            raise ComponentConfigException('Visa-sim file has not been found')


class VisaInstrumentDriver(InstrumentDriver):
    """ VISA Instrument driver controller class """
    def __init__(self,
                 config_folder: str,
                 context: Context,
                 local_config: Optional[dict] = None) -> None:
        super().__init__(config_folder, context, local_config)

        self._inst = None
        self._simulation_file = None

    def _close(self, rx_value: Empty) -> None:
        """ Entry point for closing application

            Args:
                rx_value: The value published by the subject.
        """
        if self._inst is not None:
            self._inst.close()
            self._inst = None

    def _visa_sim_file_validation(self) -> None:
        if self._instrument.visa_sim is not None:
            if os.path.exists(self._instrument.visa_sim):
                self._simulation_file = self._instrument.visa_sim
            elif os.path.exists(
                    os.path.join(self._context.get('mamba_dir'),
                                 path_from_string(self._instrument.visa_sim))):
                self._simulation_file = os.path.join(
                    self._context.get('mamba_dir'),
                    path_from_string(self._instrument.visa_sim))
            else:
                raise ComponentConfigException(
                    'Visa-sim file has not been found')

    def initialize(self) -> None:
        """ Entry point for component initialization """

        super().initialize()

        self._simulation_file = get_visa_sim_file(
            self._instrument.visa_sim, self._context.get('mamba_dir'))

    def _visa_connect(self, result: ServiceResponse) -> None:
        if self._instrument.visa_sim:
            self._inst = pyvisa.ResourceManager(
                f"{self._simulation_file}@sim").open_resource(
                    self._instrument.address,
                    read_termination=self._instrument.terminator_read,
                    write_termination=self._instrument.terminator_write)

            self._inst.encoding = self._instrument.encoding
        else:
            try:
                self._inst = pyvisa.ResourceManager().open_resource(
                    self._instrument.address, read_termination='\n')
            except (OSError, pyvisa.errors.VisaIOError):
                result.type = ParameterType.error
                result.value = 'Instrument is unreachable'

        if self._inst is not None:
            self._inst.timeout = 3000  # Default timeout

            if result.id in self._shared_memory_setter:
                self._shared_memory[self._shared_memory_setter[result.id]] = 1

            self._log_dev("Established connection to SMB")

    def _visa_disconnect(self, result: ServiceResponse) -> None:
        if self._inst is not None:
            self._inst.close()
            self._inst = None
            if result.id in self._shared_memory_setter:
                self._shared_memory[self._shared_memory_setter[result.id]] = 0
            self._log_dev("Closed connection to SMB")

    def _service_preprocessing(self, service_request: ServiceRequest,
                               result: ServiceResponse) -> None:
        """Perform preprocessing of the services.

        Note: This step is useful in case a merge of multiple arguments into
        one unique argument is needed. If the 'instrument_command' argument
        is not defined for the service, then no further processing will be
        done.

        Args:
            service_request: The current service request.
            result: The result to be published.
        """

    def _run_command(self, service_request: ServiceRequest) -> None:
        self._log_dev(f"Received service request: {service_request.id}")

        result = ServiceResponse(provider=self._name,
                                 id=service_request.id,
                                 type=service_request.type)

        self._service_preprocessing(service_request, result)

        if service_request.id == 'connect':
            if len(service_request.args) == 1:
                if service_request.args[0] == '1':
                    self._visa_connect(result)
                elif service_request.args[0] == '0':
                    self._visa_disconnect(result)
            else:
                result.type = ParameterType.error
                result.value = 'Wrong number of arguments'
        elif (service_request.type == ParameterType.get) and (
                service_request.id
                in self._shared_memory_getter) and self._parameter_info[
                    (service_request.id,
                     service_request.type)].get('instrument_command') is None:
            result.value = self._shared_memory[self._shared_memory_getter[
                service_request.id]]
        elif self._parameter_info[(service_request.id, service_request.type
                                   )].get('instrument_command') is None:
            pass
        elif self._inst is None:
            result.type = ParameterType.error
            result.value = 'Not possible to perform command before ' \
                           'connection is established'
        elif isinstance(
                self._parameter_info[(
                    service_request.id,
                    service_request.type)]['instrument_command'],
                list):  # Handle new format
            inst_commands = self._parameter_info[(
                service_request.id,
                service_request.type)]['instrument_command']

            param_sig = self._parameter_info[(
                service_request.id, service_request.type)]['signature'][0]

            if (len(param_sig) == 1) and (len(service_request.args) > 1):
                service_request.args = [' '.join(service_request.args)]
            elif len(param_sig) != len(service_request.args):
                result.type = ParameterType.error
                result.value = 'Wrong number or arguments for ' \
                               f'{service_request.id}.\n Expected: ' \
                               f'{param_sig};\n Received: ' \
                               f'{service_request.args}'

            for inst_cmd in inst_commands:
                cmd_type = list(inst_cmd.keys())[0]
                cmd = list(inst_cmd.values())[0]

                try:
                    if cmd_type == 'query':
                        value = self._inst.query(
                            cmd.format(*service_request.args)).replace(
                                ' ', '_')

                        if service_request.type == ParameterType.set:
                            self._shared_memory[self._shared_memory_setter[
                                service_request.id]] = value
                        else:
                            result.value = value

                    elif cmd_type == 'write':
                        self._inst.write(cmd.format(*service_request.args))

                except OSError:
                    result.type = ParameterType.error
                    result.value = 'Not possible to communicate to the' \
                                   ' instrument'
                except pyvisa.errors.VisaIOError:
                    result.type = ParameterType.error
                    result.value = 'Query timeout'

        self._context.rx['io_result'].on_next(result)
