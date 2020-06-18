import os
import pytest
import copy
import time

from rx import operators as op

from mamba.core.testing.utils import compose_service_info, get_config_dict, CallbackTestClass, get_provider_params_info
from mamba.core.context import Context
from mamba.mock.tcp.cyclic_tm_tcp_mock import CyclicTmTcpMock
from mamba.component.instrument_driver.tcp.cyclic_telemetry_tcp import CyclicTmTcpController
from mamba.core.exceptions import ComponentConfigException
from mamba.core.msg import Empty, ServiceRequest, ServiceResponse, ParameterType

component_path = os.path.join('component', 'instrument_driver', 'tcp',
                              'cyclic_telemetry_tcp')


class TestClass:
    def setup_class(self):
        """ setup_class called once for the class """
        self.mamba_path = os.path.join(os.path.dirname(__file__), '..', '..',
                                       '..', '..', 'mamba')

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
                         'mamba'))

    def teardown_method(self):
        """ teardown_method called for every method """
        del self.context

    def test_wo_context(self):
        """ Test component behaviour without required context """
        with pytest.raises(TypeError) as excinfo:
            CyclicTmTcpController()

        assert "missing 1 required positional argument" in str(excinfo.value)

    def test_w_default_context_component_creation(self):
        """ Test component creation behaviour with default context """
        component = CyclicTmTcpController(self.context)

        # Test default configuration load
        assert component._configuration == self.default_component_config

        # Test custom variables default values
        assert component._shared_memory == {}
        assert component._shared_memory_getter == {}
        assert component._shared_memory_setter == {}
        assert component._parameter_info == {}
        assert component._inst is None
        assert component._inst_cyclic_tm is None
        assert component._inst_cyclic_tm_thread is None
        assert component._cyclic_tm_mapping == {}

        assert component._instrument.address == '0.0.0.0'
        assert component._instrument.port is None
        assert component._instrument.tc_port == 8091
        assert component._instrument.tm_port == 8092
        assert component._instrument.encoding == 'utf-8'
        assert component._instrument.terminator_write == '\r\n'
        assert component._instrument.terminator_read == '\n'

    def test_w_default_context_component_initialization(self):
        """ Test component initialization behaviour with default context """
        component = CyclicTmTcpController(self.context)
        component.initialize()

        # Test default configuration load
        assert component._configuration == self.default_component_config

        # Test custom variables default values
        assert component._shared_memory == {
            'connected': 0,
            'parameter_1': 0,
            'parameter_2': 0,
            'parameter_3': 0,
            'raw_query': ''
        }
        assert component._shared_memory_getter == {
            'connected': 'connected',
            'parameter_1': 'parameter_1',
            'parameter_2': 'parameter_2',
            'parameter_3': 'parameter_3',
            'raw_query': 'raw_query'
        }
        assert component._shared_memory_setter == {
            'connect': 'connected',
            'parameter_1': 'parameter_1',
            'parameter_2': 'parameter_2',
            'parameter_3': 'parameter_3',
            'raw_query': 'raw_query'
        }
        assert component._parameter_info == self.default_service_info
        assert component._inst is None
        assert component._inst_cyclic_tm is None
        assert component._inst_cyclic_tm_thread is None
        assert component._cyclic_tm_mapping == {
            'parameter_1': 'PARAMETER_1 {:}',
            'parameter_2': 'PARAMETER_2 {:}',
            'parameter_3': 'PARAMETER_3 {:}'
        }

        assert component._instrument.address == '0.0.0.0'
        assert component._instrument.port is None
        assert component._instrument.tc_port == 8091
        assert component._instrument.tm_port == 8092
        assert component._instrument.encoding == 'utf-8'
        assert component._instrument.terminator_write == '\r\n'
        assert component._instrument.terminator_read == '\n'

    def test_w_custom_context(self):
        """ Test component creation behaviour with default context """
        component = CyclicTmTcpController(
            self.context,
            local_config={
                'name': 'custom_name',
                'instrument': {
                    'port': 9000
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
        custom_component_config['instrument']['port'] = 9000
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
            'connected': 0,
            'parameter_1': 0,
            'parameter_2': 0,
            'parameter_3': 0,
            'raw_query': ''
        }
        assert component._shared_memory_getter == {
            'connected': 'connected',
            'parameter_1': 'parameter_1',
            'parameter_2': 'parameter_2',
            'parameter_3': 'parameter_3',
            'raw_query': 'raw_query'
        }
        assert component._shared_memory_setter == {
            'connect': 'connected',
            'parameter_1': 'parameter_1',
            'parameter_2': 'parameter_2',
            'parameter_3': 'parameter_3',
            'raw_query': 'raw_query'
        }

        custom_service_info = compose_service_info(custom_component_config)
        assert component._parameter_info == custom_service_info
        assert component._inst is None
        assert component._inst_cyclic_tm is None
        assert component._inst_cyclic_tm_thread is None
        assert component._cyclic_tm_mapping == {
            'parameter_1': 'PARAMETER_1 {:}',
            'parameter_2': 'PARAMETER_2 {:}',
            'parameter_3': 'PARAMETER_3 {:}'
        }

    def test_w_wrong_custom_context(self):
        """ Test component creation behaviour with default context """

        # Test with wrong topics dictionary
        with pytest.raises(ComponentConfigException) as excinfo:
            CyclicTmTcpController(self.context,
                                  local_config={
                                      'parameters': 'wrong'
                                  }).initialize()
        assert 'Parameters configuration: wrong format' in str(excinfo.value)

        # In case no new parameters are given, use the default ones
        component = CyclicTmTcpController(self.context,
                                          local_config={'parameters': {}})
        component.initialize()

        assert component._configuration == self.default_component_config

        # Test with missing address
        with pytest.raises(ComponentConfigException) as excinfo:
            CyclicTmTcpController(self.context,
                                  local_config={
                                      'instrument': {
                                          'address': None
                                      }
                                  }).initialize()
        assert "Missing address in Instrument Configuration" in str(
            excinfo.value)

        # Test with missing port
        with pytest.raises(ComponentConfigException) as excinfo:
            CyclicTmTcpController(self.context,
                                  local_config={
                                      'instrument': {
                                          'port': None
                                      }
                                  }).initialize()
        assert "Missing port in Instrument Configuration" in str(excinfo.value)

        # Test case properties do not have a getter, setter or default
        component = CyclicTmTcpController(
            self.context, local_config={'parameters': {
                'new_param': {}
            }})
        component.initialize()

        assert component._shared_memory == {
            'connected': 0,
            'parameter_1': 0,
            'parameter_2': 0,
            'parameter_3': 0,
            'raw_query': ''
        }

    def test_io_signature_publication(self):
        """ Test component io_signature observable """
        dummy_test_class = CallbackTestClass()

        # Subscribe to the topic that shall be published
        self.context.rx['io_service_signature'].subscribe(
            dummy_test_class.test_func_1)

        component = CyclicTmTcpController(self.context)
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

        component = CyclicTmTcpController(
            self.context,
            local_config={
                'name': 'custom_name',
                'instrument': {
                    'address': '1.2.3.4'
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
        custom_component_config['instrument']['address'] = 8071
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
        # Start Mock
        mock = CyclicTmTcpMock(self.context)
        mock.initialize()

        # Start Test
        component = CyclicTmTcpController(self.context)
        component.initialize()
        dummy_test_class = CallbackTestClass()

        # Subscribe to the topic that shall be published
        self.context.rx['io_result'].pipe(
            op.filter(lambda value: isinstance(value, ServiceResponse) and
                      value.id != 'parameter_1' and value.id != 'parameter_2'
                      and value.id != 'parameter_3')).subscribe(
                          dummy_test_class.test_func_1)

        self.context.rx['io_result'].pipe(
            op.filter(lambda value: value.id == 'parameter_1' or value.id ==
                      'parameter_2' or value.id == 'parameter_3')).subscribe(
                          dummy_test_class.test_func_2)

        # 1 - Test that component only gets activated for implemented services
        self.context.rx['io_service_request'].on_next(
            ServiceRequest(provider='cyclic_telemetry_tcp_controller',
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
            ServiceRequest(provider='cyclic_telemetry_tcp_controller',
                           id='idn',
                           type=ParameterType.get,
                           args=[]))

        time.sleep(.1)

        assert dummy_test_class.func_1_times_called == 1
        assert dummy_test_class.func_2_times_called == 0
        assert dummy_test_class.func_1_last_value.id == 'idn'
        assert dummy_test_class.func_1_last_value.type == ParameterType.error
        assert dummy_test_class.func_1_last_value.value == 'Not possible to perform command before connection is established'

        # 3 - Test connection to the instrument
        assert component._inst is None

        self.context.rx['io_service_request'].on_next(
            ServiceRequest(provider='cyclic_telemetry_tcp_controller',
                           id='connect',
                           type=ParameterType.set,
                           args=['1']))

        time.sleep(.1)

        assert component._inst is not None
        assert dummy_test_class.func_1_times_called == 2
        assert dummy_test_class.func_1_last_value.id == 'connect'
        assert dummy_test_class.func_1_last_value.type == ParameterType.set
        assert dummy_test_class.func_1_last_value.value is None

        assert component._inst_cyclic_tm is not None
        assert component._inst_cyclic_tm_thread is not None
        assert dummy_test_class.func_2_times_called == 3
        assert dummy_test_class.func_2_last_value.id == 'parameter_3'
        assert dummy_test_class.func_2_last_value.type == ParameterType.get
        assert dummy_test_class.func_2_last_value.value == '3'

        # 4 - Test no system errors
        self.context.rx['io_service_request'].on_next(
            ServiceRequest(provider='cyclic_telemetry_tcp_controller',
                           id='sys_err',
                           type=ParameterType.get))

        time.sleep(.1)

        assert dummy_test_class.func_1_times_called == 3
        assert dummy_test_class.func_1_last_value.id == 'sys_err'
        assert dummy_test_class.func_1_last_value.type == ParameterType.get
        assert dummy_test_class.func_1_last_value.value == '0,_No_Error'

        # 5 - Test generic command
        self.context.rx['io_service_request'].on_next(
            ServiceRequest(provider='cyclic_telemetry_tcp_controller',
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
            ServiceRequest(provider='cyclic_telemetry_tcp_controller',
                           id='idn',
                           type=ParameterType.get,
                           args=[]))

        time.sleep(.1)

        assert dummy_test_class.func_1_times_called == 5
        assert dummy_test_class.func_1_last_value.id == 'idn'
        assert dummy_test_class.func_1_last_value.type == ParameterType.get
        assert dummy_test_class.func_1_last_value.value == 'Mamba Framework,Cyclic Telemetry TCP Mock,1.0'

        # 7 - Test shared memory set
        assert component._shared_memory == {
            'connected': 1,
            'raw_query': '',
            'parameter_1': '1',
            'parameter_2': '2',
            'parameter_3': '3'
        }

        self.context.rx['io_service_request'].on_next(
            ServiceRequest(provider='cyclic_telemetry_tcp_controller',
                           id='raw_query',
                           type=ParameterType.set,
                           args=['*IDN?']))

        time.sleep(.1)

        assert component._shared_memory == {
            'connected': 1,
            'raw_query': 'Mamba Framework,Cyclic Telemetry TCP Mock,1.0',
            'parameter_1': '1',
            'parameter_2': '2',
            'parameter_3': '3'
        }

        assert dummy_test_class.func_1_times_called == 6
        assert dummy_test_class.func_1_last_value.id == 'raw_query'
        assert dummy_test_class.func_1_last_value.type == ParameterType.set
        assert dummy_test_class.func_1_last_value.value is None

        # 8 - Test shared memory get
        self.context.rx['io_service_request'].on_next(
            ServiceRequest(provider='cyclic_telemetry_tcp_controller',
                           id='raw_query',
                           type=ParameterType.get,
                           args=[]))

        time.sleep(.1)

        assert dummy_test_class.func_1_times_called == 7
        assert dummy_test_class.func_1_last_value.id == 'raw_query'
        assert dummy_test_class.func_1_last_value.type == ParameterType.get
        assert dummy_test_class.func_1_last_value.value == 'Mamba Framework,Cyclic Telemetry TCP Mock,1.0'

        # 9 - Test special case of msg command with multiple args
        self.context.rx['io_service_request'].on_next(
            ServiceRequest(provider='cyclic_telemetry_tcp_controller',
                           id='parameter_3',
                           type=ParameterType.set,
                           args=['30']))

        time.sleep(5.1)

        assert dummy_test_class.func_2_times_called == 7
        assert dummy_test_class.func_2_last_value.id == 'parameter_3'
        assert dummy_test_class.func_2_last_value.type == ParameterType.get
        assert dummy_test_class.func_2_last_value.value == '30'

        self.context.rx['io_service_request'].on_next(
            ServiceRequest(provider='cyclic_telemetry_tcp_controller',
                           id='raw_write',
                           type=ParameterType.set,
                           args=['PARAMETER_3', '40']))

        time.sleep(5.1)

        assert dummy_test_class.func_2_times_called == 10
        assert dummy_test_class.func_2_last_value.id == 'parameter_3'
        assert dummy_test_class.func_2_last_value.type == ParameterType.get
        assert dummy_test_class.func_2_last_value.value == '40'

        # 10 - Test no system errors
        self.context.rx['io_service_request'].on_next(
            ServiceRequest(provider='cyclic_telemetry_tcp_controller',
                           id='sys_err',
                           type=ParameterType.get))

        time.sleep(.1)

        assert dummy_test_class.func_1_times_called == 9
        assert dummy_test_class.func_1_last_value.id == 'sys_err'
        assert dummy_test_class.func_1_last_value.type == ParameterType.get
        assert dummy_test_class.func_1_last_value.value == '0,_No_Error'

        # 11 - Test disconnection to the instrument
        self.context.rx['io_service_request'].on_next(
            ServiceRequest(provider='cyclic_telemetry_tcp_controller',
                           id='connect',
                           type=ParameterType.set,
                           args=['0']))

        time.sleep(.1)

        assert component._inst is None
        assert dummy_test_class.func_1_times_called == 10
        assert dummy_test_class.func_1_last_value.id == 'connect'
        assert dummy_test_class.func_1_last_value.type == ParameterType.set
        assert dummy_test_class.func_1_last_value.value is None

        self.context.rx['io_service_request'].on_next(
            ServiceRequest(provider='cyclic_telemetry_tcp_controller',
                           id='connected',
                           type=ParameterType.get,
                           args=[]))

        time.sleep(.1)

        assert component._inst is None
        assert dummy_test_class.func_1_times_called == 11
        assert dummy_test_class.func_1_last_value.id == 'connected'
        assert dummy_test_class.func_1_last_value.type == ParameterType.get
        assert dummy_test_class.func_1_last_value.value == 0

        self.context.rx['quit'].on_next(Empty())

        time.sleep(1)

    def test_connection_wrong_instrument_address(self):
        dummy_test_class = CallbackTestClass()

        # Subscribe to the topic that shall be published
        self.context.rx['io_result'].pipe(
            op.filter(
                lambda value: isinstance(value, ServiceResponse))).subscribe(
                    dummy_test_class.test_func_1)

        # Test simulated normal connection to the instrument
        component = CyclicTmTcpController(
            self.context,
            local_config={'instrument': {
                'port': {
                    'tc': 1000,
                    'tm': 1001
                }
            }})
        component.initialize()

        assert component._inst is None

        self.context.rx['io_service_request'].on_next(
            ServiceRequest(provider='cyclic_telemetry_tcp_controller',
                           id='connect',
                           type=ParameterType.set,
                           args=['1']))

        time.sleep(1)

        assert dummy_test_class.func_1_times_called == 1
        assert dummy_test_class.func_1_last_value.id == 'connect'
        assert dummy_test_class.func_1_last_value.type == ParameterType.error
        assert dummy_test_class.func_1_last_value.value == 'Instrument is unreachable'

    def test_disconnection_w_no_connection(self):
        dummy_test_class = CallbackTestClass()

        # Subscribe to the topic that shall be published
        self.context.rx['io_result'].pipe(
            op.filter(
                lambda value: isinstance(value, ServiceResponse))).subscribe(
                    dummy_test_class.test_func_1)

        # Test real connection to missing instrument
        component = CyclicTmTcpController(self.context)
        component.initialize()

        assert component._inst is None

        self.context.rx['io_service_request'].on_next(
            ServiceRequest(provider='cyclic_telemetry_tcp_controller',
                           id='connect',
                           type=ParameterType.set,
                           args=['0']))

        time.sleep(.1)

        assert component._inst is None
        assert dummy_test_class.func_1_times_called == 1
        assert dummy_test_class.func_1_last_value.id == 'connect'
        assert dummy_test_class.func_1_last_value.type == ParameterType.set
        assert dummy_test_class.func_1_last_value.value is None

    def test_multi_command_multi_input_parameter(self):
        # Start Mock
        mock = CyclicTmTcpMock(
            self.context,
            local_config={'instrument': {
                'port': {
                    'tc': 6000,
                    'tm': 6001
                }
            }})
        mock.initialize()

        dummy_test_class = CallbackTestClass()

        # Subscribe to the topic that shall be published
        self.context.rx['io_result'].pipe(
            op.filter(lambda value: isinstance(value, ServiceResponse) and
                      value.id != 'parameter_1' and value.id != 'parameter_2'
                      and value.id != 'parameter_3')).subscribe(
                          dummy_test_class.test_func_1)

        self.context.rx['io_result'].pipe(
            op.filter(lambda value: value.id == 'parameter_1' or value.id ==
                      'parameter_2' or value.id == 'parameter_3')).subscribe(
                          dummy_test_class.test_func_2)

        component = CyclicTmTcpController(
            self.context,
            local_config={
                'instrument': {
                    'port': {
                        'tc': 6000,
                        'tm': 6001
                    }
                },
                'parameters': {
                    'new_param': {
                        'type': 'int',
                        'description': 'New parameter description',
                        'set': {
                            'signature': [{
                                'arg_1': {
                                    'type': 'int'
                                }
                            }, {
                                'arg_2': {
                                    'type': 'int'
                                }
                            }],
                            'instrument_command': [{
                                'write': 'PARAMETER_1 {0}'
                            }, {
                                'write': 'PARAMETER_3 {1}'
                            }, {
                                'query': '*IDN?'
                            }]
                        },
                        'get': None,
                    }
                }
            })

        component.initialize()

        # Connect to instrument and check initial status
        self.context.rx['io_service_request'].on_next(
            ServiceRequest(provider='cyclic_telemetry_tcp_controller',
                           id='connect',
                           type=ParameterType.set,
                           args=['1']))

        time.sleep(.1)

        assert component._shared_memory == {
            'connected': 1,
            'new_param': None,
            'raw_query': '',
            'parameter_1': '1',
            'parameter_2': '2',
            'parameter_3': '3',
        }

        assert component._inst_cyclic_tm is not None
        assert component._inst_cyclic_tm_thread is not None
        assert dummy_test_class.func_2_times_called == 3
        assert dummy_test_class.func_2_last_value.id == 'parameter_3'
        assert dummy_test_class.func_2_last_value.type == ParameterType.get
        assert dummy_test_class.func_2_last_value.value == '3'

        # Call new parameter
        self.context.rx['io_service_request'].on_next(
            ServiceRequest(provider='cyclic_telemetry_tcp_controller',
                           id='new_param',
                           type=ParameterType.set,
                           args=['11', '33']))

        time.sleep(.1)

        assert component._shared_memory == {
            'connected': 1,
            'new_param': 'Mamba Framework,Cyclic Telemetry TCP Mock,1.0',
            'raw_query': '',
            'parameter_1': '1',
            'parameter_2': '2',
            'parameter_3': '3',
        }

        time.sleep(5)

        assert component._shared_memory == {
            'connected': 1,
            'new_param': 'Mamba Framework,Cyclic Telemetry TCP Mock,1.0',
            'raw_query': '',
            'parameter_1': '11',
            'parameter_2': '2',
            'parameter_3': '33',
        }

        assert dummy_test_class.func_2_times_called == 6
        assert dummy_test_class.func_2_last_value.id == 'parameter_3'
        assert dummy_test_class.func_2_last_value.type == ParameterType.get
        assert dummy_test_class.func_2_last_value.value == '33'

        self.context.rx['quit'].on_next(Empty())

        time.sleep(1)

    def test_service_invalid_info(self):
        with pytest.raises(ComponentConfigException) as excinfo:
            CyclicTmTcpController(self.context,
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
            CyclicTmTcpController(self.context,
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
            CyclicTmTcpController(self.context,
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

    def test_tcp_broken_and_reconnection(self):
        # Start Mock
        mock = CyclicTmTcpMock(
            self.context,
            local_config={'instrument': {
                'port': {
                    'tc': 32458,
                    'tm': 32459
                }
            }})
        mock.initialize()

        # Start Test
        component = CyclicTmTcpController(
            self.context,
            local_config={'instrument': {
                'port': {
                    'tc': 32458,
                    'tm': 32459
                }
            }})
        component.initialize()
        dummy_test_class = CallbackTestClass()

        # Subscribe to the topic that shall be published
        # Subscribe to the topic that shall be published
        self.context.rx['io_result'].pipe(
            op.filter(lambda value: isinstance(value, ServiceResponse) and
                      value.id != 'parameter_1' and value.id != 'parameter_2'
                      and value.id != 'parameter_3')).subscribe(
                          dummy_test_class.test_func_1)

        self.context.rx['io_result'].pipe(
            op.filter(lambda value: value.id == 'parameter_1' or value.id ==
                      'parameter_2' or value.id == 'parameter_3')).subscribe(
                          dummy_test_class.test_func_2)

        # 1 - Test connection to the instrument
        assert component._inst is None

        self.context.rx['io_service_request'].on_next(
            ServiceRequest(provider='cyclic_telemetry_tcp_controller',
                           id='connect',
                           type=ParameterType.set,
                           args=['1']))

        time.sleep(.1)

        assert component._inst is not None
        assert dummy_test_class.func_1_times_called == 1
        assert dummy_test_class.func_1_last_value.id == 'connect'
        assert dummy_test_class.func_1_last_value.type == ParameterType.set
        assert dummy_test_class.func_1_last_value.value is None

        # 2 - Test generic query
        self.context.rx['io_service_request'].on_next(
            ServiceRequest(provider='cyclic_telemetry_tcp_controller',
                           id='idn',
                           type=ParameterType.get,
                           args=[]))

        time.sleep(.1)

        assert dummy_test_class.func_1_times_called == 2
        assert dummy_test_class.func_1_last_value.id == 'idn'
        assert dummy_test_class.func_1_last_value.type == ParameterType.get
        assert dummy_test_class.func_1_last_value.value == 'Mamba Framework,Cyclic Telemetry TCP Mock,1.0'

        # Force connection close
        component._inst.close()

        self.context.rx['io_service_request'].on_next(
            ServiceRequest(provider='cyclic_telemetry_tcp_controller',
                           id='idn',
                           type=ParameterType.get,
                           args=[]))

        time.sleep(.1)

        assert dummy_test_class.func_1_times_called == 3
        assert dummy_test_class.func_1_last_value.id == 'idn'
        assert dummy_test_class.func_1_last_value.type == ParameterType.get
        assert dummy_test_class.func_1_last_value.value == 'Mamba Framework,Cyclic Telemetry TCP Mock,1.0'

        self.context.rx['quit'].on_next(Empty())

        time.sleep(1)

    def test_quit_observer(self):
        """ Test component quit observer """
        class Test:
            called = False

            def close(self):
                self.called = True

        component = CyclicTmTcpController(self.context)
        component.initialize()

        # Test quit while on load window
        component._inst = Test()

        assert not component._inst.called

        self.context.rx['quit'].on_next(Empty())

        # Test connection to the instrument has been closed
        assert component._inst is None
