""" VISA controller base """

import os
import pyvisa

from rx import operators as op

from mamba_server.components import ComponentBase
from mamba_server.exceptions import ComponentConfigException
from mamba_server.components.observable_types import IoServiceRequest, \
    Telemetry, Empty
from mamba_server.utils.misc import path_from_string


class VisaControllerBase(ComponentBase):
    """ VISA controller base class """
    def __init__(self, config_folder, context, local_config=None):
        super(VisaControllerBase, self).__init__(config_folder, context,
                                                 local_config)

        # Initialize observers
        self._register_observers()

        # Defined custom variables
        self._shared_memory = {}
        self._shared_memory_getter = {}
        self._shared_memory_setter = {}
        self._service_info = {}
        self._inst = None
        self._simulation_file = None

        self._custom_process = []

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

    def _visa_sim_file_validation(self):
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

    def _topics_format_validation(self):
        if not isinstance(self._configuration.get('topics'), dict):
            raise ComponentConfigException(
                'Topics configuration: wrong format')

    def initialize(self) -> None:
        """ Entry point for component initialization """

        self._topics_format_validation()
        self._visa_sim_file_validation()

        for key, service_data in self._configuration['topics'].items():
            # Create new service signature dictionary
            service_dict = {
                'description': service_data.get('description') or '',
                'signature': service_data.get('signature') or [[], None],
                'command': service_data.get('command'),
                'key': service_data.get('key'),
            }

            if not isinstance(service_dict['signature'], list) or len(
                    service_dict['signature']) != 2 or not isinstance(
                        service_dict['signature'][0], list):
                raise ComponentConfigException(
                    f'Signature of service "{key}" is invalid. Format shall'
                    f' be [[arg_1, arg_2, ...], return_type]')

            # Add new service to the component services dictionary
            self._service_info[key] = service_dict

        # Compose services signature to be published
        services_sig = {
            key: {
                'description': value['description'],
                'signature': value['signature']
            }
            for key, value in self._service_info.items()
        }

        # Compose shared memory data dictionaries
        if 'parameters' in self._configuration:
            for key, service_data in self._configuration['parameters'].items():
                # Initialize shared memory with given value, if any
                self._shared_memory[key] = service_data.get('default')

                # Compose dict assigning each getter with his memory slot
                if 'getter' in service_data:
                    for getter, value in service_data['getter'].items():
                        self._shared_memory_getter[getter] = key

                # Compose dict assigning each setter with his memory slot
                if 'setter' in service_data:
                    for setter, value in service_data['setter'].items():
                        self._shared_memory_setter[setter] = key

        # Publish services signature
        self._context.rx['io_service_signature'].on_next(services_sig)

        # Subscribe to the services request
        self._context.rx['io_service_request'].pipe(
            op.filter(lambda value: isinstance(value, IoServiceRequest) and
                      (value.id in self._service_info))).subscribe(
                          on_next=self._run_command)

    def _visa_connect(self, result: Telemetry):
        if self._configuration.get('visa-sim'):
            self._inst = pyvisa.ResourceManager(
                f"{self._simulation_file}@sim").open_resource(
                    self._configuration['resource-name'],
                    read_termination='\n')
        else:
            try:
                self._inst = pyvisa.ResourceManager().open_resource(
                    self._configuration['resource-name'],
                    read_termination='\n')
            except (OSError, pyvisa.errors.VisaIOError):
                result.type = 'error'
                result.value = 'Instrument is unreachable'

        if self._inst is not None:
            self._inst.timeout = 3000  # Default timeout

            if result.id in self._shared_memory_setter:
                self._shared_memory[self._shared_memory_setter[result.id]] = 1

            self._log_dev("Established connection to SMB")

    def _visa_disconnect(self, result: Telemetry):
        if self._inst is not None:
            self._inst.close()
            if result.id in self._shared_memory_setter:
                self._shared_memory[self._shared_memory_setter[result.id]] = 0
            self._log_dev("Closed connection to SMB")

    def _service_preprocessing(self, service_request: IoServiceRequest,
                               result: Telemetry):
        raise NotImplementedError

    def _run_command(self, service_request: IoServiceRequest):
        self._log_dev(f"Received service request: {service_request.id}")

        result = Telemetry(tm_id=service_request.id,
                           tm_type=service_request.type)

        if service_request.id in self._custom_process:
            self._service_preprocessing(service_request, result)

        if self._service_info[service_request.id].get('key') == '@connect':
            self._visa_connect(result)
        elif self._service_info[service_request.id].get(
                'key') == '@disconnect':
            self._visa_disconnect(result)
        elif service_request.id in self._shared_memory_getter:
            result.value = self._shared_memory[self._shared_memory_getter[
                service_request.id]]
        elif self._service_info[service_request.id].get('command') is None:
            if service_request.id not in self._custom_process:
                result.type = 'error'
                result.value = f'Command implementation for ' \
                               f'{service_request.id} is missing in component'
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

        self._context.rx['io_result'].on_next(result)
