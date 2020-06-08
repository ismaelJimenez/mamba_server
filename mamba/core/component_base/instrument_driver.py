""" Instrument driver controller base """
from typing import Optional, Dict, Union

from rx import operators as op

from mamba.core.context import Context
from mamba.component import ComponentBase
from mamba.core.exceptions import ComponentConfigException
from mamba.core.msg import ServiceRequest, Empty, \
    ParameterInfo, ParameterType


class Instrument:
    def __init__(self, inst_config):
        if inst_config.get('address') is not None:
            self.address = inst_config.get('address')
        else:
            raise ComponentConfigException(
                'Missing address in Instrument Configuration')

        self.visa_sim = inst_config.get('visa_sim')
        self.encoding = inst_config.get('encoding') or 'ascii'
        self.terminator_write = inst_config.get('terminator',
                                                {}).get('write') or '\r\n'
        self.terminator_read = inst_config.get('terminator',
                                               {}).get('read') or '\n'

        if isinstance(inst_config.get('port'), dict):
            self.tc_port = inst_config.get('port', {}).get('tc')
            self.tm_port = inst_config.get('port', {}).get('tm')
        else:
            self.port = inst_config.get('port')


def parameters_format_validation(parameters) -> None:
    if not isinstance(parameters, dict):
        raise ComponentConfigException(
            'Parameters configuration: wrong format')


def get_parameters(params_dict, component_name) -> dict:
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
                for cmd in getter.get('instrument_command'):
                    if list(cmd.keys())[0] == 'query':
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

            if not isinstance(service_dict['signature'][0], list):
                raise ComponentConfigException(
                    f'Signature of service {component_name} : "{key}" is'
                    f' invalid. Format shall be [[arg_1, arg_2, ...],'
                    f' return_type]')

            setter_key = setter.get('alias') or key
            setter_id = setter_key.lower()

            # Add new service to the component services dictionary
            _service_info[(setter_id, ParameterType.set)] = service_dict

    return _service_info


class InstrumentDriver(ComponentBase):
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
        self._parameter_info: Dict[tuple, dict] = {}

        # Initialize observers
        self._register_observers()

    def _register_observers(self) -> None:
        """ Entry point for registering component observers """

        # Quit is sent to command App finalization
        self._context.rx['quit'].pipe(
            op.filter(lambda value: isinstance(value, Empty))).subscribe(
                on_next=self._close)

    def _close(self, rx_value: Optional[Empty] = None) -> None:
        """ Entry point for closing application

            Args:
                rx_value: The value published by the subject.
        """

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
            op.filter(lambda value: isinstance(value, ServiceRequest) and (
                value.provider == self._name) and ((
                    value.id, value.type) in self._parameter_info))).subscribe(
                        on_next=self._run_command)
