""" VISA controller base """
from typing import Optional, Dict, Union
import os
import pyvisa

from rx import operators as op

from mamba.core.context import Context
from mamba.component import ComponentBase
from mamba.core.exceptions import ComponentConfigException
from mamba.core.msg import ServiceRequest, \
    ServiceResponse, Empty
from mamba.core.utils import path_from_string


class VisaInstrumentDriver(ComponentBase):
    """ VISA controller base class """
    def __init__(self,
                 config_folder: str,
                 context: Context,
                 local_config: Optional[dict] = None) -> None:
        super(VisaInstrumentDriver, self).__init__(config_folder, context,
                                                   local_config)

        # Initialize observers
        self._register_observers()

        # Defined custom variables
        self._shared_memory: Dict[str, Union[str, int, float]] = {}
        self._shared_memory_getter: Dict[str, str] = {}
        self._shared_memory_setter: Dict[str, str] = {}
        self._service_info: Dict[str, dict] = {}
        self._inst = None
        self._simulation_file = None
        self._eom_write = '\r\n'
        self._eom_read = '\n'
        self._device_encoding = 'ascii'

    def _register_observers(self) -> None:
        """ Entry point for registering component observers """

        # Quit is sent to command App finalization
        self._context.rx['quit'].pipe(
            op.filter(lambda value: isinstance(value, Empty))).subscribe(
                on_next=self._close)

    def _close(self, rx_value: Empty) -> None:
        """ Entry point for closing application

            Args:
                rx_value: The value published by the subject.
        """
        if self._inst is not None:
            self._inst.close()
            self._inst = None

    def _visa_sim_file_validation(self) -> None:
        if self._configuration.get('visa-sim') is not None:
            if os.path.exists(self._configuration['visa-sim']):
                self._simulation_file = self._configuration['visa-sim']
            elif os.path.exists(
                    os.path.join(
                        self._context.get('mamba_dir'),
                        path_from_string(self._configuration['visa-sim']))):
                self._simulation_file = os.path.join(
                    self._context.get('mamba_dir'),
                    path_from_string(self._configuration['visa-sim']))
            else:
                raise ComponentConfigException(
                    'Visa-sim file has not been found')

    def _topics_format_validation(self) -> None:
        if not isinstance(self._configuration.get('topics'), dict):
            raise ComponentConfigException(
                'Topics configuration: wrong format')

    def initialize(self) -> None:
        """ Entry point for component initialization """

        self._topics_format_validation()
        self._visa_sim_file_validation()

        try:
            self._eom_write = self._configuration['device']['eom']['write']
        except KeyError:
            pass

        try:
            self._eom_read = self._configuration['device']['eom']['read']
        except KeyError:
            pass

        try:
            self._device_encoding = self._configuration['device']['encoding']
        except KeyError:
            pass

        for key, service_data in self._configuration['topics'].items():
            # Create new service signature dictionary
            service_dict = {
                'description': service_data.get('description') or '',
                'signature': service_data.get('signature') or [[], None],
                'command': service_data.get('command')
            }

            if not isinstance(service_dict['signature'], list) or len(
                    service_dict['signature']) != 2 or not isinstance(
                        service_dict['signature'][0], list):
                raise ComponentConfigException(
                    f'Signature of service "{key}" is invalid. Format shall'
                    f' be [[arg_1, arg_2, ...], return_type]')

            # Add new service to the component services dictionary
            self._service_info[key.lower()] = service_dict

        # Compose services signature to be published
        services_sig = {
            key: {
                'description': value['description'],
                'signature': value['signature']
            }
            for key, value in self._service_info.items()
        }

        io_signatures = {'provider': self._name, 'services': services_sig}

        # Compose shared memory data dictionaries
        if 'parameters' in self._configuration:
            for key, service_data in self._configuration['parameters'].items():
                # Initialize shared memory with given value, if any
                self._shared_memory[key] = service_data.get('default')

                # Compose dict assigning each getter with his memory slot
                if 'getter' in service_data:
                    for getter, value in service_data['getter'].items():
                        self._shared_memory_getter[getter.lower()] = key

                # Compose dict assigning each setter with his memory slot
                if 'setter' in service_data:
                    for setter, value in service_data['setter'].items():
                        self._shared_memory_setter[setter.lower()] = key

        # Publish services signature
        self._context.rx['io_service_signature'].on_next(io_signatures)

        # Subscribe to the services request
        self._context.rx['io_service_request'].pipe(
            op.filter(lambda value: isinstance(value, ServiceRequest) and
                      (value.provider == self._name) and
                      (value.id in self._service_info))).subscribe(
                          on_next=self._run_command)

    def _visa_connect(self, result: ServiceResponse) -> None:
        if self._configuration.get('visa-sim'):
            self._inst = pyvisa.ResourceManager(
                f"{self._simulation_file}@sim").open_resource(
                    self._configuration['address'],
                    read_termination=self._eom_read,
                    write_termination=self._eom_write)

            self._inst.encoding = self._device_encoding
        else:
            try:
                self._inst = pyvisa.ResourceManager().open_resource(
                    self._configuration['address'], read_termination='\n')
            except (OSError, pyvisa.errors.VisaIOError):
                result.type = 'error'
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
        one unique argument is needed. If the 'command' argument is not
        defined for the service, then no further processing will be done.

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
            self._visa_connect(result)
        elif service_request.id == 'disconnect':
            self._visa_disconnect(result)
        elif service_request.id in self._shared_memory_getter:
            result.value = self._shared_memory[self._shared_memory_getter[
                service_request.id]]
        elif self._service_info[service_request.id].get('command') is None:
            pass
        elif self._inst is None:
            result.type = 'error'
            result.value = 'Not possible to perform command before ' \
                           'connection is established'
        elif self._service_info[service_request.id]['signature'][
                1] is not None and self._service_info[
                    service_request.id]['signature'][1] != 'None':
            try:
                if (len(self._service_info[service_request.id]['signature'][0])
                        == 1) and (len(service_request.args) > 1):
                    service_request.args = [' '.join(service_request.args)]

                value = self._inst.query(
                    self._service_info[service_request.id]['command'].format(
                        *service_request.args)).replace(' ', '_')

                if service_request.id in self._shared_memory_setter:
                    self._shared_memory[self._shared_memory_setter[
                        service_request.id]] = value
                else:
                    result.value = value
            except OSError:
                result.type = 'error'
                result.value = 'Not possible to communicate to the instrument'
            except pyvisa.errors.VisaIOError:
                result.type = 'error'
                result.value = 'Query timeout'
        else:
            try:
                if (len(self._service_info[service_request.id]['signature'][0])
                        == 1) and (len(service_request.args) > 1):
                    service_request.args = [' '.join(service_request.args)]

                self._inst.write(self._service_info[service_request.id]
                                 ['command'].format(*service_request.args))
            except OSError:
                result.type = 'error'
                result.value = 'Not possible to communicate to the instrument'
            except pyvisa.errors.VisaIOError:
                result.type = 'error'
                result.value = 'Write timeout'

        self._context.rx['io_result'].on_next(result)
