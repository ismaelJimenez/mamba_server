import os
import pytest
import copy
import time
from tempfile import NamedTemporaryFile

from rx import operators as op

from mamba.core.testing.utils import compose_service_info, get_config_dict, CallbackTestClass, get_provider_params_info
from mamba.core.context import Context
from mamba.component.instrument_driver.switch_matrix import SwitchMatrixKsZ2091c
from mamba.core.exceptions import ComponentConfigException
from mamba.core.msg import Empty, ServiceRequest, ServiceResponse, ParameterType

component_path = os.path.join('component', 'instrument_driver',
                              'switch_matrix', 'ks_z2091c')


class TestClass:
    def setup_class(self):
        """ setup_class called once for the class """
        self.mamba_path = os.path.join(os.path.dirname(__file__), '..', '..',
                                       '..', 'mamba')

        self.default_component_config = get_config_dict(
            os.path.join(self.mamba_path, component_path, 'config.yml'))

        self.default_service_info = compose_service_info(
            self.default_component_config)

    def teardown_class(self):
        """ teardown_class called once for the class """
        pass

    def setup_method(self):
        """ setup_method called for every method """
        self.context = Context()
        self.context.set(
            'mamba_dir',
            os.path.join(os.path.dirname(__file__), '..', '..', '..', 'mamba'))

    def teardown_method(self):
        """ teardown_method called for every method """
        del self.context

    def test_wo_context(self):
        """ Test component behaviour without required context """
        with pytest.raises(TypeError) as excinfo:
            SwitchMatrixKsZ2091c()

        assert "missing 1 required positional argument" in str(excinfo.value)

    def test_w_default_context_component_creation(self):
        """ Test component creation behaviour with default context """
        component = SwitchMatrixKsZ2091c(self.context)

        # Test default configuration load
        assert component._configuration == self.default_component_config

        # Test custom variables default values
        assert component._shared_memory == {}
        assert component._shared_memory_getter == {}
        assert component._shared_memory_setter == {}
        assert component._parameter_info == {}
        assert component._inst is None
        assert component._simulation_file is None

        assert component._instrument.address == 'TCPIP0::1.2.3.4::INSTR'
        assert component._instrument.visa_sim == 'mock/visa/switch_matrix/ks_z2091c.yml'
        assert component._instrument.encoding == 'ascii'
        assert component._instrument.terminator_write == '\r\n'
        assert component._instrument.terminator_read == '\n'

    def test_w_default_context_component_initialization(self):
        """ Test component initialization behaviour with default context """
        component = SwitchMatrixKsZ2091c(self.context)
        component.initialize()

        # Test default configuration load
        assert component._configuration == self.default_component_config

        # Test custom variables default values
        assert component._shared_memory == {
            'connected': False,
            'raw_query': '',
            'path_define_get': None,
            'route_close_get': None
        }
        assert component._shared_memory_getter == {
            'connected': 'connected',
            'raw_query': 'raw_query',
            'path_define_get': 'path_define_get',
            'route_close_get': 'route_close_get'
        }
        assert component._shared_memory_setter == {
            'connect': 'connected',
            'raw_query': 'raw_query',
            'path_define_get': 'path_define_get',
            'route_close_get': 'route_close_get'
        }
        assert component._parameter_info == self.default_service_info
        assert component._inst is None
        assert 'ks_z2091c.yml' in component._simulation_file

        assert component._instrument.address == 'TCPIP0::1.2.3.4::INSTR'
        assert component._instrument.visa_sim == 'mock/visa/switch_matrix/ks_z2091c.yml'
        assert component._instrument.encoding == 'ascii'
        assert component._instrument.terminator_write == '\r\n'
        assert component._instrument.terminator_read == '\n'

    def test_visa_sim_local_from_project_folder(self):
        """ Test component creation behaviour with default context """
        temp_file = NamedTemporaryFile(delete=False)

        temp_file_folder = temp_file.name.rsplit('/', 1)[0]
        temp_file_name = temp_file.name.rsplit('/', 1)[1]

        os.chdir(temp_file_folder)

        component = SwitchMatrixKsZ2091c(
            self.context,
            local_config={'instrument': {
                'visa_sim': temp_file_name
            }})
        component.initialize()

        assert temp_file_name in component._simulation_file

        temp_file.close()

    def test_visa_sim_mamba_from_project_folder(self):
        """ Test component creation behaviour with default context """
        os.chdir('/tmp')

        component = SwitchMatrixKsZ2091c(self.context)
        component.initialize()

        assert 'ks_z2091c.yml' in component._simulation_file

    def test_w_custom_context(self):
        """ Test component creation behaviour with default context """
        component = SwitchMatrixKsZ2091c(
            self.context,
            local_config={
                'name': 'custom_name',
                'instrument': {
                    'visa_sim': None
                },
                'parameters': {
                    'new_param': {
                        'description': 'New parameter description',
                        'set': {
                            'signature': [{
                                'param_1': {
                                    type: str
                                }
                            }],
                            'instrument_command': [{
                                'write': '{:}'
                            }]
                        },
                    }
                }
            })
        component.initialize()

        custom_component_config = copy.deepcopy(self.default_component_config)
        custom_component_config['name'] = 'custom_name'
        custom_component_config['instrument']['visa_sim'] = None
        custom_component_config['parameters']['new_param'] = {
            'description': 'New parameter description',
            'set': {
                'signature': [{
                    'param_1': {
                        type: str
                    }
                }],
                'instrument_command': [{
                    'write': '{:}'
                }]
            },
        }

        # Test default configuration load
        assert component._configuration == custom_component_config

        # Test custom variables default values
        assert component._shared_memory == {
            'connected': False,
            'raw_query': '',
            'path_define_get': None,
            'route_close_get': None
        }
        assert component._shared_memory_getter == {
            'connected': 'connected',
            'raw_query': 'raw_query',
            'path_define_get': 'path_define_get',
            'route_close_get': 'route_close_get'
        }
        assert component._shared_memory_setter == {
            'connect': 'connected',
            'raw_query': 'raw_query',
            'path_define_get': 'path_define_get',
            'route_close_get': 'route_close_get'
        }

        custom_service_info = compose_service_info(custom_component_config)
        assert component._parameter_info == custom_service_info
        assert component._inst is None
        assert component._simulation_file is None

    def test_w_wrong_custom_context(self):
        """ Test component creation behaviour with default context """

        # Test with wrong topics dictionary
        with pytest.raises(ComponentConfigException) as excinfo:
            SwitchMatrixKsZ2091c(self.context,
                                 local_config={
                                     'parameters': 'wrong'
                                 }).initialize()
        assert "Parameters configuration: wrong format" in str(excinfo.value)

        # In case no new topics are given, use the default ones
        component = SwitchMatrixKsZ2091c(self.context,
                                         local_config={'parameters': {}})
        component.initialize()

        assert component._configuration == self.default_component_config

        # Test with missing simulation file
        with pytest.raises(ComponentConfigException) as excinfo:
            SwitchMatrixKsZ2091c(self.context,
                                 local_config={
                                     'instrument': {
                                         'visa_sim': 'non-existing'
                                     }
                                 }).initialize()
        assert "Visa-sim file has not been found" in str(excinfo.value)

        # Test case properties do not have a getter, setter or default
        component = SwitchMatrixKsZ2091c(
            self.context, local_config={'parameters': {
                'new_param': {}
            }})
        component.initialize()

        assert component._shared_memory == {
            'connected': False,
            'raw_query': '',
            'path_define_get': None,
            'route_close_get': None
        }

    def test_io_signature_publication(self):
        """ Test component io_signature observable """
        dummy_test_class = CallbackTestClass()

        # Subscribe to the topic that shall be published
        self.context.rx['io_service_signature'].subscribe(
            dummy_test_class.test_func_1)

        component = SwitchMatrixKsZ2091c(self.context)
        component.initialize()

        time.sleep(.1)

        assert dummy_test_class.func_1_times_called == 1

        received_params_info = str([
            str(parameter_info)
            for parameter_info in dummy_test_class.func_1_last_value
        ])
        expected_params_info = str([
            str(parameter_info) for parameter_info in get_provider_params_info(
                self.default_component_config, self.default_service_info)
        ])
        assert received_params_info == expected_params_info

        component = SwitchMatrixKsZ2091c(
            self.context,
            local_config={
                'name': 'custom_name',
                'instrument': {
                    'visa_sim': None
                },
                'parameters': {
                    'new_param': {
                        'description': 'New parameter description',
                        'set': {
                            'signature': [{
                                'param_1': {
                                    type: str
                                }
                            }],
                            'instrument_command': [{
                                'write': '{:}'
                            }]
                        },
                    }
                }
            })
        component.initialize()

        time.sleep(.1)

        assert dummy_test_class.func_1_times_called == 2

        custom_component_config = copy.deepcopy(self.default_component_config)
        custom_component_config['name'] = 'custom_name'
        custom_component_config['instrument']['visa_sim'] = None
        parameters = {
            'new_param': {
                'description': 'New parameter description',
                'set': {
                    'signature': [{
                        'param_1': {
                            type: str
                        }
                    }],
                    'instrument_command': [{
                        'write': '{:}'
                    }]
                },
            }
        }
        parameters.update(custom_component_config['parameters'])
        custom_component_config['parameters'] = parameters

        custom_service_info = compose_service_info(custom_component_config)

        received_params_info = str([
            str(parameter_info)
            for parameter_info in dummy_test_class.func_1_last_value
        ])
        expected_params_info = str([
            str(parameter_info) for parameter_info in get_provider_params_info(
                custom_component_config, custom_service_info)
        ])

        assert received_params_info == expected_params_info

    def test_io_service_request_observer(self):
        """ Test component io_service_request observer """
        component = SwitchMatrixKsZ2091c(self.context)
        component.initialize()
        dummy_test_class = CallbackTestClass()

        # Subscribe to the topic that shall be published
        self.context.rx['io_result'].pipe(
            op.filter(
                lambda value: isinstance(value, ServiceResponse))).subscribe(
                    dummy_test_class.test_func_1)

        # 1 - Test that component only gets activated for implemented services
        self.context.rx['io_service_request'].on_next(
            ServiceRequest(provider='keysight_z2091c_smart_switch_matrix',
                           id='NOT_EXISTING',
                           type='any',
                           args=[]))

        assert dummy_test_class.func_1_times_called == 0
        assert dummy_test_class.func_1_last_value is None

        self.context.rx['io_service_request'].on_next(
            ServiceRequest(provider='NOT_EXISTING',
                           id='connect',
                           type='any',
                           args=[]))

        assert dummy_test_class.func_1_times_called == 0
        assert dummy_test_class.func_1_last_value is None

        # 2 - Test generic command before connection to the instrument has been established
        self.context.rx['io_service_request'].on_next(
            ServiceRequest(provider='keysight_z2091c_smart_switch_matrix',
                           id='idn',
                           type=ParameterType.get,
                           args=[]))

        time.sleep(.1)

        assert dummy_test_class.func_1_times_called == 1
        assert dummy_test_class.func_1_last_value.id == 'idn'
        assert dummy_test_class.func_1_last_value.type == ParameterType.error
        assert dummy_test_class.func_1_last_value.value == 'Not possible to perform command before connection is established'

        # 3 - Test connection to the instrument
        assert component._inst is None

        self.context.rx['io_service_request'].on_next(
            ServiceRequest(provider='keysight_z2091c_smart_switch_matrix',
                           id='connect',
                           type=ParameterType.set,
                           args=['1']))

        time.sleep(.1)

        assert component._inst is not None
        assert dummy_test_class.func_1_times_called == 2
        assert dummy_test_class.func_1_last_value.id == 'connect'
        assert dummy_test_class.func_1_last_value.type == ParameterType.set
        assert dummy_test_class.func_1_last_value.value is None

        # 4 - Test no system errors
        self.context.rx['io_service_request'].on_next(
            ServiceRequest(provider='keysight_z2091c_smart_switch_matrix',
                           id='sys_err',
                           type=ParameterType.get))

        time.sleep(.1)

        assert dummy_test_class.func_1_times_called == 3
        assert dummy_test_class.func_1_last_value.id == 'sys_err'
        assert dummy_test_class.func_1_last_value.type == ParameterType.get
        assert dummy_test_class.func_1_last_value.value == '0,_No_Error'

        # 5 - Test generic command
        self.context.rx['io_service_request'].on_next(
            ServiceRequest(provider='keysight_z2091c_smart_switch_matrix',
                           id='clear',
                           type=ParameterType.set,
                           args=[]))

        time.sleep(.1)

        assert dummy_test_class.func_1_times_called == 4
        assert dummy_test_class.func_1_last_value.id == 'clear'
        assert dummy_test_class.func_1_last_value.type == ParameterType.set
        assert dummy_test_class.func_1_last_value.value is None

        # 6 - Test generic query
        self.context.rx['io_service_request'].on_next(
            ServiceRequest(provider='keysight_z2091c_smart_switch_matrix',
                           id='idn',
                           type=ParameterType.get,
                           args=[]))

        time.sleep(.1)

        assert dummy_test_class.func_1_times_called == 5
        assert dummy_test_class.func_1_last_value.id == 'idn'
        assert dummy_test_class.func_1_last_value.type == ParameterType.get
        assert dummy_test_class.func_1_last_value.value == 'Keysight_Technologies,Z2091C-001,US56400131,1.1.6450.15113'

        # 7 - Test shared memory set
        assert component._shared_memory == {
            'connected': 1,
            'raw_query': '',
            'route_close_get': None,
            'path_define_get': None
        }

        self.context.rx['io_service_request'].on_next(
            ServiceRequest(provider='keysight_z2091c_smart_switch_matrix',
                           id='raw_query',
                           type=ParameterType.set,
                           args=['*IDN?']))

        time.sleep(.1)

        assert component._shared_memory == {
            'connected': 1,
            'raw_query':
            'Keysight_Technologies,Z2091C-001,US56400131,1.1.6450.15113',
            'route_close_get': None,
            'path_define_get': None
        }

        assert dummy_test_class.func_1_times_called == 6
        assert dummy_test_class.func_1_last_value.id == 'raw_query'
        assert dummy_test_class.func_1_last_value.type == ParameterType.set
        assert dummy_test_class.func_1_last_value.value is None

        # 8 - Test shared memory get
        self.context.rx['io_service_request'].on_next(
            ServiceRequest(provider='keysight_z2091c_smart_switch_matrix',
                           id='raw_query',
                           type=ParameterType.get,
                           args=[]))

        time.sleep(.1)

        assert dummy_test_class.func_1_times_called == 7
        assert dummy_test_class.func_1_last_value.id == 'raw_query'
        assert dummy_test_class.func_1_last_value.type == ParameterType.get
        assert dummy_test_class.func_1_last_value.value == 'Keysight_Technologies,Z2091C-001,US56400131,1.1.6450.15113'

        # 9 - Test special case of msg command with multiple args
        self.context.rx['io_service_request'].on_next(
            ServiceRequest(provider='keysight_z2091c_smart_switch_matrix',
                           id='raw_write',
                           type=ParameterType.set,
                           args=['CONF:DIG:WIDTH', 'WORD,', '(@2001)']))

        time.sleep(.1)

        assert dummy_test_class.func_1_times_called == 8
        assert dummy_test_class.func_1_last_value.id == 'raw_write'
        assert dummy_test_class.func_1_last_value.type == ParameterType.set
        assert dummy_test_class.func_1_last_value.value is None

        self.context.rx['io_service_request'].on_next(
            ServiceRequest(provider='keysight_z2091c_smart_switch_matrix',
                           id='raw_query',
                           type=ParameterType.set,
                           args=['CONF:DIG:WIDTH?', '(@2001)']))

        time.sleep(.1)

        assert component._shared_memory == {
            'connected': 1,
            'raw_query': 'WORD',
            'route_close_get': None,
            'path_define_get': None
        }

        self.context.rx['io_service_request'].on_next(
            ServiceRequest(provider='keysight_z2091c_smart_switch_matrix',
                           id='raw_query',
                           type=ParameterType.get,
                           args=[]))

        time.sleep(.1)

        assert dummy_test_class.func_1_times_called == 10
        assert dummy_test_class.func_1_last_value.id == 'raw_query'
        assert dummy_test_class.func_1_last_value.type == ParameterType.get
        assert dummy_test_class.func_1_last_value.value == 'WORD'

        # 10 - Test specific comamnds
        self.context.rx['io_service_request'].on_next(
            ServiceRequest(provider='keysight_z2091c_smart_switch_matrix',
                           id='opc',
                           type=ParameterType.get,
                           args=[]))

        time.sleep(.1)

        assert dummy_test_class.func_1_times_called == 11
        assert dummy_test_class.func_1_last_value.id == 'opc'
        assert dummy_test_class.func_1_last_value.type == ParameterType.get
        assert dummy_test_class.func_1_last_value.value == '1'

        self.context.rx['io_service_request'].on_next(
            ServiceRequest(provider='keysight_z2091c_smart_switch_matrix',
                           id='reset',
                           type=ParameterType.set,
                           args=[]))

        time.sleep(.1)

        assert dummy_test_class.func_1_times_called == 12
        assert dummy_test_class.func_1_last_value.id == 'reset'
        assert dummy_test_class.func_1_last_value.type == ParameterType.set
        assert dummy_test_class.func_1_last_value.value is None

        self.context.rx['io_service_request'].on_next(
            ServiceRequest(provider='keysight_z2091c_smart_switch_matrix',
                           id='route_close_set',
                           type=ParameterType.set,
                           args=['SW5(3), ATT2(25), 1104, MyPath2']))

        time.sleep(.1)

        assert dummy_test_class.func_1_times_called == 13
        assert dummy_test_class.func_1_last_value.id == 'route_close_set'
        assert dummy_test_class.func_1_last_value.type == ParameterType.set
        assert dummy_test_class.func_1_last_value.value is None

        self.context.rx['io_service_request'].on_next(
            ServiceRequest(provider='keysight_z2091c_smart_switch_matrix',
                           id='route_close_get',
                           type=ParameterType.set,
                           args=['SW5(3), ATT2(25), 1104, MyPath2']))

        time.sleep(.1)

        assert dummy_test_class.func_1_times_called == 14
        assert dummy_test_class.func_1_last_value.id == 'route_close_get'
        assert dummy_test_class.func_1_last_value.type == ParameterType.set
        assert dummy_test_class.func_1_last_value.value is None

        self.context.rx['io_service_request'].on_next(
            ServiceRequest(provider='keysight_z2091c_smart_switch_matrix',
                           id='route_close_get',
                           type=ParameterType.get,
                           args=[]))

        time.sleep(.1)

        assert dummy_test_class.func_1_times_called == 15
        assert dummy_test_class.func_1_last_value.id == 'route_close_get'
        assert dummy_test_class.func_1_last_value.type == ParameterType.get
        assert dummy_test_class.func_1_last_value.value == '1,0,1,1'

        self.context.rx['io_service_request'].on_next(
            ServiceRequest(provider='keysight_z2091c_smart_switch_matrix',
                           id='path_catalog',
                           type=ParameterType.get,
                           args=[]))

        time.sleep(.1)

        assert dummy_test_class.func_1_times_called == 16
        assert dummy_test_class.func_1_last_value.id == 'path_catalog'
        assert dummy_test_class.func_1_last_value.type == ParameterType.get
        assert dummy_test_class.func_1_last_value.value == '"MYPATH1","MYPATH2"'

        self.context.rx['io_service_request'].on_next(
            ServiceRequest(provider='keysight_z2091c_smart_switch_matrix',
                           id='path_delete',
                           type=ParameterType.set,
                           args=['MyPath2']))

        time.sleep(.1)

        assert dummy_test_class.func_1_times_called == 17
        assert dummy_test_class.func_1_last_value.id == 'path_delete'
        assert dummy_test_class.func_1_last_value.type == ParameterType.set
        assert dummy_test_class.func_1_last_value.value is None

        self.context.rx['io_service_request'].on_next(
            ServiceRequest(provider='keysight_z2091c_smart_switch_matrix',
                           id='path_define_set',
                           type=ParameterType.set,
                           args=['MyPath1', 'SW1(3),SW2(1)']))

        time.sleep(.1)

        assert dummy_test_class.func_1_times_called == 18
        assert dummy_test_class.func_1_last_value.id == 'path_define_set'
        assert dummy_test_class.func_1_last_value.type == ParameterType.set
        assert dummy_test_class.func_1_last_value.value is None

        self.context.rx['io_service_request'].on_next(
            ServiceRequest(provider='keysight_z2091c_smart_switch_matrix',
                           id='path_define_get',
                           type=ParameterType.set,
                           args=['MyPath1']))

        time.sleep(.1)

        assert dummy_test_class.func_1_times_called == 19
        assert dummy_test_class.func_1_last_value.id == 'path_define_get'
        assert dummy_test_class.func_1_last_value.type == ParameterType.set
        assert dummy_test_class.func_1_last_value.value is None

        self.context.rx['io_service_request'].on_next(
            ServiceRequest(provider='keysight_z2091c_smart_switch_matrix',
                           id='path_define_get',
                           type=ParameterType.get,
                           args=[]))

        time.sleep(.1)

        assert dummy_test_class.func_1_times_called == 20
        assert dummy_test_class.func_1_last_value.id == 'path_define_get'
        assert dummy_test_class.func_1_last_value.type == ParameterType.get
        assert dummy_test_class.func_1_last_value.value == '(@SW1(3),SW2(A))'

        # # 10 - Test no system errors
        self.context.rx['io_service_request'].on_next(
            ServiceRequest(provider='keysight_z2091c_smart_switch_matrix',
                           id='sys_err',
                           type=ParameterType.get))

        time.sleep(.1)

        assert dummy_test_class.func_1_times_called == 21
        assert dummy_test_class.func_1_last_value.id == 'sys_err'
        assert dummy_test_class.func_1_last_value.type == ParameterType.get
        assert dummy_test_class.func_1_last_value.value == '0,_No_Error'

        # 11 - Test disconnection to the instrument
        self.context.rx['io_service_request'].on_next(
            ServiceRequest(provider='keysight_z2091c_smart_switch_matrix',
                           id='connect',
                           type=ParameterType.set,
                           args=['0']))

        time.sleep(.1)

        assert component._inst is None
        assert dummy_test_class.func_1_times_called == 22
        assert dummy_test_class.func_1_last_value.id == 'connect'
        assert dummy_test_class.func_1_last_value.type == ParameterType.set
        assert dummy_test_class.func_1_last_value.value is None

        self.context.rx['io_service_request'].on_next(
            ServiceRequest(provider='keysight_z2091c_smart_switch_matrix',
                           id='connected',
                           type=ParameterType.get,
                           args=[]))

        time.sleep(.1)

        assert component._inst is None
        assert dummy_test_class.func_1_times_called == 23
        assert dummy_test_class.func_1_last_value.id == 'connected'
        assert dummy_test_class.func_1_last_value.type == ParameterType.get
        assert dummy_test_class.func_1_last_value.value == 0

    def test_connection_visa_sim_wrong_instrument_address(self):
        dummy_test_class = CallbackTestClass()

        # Subscribe to the topic that shall be published
        self.context.rx['io_result'].pipe(
            op.filter(
                lambda value: isinstance(value, ServiceResponse))).subscribe(
                    dummy_test_class.test_func_1)

        # Test simulated normal connection to the instrument
        component = SwitchMatrixKsZ2091c(
            self.context,
            local_config={'instrument': {
                'address': 'TCPIP0::4.3.2.1::INSTR'
            }})
        component.initialize()

        assert component._inst is None

        self.context.rx['io_service_request'].on_next(
            ServiceRequest(provider='keysight_z2091c_smart_switch_matrix',
                           id='connect',
                           type=ParameterType.set,
                           args=['1']))

        time.sleep(.1)

        assert dummy_test_class.func_1_times_called == 1
        assert dummy_test_class.func_1_last_value.id == 'connect'
        assert dummy_test_class.func_1_last_value.type == ParameterType.set
        assert dummy_test_class.func_1_last_value.value is None

    def test_disconnection_w_no_connection(self):
        dummy_test_class = CallbackTestClass()

        # Subscribe to the topic that shall be published
        self.context.rx['io_result'].pipe(
            op.filter(
                lambda value: isinstance(value, ServiceResponse))).subscribe(
                    dummy_test_class.test_func_1)

        # Test real connection to missing instrument
        component = SwitchMatrixKsZ2091c(self.context)
        component.initialize()

        assert component._inst is None

        self.context.rx['io_service_request'].on_next(
            ServiceRequest(provider='keysight_z2091c_smart_switch_matrix',
                           id='connect',
                           type=ParameterType.set,
                           args=['0']))

        time.sleep(.1)

        assert component._inst is None
        assert dummy_test_class.func_1_times_called == 1
        assert dummy_test_class.func_1_last_value.id == 'connect'
        assert dummy_test_class.func_1_last_value.type == ParameterType.set
        assert dummy_test_class.func_1_last_value.value is None

    def test_service_invalid_info(self):
        with pytest.raises(ComponentConfigException) as excinfo:
            SwitchMatrixKsZ2091c(self.context,
                                 local_config={
                                     'parameters': {
                                         'new_param': {
                                             'type': 'str',
                                             'description':
                                             'New parameter description',
                                             'set': {
                                                 'signature':
                                                 'wrong',
                                                 'instrument_command': [{
                                                     'write':
                                                     '{:}'
                                                 }]
                                             },
                                         }
                                     }
                                 }).initialize()

        assert '"new_param" is invalid. Format shall' \
               ' be [[arg_1, arg_2, ...], return_type]' in str(excinfo.value)

        with pytest.raises(ComponentConfigException) as excinfo:
            SwitchMatrixKsZ2091c(self.context,
                                 local_config={
                                     'parameters': {
                                         'new_param': {
                                             'type': 'str',
                                             'description':
                                             'New parameter description',
                                             'get': {
                                                 'signature': [{
                                                     'arg': {
                                                         'type': 'str'
                                                     }
                                                 }],
                                                 'instrument_command': [{
                                                     'write':
                                                     '{:}'
                                                 }]
                                             },
                                         }
                                     }
                                 }).initialize()

        assert '"new_param" Signature for GET is still not allowed' in str(
            excinfo.value)

        with pytest.raises(ComponentConfigException) as excinfo:
            SwitchMatrixKsZ2091c(self.context,
                                 local_config={
                                     'parameters': {
                                         'new_param': {
                                             'type': 'str',
                                             'description':
                                             'New parameter description',
                                             'get': {
                                                 'instrument_command': [{
                                                     'write':
                                                     '{:}'
                                                 }]
                                             },
                                         }
                                     }
                                 }).initialize()

        assert '"new_param" Command for GET does not have a Query' in str(
            excinfo.value)

        with pytest.raises(ComponentConfigException) as excinfo:
            SwitchMatrixKsZ2091c(self.context,
                                 local_config={
                                     'parameters': {
                                         'new_param': {
                                             'description':
                                             'New parameter description',
                                             'get': {
                                                 'instrument_command': [{
                                                     'write':
                                                     '{:}'
                                                 }]
                                             },
                                         }
                                     }
                                 }).initialize()

        assert '"new_param" parameter type is missing' in str(excinfo.value)

    def test_connection_cases_normal_fail(self):
        dummy_test_class = CallbackTestClass()

        # Subscribe to the topic that shall be published
        self.context.rx['io_result'].pipe(
            op.filter(
                lambda value: isinstance(value, ServiceResponse))).subscribe(
                    dummy_test_class.test_func_1)

        # Test real connection to missing instrument
        component = SwitchMatrixKsZ2091c(
            self.context, local_config={'instrument': {
                'visa_sim': None
            }})
        component.initialize()

        assert component._inst is None

        self.context.rx['io_service_request'].on_next(
            ServiceRequest(provider='keysight_z2091c_smart_switch_matrix',
                           id='connect',
                           type=ParameterType.set,
                           args=['1']))

        time.sleep(.1)

        assert component._inst is None
        assert dummy_test_class.func_1_times_called == 1
        assert dummy_test_class.func_1_last_value.id == 'connect'
        assert dummy_test_class.func_1_last_value.type == ParameterType.error
        assert dummy_test_class.func_1_last_value.value == 'Instrument is unreachable'

    def test_quit_observer(self):
        """ Test component quit observer """
        class Test:
            called = False

            def close(self):
                self.called = True

        component = SwitchMatrixKsZ2091c(self.context)
        component.initialize()

        # Test quit while on load window
        component._inst = Test()

        assert not component._inst.called

        self.context.rx['quit'].on_next(Empty())

        # Test connection to the instrument has been closed
        assert component._inst is None
