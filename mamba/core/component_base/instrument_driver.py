""" Instrument driver controller base """
from typing import Optional, Dict, Union, Any, Tuple

from rx import operators as op

from mamba.core.context import Context
from mamba.core.component_base import Component
from mamba.core.exceptions import ComponentConfigException
from mamba.core.msg import ServiceRequest, Empty, \
    ParameterInfo, ParameterType, ServiceResponse


class Instrument:
    def __init__(self, inst_config: dict) -> None:
        instrument_address = inst_config.get('address')
        if instrument_address is not None and isinstance(
                instrument_address, str):
            self.address: str = instrument_address
        else:
            raise ComponentConfigException(
                'Missing address in Instrument Configuration')

        self.visa_sim: Optional[str] = inst_config.get('visa_sim')
        self.encoding: str = inst_config.get('encoding') or 'ascii'
        self.terminator_write: str = inst_config.get('terminator',
                                                     {}).get('write') or '\r\n'
        self.terminator_read: str = inst_config.get('terminator',
                                                    {}).get('read') or '\n'

        self.max_connection_attempts: int = inst_config.get(
            'max_connection_attempts', 2)

        self.tc_port: Optional[int] = None
        self.tm_port: Optional[int] = None
        self.port: Optional[int] = None

        if isinstance(inst_config.get('port'), dict):
            self.tc_port = int(inst_config.get('port', {}).get('tc'))
            self.tm_port = int(inst_config.get('port', {}).get('tm'))
        else:
            self.port = int(inst_config.get('port')) if inst_config.get(
                'port') is not None else None

        self.reply_timeout: str = inst_config.get('reply_timeout') or None


def parameters_format_validation(parameters: Dict[str, dict]) -> None:
    if not isinstance(parameters, dict):
        raise ComponentConfigException(
            'Parameters configuration: wrong format')


def get_parameters(
        params_dict: Dict[str, dict],
        component_name: str) -> Dict[Tuple[str, ParameterType], dict]:
    parameters_format_validation(params_dict)

    _service_info = {}

    for key, parameter_info in params_dict.items():
        if 'get' in parameter_info:
            getter = parameter_info.get('get') or {}

            if parameter_info.get('type') is None:
                raise ComponentConfigException(
                    f'In service {component_name} : "{key}" '
                    f'parameter type is missing.')

            if getter.get('signature') is not None:
                raise ComponentConfigException(
                    f'In service {component_name} : "{key}" Signature '
                    f'for GET is still not allowed. Consider'
                    f'creating a new parameter for this.')

            if getter.get('instrument_command') is not None:
                is_query = False
                for cmd in getter.get('instrument_command', []):
                    cmd_type = list(cmd.keys())[0]
                    if cmd_type == 'query' or cmd_type == 'cyclic':
                        is_query = True
                        break
                if not is_query:
                    raise ComponentConfigException(
                        f'In service {component_name} : "{key}" Command'
                        f' for GET does not have a Query. Consider'
                        f' removing the command or adding a query')

            service_dict = {
                'description': parameter_info.get('description') or '',
                'signature': [[], parameter_info.get('type')],
                'instrument_command': getter.get('instrument_command'),
                'type': ParameterType.get,
            }

            getter_key = getter.get('alias') or key
            getter_id = getter_key.lower()

            _service_info[(getter_id, ParameterType.get)] = service_dict

        if 'set' in parameter_info:
            setter = parameter_info.get('set') or {}

            service_dict = {
                'description': parameter_info.get('description') or '',
                'signature': [setter.get('signature') or [], None],
                'instrument_command': setter.get('instrument_command'),
                'type': ParameterType.set,
            }

            if not isinstance(service_dict['signature'], list) or \
                    not isinstance(service_dict['signature'][0], list):
                raise ComponentConfigException(
                    f'Signature of service {component_name} : "{key}" is'
                    f' invalid. Format shall be [[arg_1, arg_2, ...],'
                    f' return_type]')

            setter_key = setter.get('alias') or key
            setter_id = setter_key.lower()

            # Add new service to the component services dictionary
            _service_info[(setter_id, ParameterType.set)] = service_dict

    return _service_info


class InstrumentDriver(Component):
    """ VISA controller base class """
    def __init__(self,
                 config_folder: str,
                 context: Context,
                 local_config: Optional[dict] = None) -> None:
        super().__init__(config_folder, context, local_config)

        # Initialize instrument configuration
        self._instrument = Instrument(self._configuration.get('instrument'))

        # Define parameter mapping
        self._shared_memory: Dict[str, Union[str, int, float]] = {}
        self._shared_memory_getter: Dict[str, str] = {}
        self._shared_memory_setter: Dict[str, str] = {}
        self._parameter_info: Dict[Tuple[str, ParameterType], dict] = {}
        self._inst: Optional[Any] = None

        # Initialize observers
        self._register_observers()

    def _register_observers(self) -> None:
        """ Entry point for registering component observers """

        # Quit is sent to command App finalization
        self._context.rx['quit'].subscribe(on_next=self._close)

    def _close(self, rx_value: Optional[Empty] = None) -> None:
        """ Entry point for closing application

            Args:
                rx_value: The value published by the subject.
        """
        self._instrument_disconnect()

    def initialize(self) -> None:
        """ Entry point for component initialization """

        # Compose shared memory data dictionaries
        if 'parameters' in self._configuration:
            self._parameter_info = get_parameters(
                self._configuration['parameters'], self._name)

            # Enable memory only if get is enabled, and get value is
            # not directly retrieved from instrument
            for key, parameter_info in self._configuration['parameters'].items(
            ):
                if ('get' in parameter_info
                        and (parameter_info['get']
                             or {}).get('instrument_command') is None):
                    # Initialize shared memory with given value, if any
                    self._shared_memory[key] = parameter_info.get(
                        'initial_value')
                    self._shared_memory_getter[((parameter_info.get('get')
                                                 or {}).get('alias')
                                                or key).lower()] = key
                    self._shared_memory_setter[((parameter_info.get('set')
                                                 or {}).get('alias')
                                                or key).lower()] = key

        # Compose services signature to be published
        parameter_info = [
            ParameterInfo(provider=self._name,
                          param_id=key[0],
                          param_type=key[1],
                          signature=value['signature'],
                          description=value['description'])
            for key, value in self._parameter_info.items()
        ]

        # Publish services signature
        self._context.rx['io_service_signature'].on_next(parameter_info)

        # Subscribe to the services request
        self._context.rx['io_service_request'].pipe(
            op.filter(lambda value: value.provider == self._name and (
                (value.id, value.type) in self._parameter_info))).subscribe(
                    on_next=self._run_command)

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

    def _instrument_connect(self,
                            result: Optional[ServiceResponse] = None) -> None:
        pass

    def _instrument_disconnect(self,
                               result: Optional[ServiceResponse] = None
                               ) -> None:
        pass

    def _process_inst_command(self, cmd_type: str, cmd: str,
                              service_request: ServiceRequest,
                              result: ServiceResponse) -> None:
        pass

    def _run_command(self, service_request: ServiceRequest) -> None:
        self._log_dev(f"Received service request: {service_request.id}")

        result = ServiceResponse(provider=self._name,
                                 id=service_request.id,
                                 type=service_request.type)

        self._service_preprocessing(service_request, result)

        if service_request.id == 'connect':
            if len(service_request.args) == 1:
                if service_request.args[0] == '1':
                    self._instrument_connect(result)
                elif service_request.args[0] == '0':
                    self._instrument_disconnect(result)
            else:
                result.type = ParameterType.error
                result.value = 'Wrong number of arguments'
                self._log_error(result.value)
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
            self._log_error(result.value)
        else:
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
                self._log_error(result.value)

            if result.type != ParameterType.error:
                for inst_cmd in inst_commands:
                    cmd_type = list(inst_cmd.keys())[0]
                    cmd = list(inst_cmd.values())[0]

                    self._process_inst_command(cmd_type, cmd, service_request,
                                               result)

        self._context.rx['io_result'].on_next(result)
