""" VISA Instrument driver controller base """
from typing import Optional
import os
import pyvisa

from mamba.core.context import Context
from mamba.core.component_base import InstrumentDriver
from mamba.core.exceptions import ComponentConfigException
from mamba.core.msg import ServiceRequest, Empty, \
    ServiceResponse, ParameterType
from mamba.core.utils import path_from_string


def get_visa_sim_file(sim_path: Optional[str],
                      mamba_dir: str) -> Optional[str]:
    sim_file = None
    if sim_path is not None:
        if os.path.exists(sim_path):
            sim_file = sim_path
        elif os.path.exists(os.path.join(mamba_dir,
                                         path_from_string(sim_path))):
            sim_file = os.path.join(mamba_dir, path_from_string(sim_path))
        else:
            raise ComponentConfigException('Visa-sim file has not been found')

    return sim_file


class VisaInstrumentDriver(InstrumentDriver):
    """ VISA Instrument driver controller class """
    def __init__(self,
                 config_folder: str,
                 context: Context,
                 local_config: Optional[dict] = None) -> None:
        super().__init__(config_folder, context, local_config)

        self._simulation_file: Optional[str] = None
        self._inst: Optional[pyvisa.ResourceManager] = None

    def initialize(self) -> None:
        """ Entry point for component initialization """
        super().initialize()

        self._simulation_file = get_visa_sim_file(
            self._instrument.visa_sim, self._context.get('mamba_dir'))

    def _instrument_connect(self,
                            result: Optional[ServiceResponse] = None) -> None:
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
                error = 'Instrument is unreachable'
                if result is not None:
                    result.type = ParameterType.error
                    result.value = error
                self._log_error(error)

        if self._inst is not None:
            self._inst.timeout = 3000  # Default timeout

            if result is not None and result.id in self._shared_memory_setter:
                self._shared_memory[self._shared_memory_setter[result.id]] = 1

            self._log_dev("Established connection to Instrument")

    def _instrument_disconnect(self,
                               result: Optional[ServiceResponse] = None
                               ) -> None:
        if self._inst is not None:
            self._inst.close()
            self._inst = None
            if result is not None and result.id in self._shared_memory_setter:
                self._shared_memory[self._shared_memory_setter[result.id]] = 0
            self._log_dev("Closed connection to Instrument")

    def _process_inst_command(self, cmd_type: str, cmd: str,
                              service_request: ServiceRequest,
                              result: ServiceResponse) -> None:
        if self._inst is not None:
            try:
                a = cmd.format(*service_request.args)
                if cmd_type == 'query':
                    value = self._inst.query(
                        cmd.format(*service_request.args)).replace(' ', '_')

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
                self._log_error(result.value)
            except pyvisa.errors.VisaIOError:
                result.type = ParameterType.error
                result.value = 'Query timeout'
                self._log_error(result.value)
        else:
            result.type = ParameterType.error
            result.value = 'Not possible to perform command before ' \
                           'connection is established'
            self._log_error(result.value)
