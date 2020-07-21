import os
import pytest
import copy
import time
from tempfile import NamedTemporaryFile

from rx import operators as op

from mamba.core.testing.utils import compose_service_info, get_config_dict, CallbackTestClass, get_provider_params_info
from mamba.core.context import Context
from mamba.marketplace.components.power_supply.keysight_n5700 import PowerSupplyKsN5700
from mamba.core.exceptions import ComponentConfigException
from mamba.core.msg import Empty, ServiceRequest, ServiceResponse, ParameterType

component_path = os.path.join('marketplace', 'components', 'power_supply',
                              'keysight_n5700')


class TestClass:
    def setup_class(self):
        """ setup_class called once for the class """
        self.mamba_path = os.path.join(os.path.dirname(__file__), '..', '..',
                                       '..', '..', '..', 'mamba')

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
            os.path.join(os.path.dirname(__file__), '..', '..', '..', '..',
                         '..', 'mamba'))

    def teardown_method(self):
        """ teardown_method called for every method """
        del self.context

    def test_wo_context(self):
        """ Test component behaviour without required context """
        with pytest.raises(TypeError) as excinfo:
            PowerSupplyKsN5700()

        assert "missing 1 required positional argument" in str(excinfo.value)

    def test_w_default_context_component_creation(self):
        """ Test component creation behaviour with default context """
        component = PowerSupplyKsN5700(self.context)

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
        assert component._instrument.visa_sim == 'visa_sim.yml'
        assert component._instrument.encoding == 'ascii'
        assert component._instrument.terminator_write == '\n'
        assert component._instrument.terminator_read == '\n'

    def test_w_default_context_component_initialization(self):
        """ Test component initialization behaviour with default context """
        component = PowerSupplyKsN5700(self.context)
        component.initialize()

        # Test default configuration load
        assert component._configuration == self.default_component_config

        # Test custom variables default values
        assert component._shared_memory == {
            'connected': False,
            'raw_query': ''
        }
        assert component._shared_memory_getter == {
            'connected': 'connected',
            'raw_query': 'raw_query'
        }
        assert component._shared_memory_setter == {
            'connect': 'connected',
            'raw_query': 'raw_query'
        }
        assert component._parameter_info == self.default_service_info
        assert component._inst is None
        assert 'visa_sim.yml' in component._simulation_file

        assert component._instrument.address == 'TCPIP0::1.2.3.4::INSTR'
        assert component._instrument.visa_sim == 'visa_sim.yml'
        assert component._instrument.encoding == 'ascii'
        assert component._instrument.terminator_write == '\n'
        assert component._instrument.terminator_read == '\n'

    def test_visa_sim_local_from_project_folder(self):
        """ Test component creation behaviour with default context """
        temp_file = NamedTemporaryFile(delete=False)

        temp_file_folder = temp_file.name.rsplit('/', 1)[0]
        temp_file_name = temp_file.name.rsplit('/', 1)[1]

        os.chdir(temp_file_folder)

        component = PowerSupplyKsN5700(
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

        component = PowerSupplyKsN5700(self.context)
        component.initialize()

        assert 'visa_sim.yml' in component._simulation_file

    def test_w_custom_context(self):
        """ Test component creation behaviour with default context """
        component = PowerSupplyKsN5700(self.context,
                                       local_config={
                                           'name': 'custom_name',
                                           'instrument': {
                                               'visa_sim': None
                                           },
                                           'parameters': {
                                               'new_param': {
                                                   'description':
                                                   'New parameter description',
                                                   'set': {
                                                       'signature': [{
                                                           'param_1': {
                                                               type: str
                                                           }
                                                       }],
                                                       'instrument_command': [{
                                                           'write':
                                                           '{:}'
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
            'raw_query': ''
        }
        assert component._shared_memory_getter == {
            'connected': 'connected',
            'raw_query': 'raw_query'
        }
        assert component._shared_memory_setter == {
            'connect': 'connected',
            'raw_query': 'raw_query'
        }

        custom_service_info = compose_service_info(custom_component_config)
        assert component._parameter_info == custom_service_info
        assert component._inst is None
        assert component._simulation_file is None

    def test_w_wrong_custom_context(self):
        """ Test component creation behaviour with default context """

        # Test with wrong topics dictionary
        with pytest.raises(ComponentConfigException) as excinfo:
            PowerSupplyKsN5700(self.context,
                               local_config={
                                   'parameters': 'wrong'
                               }).initialize()
        assert 'Parameters configuration: wrong format' in str(excinfo.value)

        # In case no new parameters are given, use the default ones
        component = PowerSupplyKsN5700(self.context,
                                       local_config={'parameters': {}})
        component.initialize()

        assert component._configuration == self.default_component_config

        # Test with missing simulation file
        with pytest.raises(ComponentConfigException) as excinfo:
            PowerSupplyKsN5700(self.context,
                               local_config={
                                   'instrument': {
                                       'visa_sim': 'non-existing'
                                   }
                               }).initialize()
        assert "Visa-sim file has not been found" in str(excinfo.value)

        # Test case properties do not have a getter, setter or default
        component = PowerSupplyKsN5700(
            self.context, local_config={'parameters': {
                'new_param': {}
            }})
        component.initialize()

        assert component._shared_memory == {'connected': 0, 'raw_query': ''}

    def test_io_signature_publication(self):
        """ Test component io_signature observable """
        dummy_test_class = CallbackTestClass()

        # Subscribe to the topic that shall be published
        self.context.rx['io_service_signature'].subscribe(
            dummy_test_class.test_func_1)

        component = PowerSupplyKsN5700(self.context)
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

        component = PowerSupplyKsN5700(self.context,
                                       local_config={
                                           'name': 'custom_name',
                                           'instrument': {
                                               'visa_sim': None
                                           },
                                           'parameters': {
                                               'new_param': {
                                                   'description':
                                                   'New parameter description',
                                                   'set': {
                                                       'signature': [{
                                                           'param_1': {
                                                               type: str
                                                           }
                                                       }],
                                                       'instrument_command': [{
                                                           'write':
                                                           '{:}'
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
        component = PowerSupplyKsN5700(self.context)
        component.initialize()
        dummy_test_class = CallbackTestClass()

        # Subscribe to the topic that shall be published
        self.context.rx['io_result'].pipe(
            op.filter(
                lambda value: isinstance(value, ServiceResponse))).subscribe(
                    dummy_test_class.test_func_1)

        # 1 - Test that component only gets activated for implemented services
        self.context.rx['io_service_request'].on_next(
            ServiceRequest(
                provider='keysight_series_n5700_dc_power_supply_controller',
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
            ServiceRequest(
                provider='keysight_series_n5700_dc_power_supply_controller',
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
            ServiceRequest(
                provider='keysight_series_n5700_dc_power_supply_controller',
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
            ServiceRequest(
                provider='keysight_series_n5700_dc_power_supply_controller',
                id='sys_err',
                type=ParameterType.get))

        time.sleep(.1)

        assert dummy_test_class.func_1_times_called == 3
        assert dummy_test_class.func_1_last_value.id == 'sys_err'
        assert dummy_test_class.func_1_last_value.type == ParameterType.get
        assert dummy_test_class.func_1_last_value.value == '0,_No_Error'

        # 5 - Test generic command
        self.context.rx['io_service_request'].on_next(
            ServiceRequest(
                provider='keysight_series_n5700_dc_power_supply_controller',
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
            ServiceRequest(
                provider='keysight_series_n5700_dc_power_supply_controller',
                id='idn',
                type=ParameterType.get,
                args=[]))

        time.sleep(.1)

        assert dummy_test_class.func_1_times_called == 5
        assert dummy_test_class.func_1_last_value.id == 'idn'
        assert dummy_test_class.func_1_last_value.type == ParameterType.get
        assert dummy_test_class.func_1_last_value.value == 'Keysight_Technologies,5700A,12345,A.11.22,A.33.44'

        # 7 - Test shared memory set
        assert component._shared_memory == {'connected': 1, 'raw_query': ''}

        self.context.rx['io_service_request'].on_next(
            ServiceRequest(
                provider='keysight_series_n5700_dc_power_supply_controller',
                id='raw_query',
                type=ParameterType.set,
                args=['*IDN?']))

        time.sleep(.1)

        assert component._shared_memory == {
            'connected': 1,
            'raw_query': 'Keysight_Technologies,5700A,12345,A.11.22,A.33.44'
        }

        assert dummy_test_class.func_1_times_called == 6
        assert dummy_test_class.func_1_last_value.id == 'raw_query'
        assert dummy_test_class.func_1_last_value.type == ParameterType.set
        assert dummy_test_class.func_1_last_value.value is None

        # 8 - Test shared memory get
        self.context.rx['io_service_request'].on_next(
            ServiceRequest(
                provider='keysight_series_n5700_dc_power_supply_controller',
                id='raw_query',
                type=ParameterType.get,
                args=[]))

        time.sleep(.1)

        assert dummy_test_class.func_1_times_called == 7
        assert dummy_test_class.func_1_last_value.id == 'raw_query'
        assert dummy_test_class.func_1_last_value.type == ParameterType.get
        assert dummy_test_class.func_1_last_value.value == 'Keysight_Technologies,5700A,12345,A.11.22,A.33.44'

        # 9 - Test special case of msg command with multiple args
        self.context.rx['io_service_request'].on_next(
            ServiceRequest(
                provider='keysight_series_n5700_dc_power_supply_controller',
                id='raw_write',
                type=ParameterType.set,
                args=['CURR', '2']))

        time.sleep(.1)

        assert dummy_test_class.func_1_times_called == 8
        assert dummy_test_class.func_1_last_value.id == 'raw_write'
        assert dummy_test_class.func_1_last_value.type == ParameterType.set
        assert dummy_test_class.func_1_last_value.value is None

        self.context.rx['io_service_request'].on_next(
            ServiceRequest(
                provider='keysight_series_n5700_dc_power_supply_controller',
                id='raw_query',
                type=ParameterType.set,
                args=['CURR?']))

        time.sleep(.1)

        assert component._shared_memory == {'connected': 1, 'raw_query': '2'}

        self.context.rx['io_service_request'].on_next(
            ServiceRequest(
                provider='keysight_series_n5700_dc_power_supply_controller',
                id='raw_query',
                type=ParameterType.get,
                args=[]))

        time.sleep(.1)

        assert dummy_test_class.func_1_times_called == 10
        assert dummy_test_class.func_1_last_value.id == 'raw_query'
        assert dummy_test_class.func_1_last_value.type == ParameterType.get
        assert dummy_test_class.func_1_last_value.value == '2'

        # 10 - Specific parameters
        self.context.rx['io_service_request'].on_next(
            ServiceRequest(
                provider='keysight_series_n5700_dc_power_supply_controller',
                id='output_voltage_setting',
                type=ParameterType.get,
                args=[]))

        time.sleep(.1)

        assert dummy_test_class.func_1_times_called == 11
        assert dummy_test_class.func_1_last_value.id == 'output_voltage_setting'
        assert dummy_test_class.func_1_last_value.type == ParameterType.get
        assert dummy_test_class.func_1_last_value.value == '0'

        self.context.rx['io_service_request'].on_next(
            ServiceRequest(
                provider='keysight_series_n5700_dc_power_supply_controller',
                id='output_voltage_setting',
                type=ParameterType.set,
                args=[5.2]))

        time.sleep(.1)

        assert dummy_test_class.func_1_times_called == 12
        assert dummy_test_class.func_1_last_value.id == 'output_voltage_setting'
        assert dummy_test_class.func_1_last_value.type == ParameterType.set
        assert dummy_test_class.func_1_last_value.value is None

        self.context.rx['io_service_request'].on_next(
            ServiceRequest(
                provider='keysight_series_n5700_dc_power_supply_controller',
                id='output_voltage_setting',
                type=ParameterType.get,
                args=[]))

        time.sleep(.1)

        assert dummy_test_class.func_1_times_called == 13
        assert dummy_test_class.func_1_last_value.id == 'output_voltage_setting'
        assert dummy_test_class.func_1_last_value.type == ParameterType.get
        assert dummy_test_class.func_1_last_value.value == '5.2'

        # 11 - Test no system errors
        self.context.rx['io_service_request'].on_next(
            ServiceRequest(
                provider='keysight_series_n5700_dc_power_supply_controller',
                id='sys_err',
                type=ParameterType.get))

        time.sleep(.1)

        assert dummy_test_class.func_1_times_called == 14
        assert dummy_test_class.func_1_last_value.id == 'sys_err'
        assert dummy_test_class.func_1_last_value.type == ParameterType.get
        assert dummy_test_class.func_1_last_value.value == '0,_No_Error'

        # 12 - Test disconnection to the instrument
        self.context.rx['io_service_request'].on_next(
            ServiceRequest(
                provider='keysight_series_n5700_dc_power_supply_controller',
                id='connect',
                type=ParameterType.set,
                args=['0']))

        time.sleep(.1)

        assert component._inst is None
        assert dummy_test_class.func_1_times_called == 15
        assert dummy_test_class.func_1_last_value.id == 'connect'
        assert dummy_test_class.func_1_last_value.type == ParameterType.set
        assert dummy_test_class.func_1_last_value.value is None

        self.context.rx['io_service_request'].on_next(
            ServiceRequest(
                provider='keysight_series_n5700_dc_power_supply_controller',
                id='connected',
                type=ParameterType.get,
                args=[]))

        time.sleep(.1)

        assert component._inst is None
        assert dummy_test_class.func_1_times_called == 16
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
        component = PowerSupplyKsN5700(
            self.context,
            local_config={'instrument': {
                'address': 'TCPIP0::4.3.2.1::INSTR'
            }})
        component.initialize()

        assert component._inst is None

        self.context.rx['io_service_request'].on_next(
            ServiceRequest(
                provider='keysight_series_n5700_dc_power_supply_controller',
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
        component = PowerSupplyKsN5700(self.context)
        component.initialize()

        assert component._inst is None

        self.context.rx['io_service_request'].on_next(
            ServiceRequest(
                provider='keysight_series_n5700_dc_power_supply_controller',
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
            PowerSupplyKsN5700(self.context,
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
            PowerSupplyKsN5700(self.context,
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
            PowerSupplyKsN5700(self.context,
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

    def test_connection_cases_normal_fail(self):
        dummy_test_class = CallbackTestClass()

        # Subscribe to the topic that shall be published
        self.context.rx['io_result'].pipe(
            op.filter(
                lambda value: isinstance(value, ServiceResponse))).subscribe(
                    dummy_test_class.test_func_1)

        # Test real connection to missing instrument
        component = PowerSupplyKsN5700(
            self.context, local_config={'instrument': {
                'visa_sim': None
            }})
        component.initialize()

        assert component._inst is None

        self.context.rx['io_service_request'].on_next(
            ServiceRequest(
                provider='keysight_series_n5700_dc_power_supply_controller',
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

        component = PowerSupplyKsN5700(self.context)
        component.initialize()

        # Test quit while on load window
        component._inst = Test()

        assert not component._inst.called

        self.context.rx['quit'].on_next(Empty())

        # Test connection to the instrument has been closed
        assert component._inst is None
