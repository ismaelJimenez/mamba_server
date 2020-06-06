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
from mamba.core.msg import Empty, ServiceRequest, ServiceResponse

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
        assert component._service_info == {}
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
            'query_raw_result': ''
        }
        assert component._shared_memory_getter == {
            'query_connected': 'connected',
            'tm_query_raw': 'query_raw_result'
        }
        assert component._shared_memory_setter == {
            'connect': 'connected',
            'disconnect': 'connected',
            'tc_query_raw': 'query_raw_result'
        }
        assert component._service_info == self.default_service_info
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
                'topics': {
                    'CUSTOM_TOPIC': {
                        'command': 'CUSTOM_SCPI {:}',
                        'description': 'Custom command description',
                        'signature': [['str'], None]
                    }
                }
            })
        component.initialize()

        custom_component_config = copy.deepcopy(self.default_component_config)
        custom_component_config['name'] = 'custom_name'
        custom_component_config['instrument']['visa_sim'] = None
        custom_component_config['topics'].update({
            'CUSTOM_TOPIC': {
                'command': 'CUSTOM_SCPI {:}',
                'description': 'Custom command description',
                'signature': [['str'], None]
            }
        })

        # Test default configuration load
        assert component._configuration == custom_component_config

        # Test custom variables default values
        assert component._shared_memory == {
            'connected': False,
            'query_raw_result': ''
        }
        assert component._shared_memory_getter == {
            'query_connected': 'connected',
            'tm_query_raw': 'query_raw_result'
        }
        assert component._shared_memory_setter == {
            'connect': 'connected',
            'disconnect': 'connected',
            'tc_query_raw': 'query_raw_result'
        }

        custom_service_info = compose_service_info(custom_component_config)
        assert component._service_info == custom_service_info
        assert component._inst is None
        assert component._simulation_file is None

    def test_w_wrong_custom_context(self):
        """ Test component creation behaviour with default context """

        # Test with wrong topics dictionary
        with pytest.raises(ComponentConfigException) as excinfo:
            SwitchMatrixKsZ2091c(self.context,
                                 local_config={
                                     'topics': 'wrong'
                                 }).initialize()
        assert "Topics configuration: wrong format" in str(excinfo.value)

        # In case no new topics are given, use the default ones
        component = SwitchMatrixKsZ2091c(self.context,
                                         local_config={'topics': {}})
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
            'query_raw_result': '',
            'new_param': None,
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
                'topics': {
                    'CUSTOM_TOPIC': {
                        'command': 'CUSTOM_SCPI {:}',
                        'description': 'Custom command description',
                        'signature': [['str'], None]
                    }
                }
            })
        component.initialize()

        time.sleep(.1)

        assert dummy_test_class.func_1_times_called == 2

        custom_component_config = copy.deepcopy(self.default_component_config)
        custom_component_config['name'] = 'custom_name'
        custom_component_config['instrument']['visa_sim'] = None
        topics = {
            'CUSTOM_TOPIC': {
                'command': 'CUSTOM_SCPI {:}',
                'description': 'Custom command description',
                'signature': [['str'], None]
            }
        }
        topics.update(custom_component_config['topics'])
        custom_component_config['topics'] = topics

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
            ServiceRequest(provider='keysight_z2091c_switch',
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
            ServiceRequest(provider='keysight_z2091c_switch',
                           id='query_idn',
                           type='set',
                           args=[]))

        time.sleep(.1)

        assert dummy_test_class.func_1_times_called == 1
        assert dummy_test_class.func_1_last_value.id == 'query_idn'
        assert dummy_test_class.func_1_last_value.type == 'error'
        assert dummy_test_class.func_1_last_value.value == 'Not possible to perform command before connection is established'

        # 3 - Test connection to the instrument
        assert component._inst is None

        self.context.rx['io_service_request'].on_next(
            ServiceRequest(provider='keysight_z2091c_switch',
                           id='connect',
                           type='set',
                           args=[]))

        time.sleep(.1)

        assert component._inst is not None
        assert dummy_test_class.func_1_times_called == 2
        assert dummy_test_class.func_1_last_value.id == 'connect'
        assert dummy_test_class.func_1_last_value.type == 'set'
        assert dummy_test_class.func_1_last_value.value is None

        # 4 - Test no system errors
        self.context.rx['io_service_request'].on_next(
            ServiceRequest(provider='keysight_z2091c_switch',
                           id='query_sys_err',
                           type='get'))

        time.sleep(.1)

        assert dummy_test_class.func_1_times_called == 3
        assert dummy_test_class.func_1_last_value.id == 'query_sys_err'
        assert dummy_test_class.func_1_last_value.type == 'get'
        assert dummy_test_class.func_1_last_value.value == '0,_No_Error'

        # 5 - Test generic command
        self.context.rx['io_service_request'].on_next(
            ServiceRequest(provider='keysight_z2091c_switch',
                           id='rst',
                           type='set',
                           args=[1]))

        time.sleep(.1)

        assert dummy_test_class.func_1_times_called == 4
        assert dummy_test_class.func_1_last_value.id == 'rst'
        assert dummy_test_class.func_1_last_value.type == 'set'
        assert dummy_test_class.func_1_last_value.value is None

        # 6 - Test generic query
        self.context.rx['io_service_request'].on_next(
            ServiceRequest(provider='keysight_z2091c_switch',
                           id='query_idn',
                           type='get',
                           args=[]))

        time.sleep(.1)

        assert dummy_test_class.func_1_times_called == 5
        assert dummy_test_class.func_1_last_value.id == 'query_idn'
        assert dummy_test_class.func_1_last_value.type == 'get'
        assert dummy_test_class.func_1_last_value.value == 'Keysight_Technologies,Z2091C-001,US56400131,1.1.6450.15113'

        # 7 - Test shared memory set
        assert component._shared_memory == {
            'connected': 1,
            'query_raw_result': ''
        }

        self.context.rx['io_service_request'].on_next(
            ServiceRequest(provider='keysight_z2091c_switch',
                           id='tc_query_raw',
                           type='set',
                           args=['*IDN?']))

        time.sleep(.1)

        assert component._shared_memory == {
            'connected':
            1,
            'query_raw_result':
            'Keysight_Technologies,Z2091C-001,US56400131,1.1.6450.15113'
        }

        assert dummy_test_class.func_1_times_called == 6
        assert dummy_test_class.func_1_last_value.id == 'tc_query_raw'
        assert dummy_test_class.func_1_last_value.type == 'set'
        assert dummy_test_class.func_1_last_value.value is None

        # 8 - Test shared memory get
        self.context.rx['io_service_request'].on_next(
            ServiceRequest(provider='keysight_z2091c_switch',
                           id='tm_query_raw',
                           type='get',
                           args=[]))

        time.sleep(.1)

        assert dummy_test_class.func_1_times_called == 7
        assert dummy_test_class.func_1_last_value.id == 'tm_query_raw'
        assert dummy_test_class.func_1_last_value.type == 'get'
        assert dummy_test_class.func_1_last_value.value == 'Keysight_Technologies,Z2091C-001,US56400131,1.1.6450.15113'

        # 9 - Test special case of msg command with multiple args
        self.context.rx['io_service_request'].on_next(
            ServiceRequest(provider='keysight_z2091c_switch',
                           id='raw',
                           type='set',
                           args=['CONF:DIG:WIDTH', 'WORD,', '(@2001)']))

        time.sleep(.1)

        assert dummy_test_class.func_1_times_called == 8
        assert dummy_test_class.func_1_last_value.id == 'raw'
        assert dummy_test_class.func_1_last_value.type == 'set'
        assert dummy_test_class.func_1_last_value.value is None

        self.context.rx['io_service_request'].on_next(
            ServiceRequest(provider='keysight_z2091c_switch',
                           id='tc_query_raw',
                           type='set',
                           args=['CONF:DIG:WIDTH?', '(@2001)']))

        time.sleep(.1)

        assert component._shared_memory == {
            'connected': 1,
            'query_raw_result': 'WORD'
        }

        self.context.rx['io_service_request'].on_next(
            ServiceRequest(provider='keysight_z2091c_switch',
                           id='tm_query_raw',
                           type='get',
                           args=[]))

        time.sleep(.1)

        assert dummy_test_class.func_1_times_called == 10
        assert dummy_test_class.func_1_last_value.id == 'tm_query_raw'
        assert dummy_test_class.func_1_last_value.type == 'get'
        assert dummy_test_class.func_1_last_value.value == 'WORD'

        # 10 - Test no system errors
        self.context.rx['io_service_request'].on_next(
            ServiceRequest(provider='keysight_z2091c_switch',
                           id='query_sys_err',
                           type='get'))

        time.sleep(.1)

        assert dummy_test_class.func_1_times_called == 11
        assert dummy_test_class.func_1_last_value.id == 'query_sys_err'
        assert dummy_test_class.func_1_last_value.type == 'get'
        assert dummy_test_class.func_1_last_value.value == '0,_No_Error'

        # 11 - Test disconnection to the instrument
        self.context.rx['io_service_request'].on_next(
            ServiceRequest(provider='keysight_z2091c_switch',
                           id='disconnect',
                           type='set',
                           args=[]))

        time.sleep(.1)

        assert component._inst is None
        assert dummy_test_class.func_1_times_called == 12
        assert dummy_test_class.func_1_last_value.id == 'disconnect'
        assert dummy_test_class.func_1_last_value.type == 'set'
        assert dummy_test_class.func_1_last_value.value is None

        self.context.rx['io_service_request'].on_next(
            ServiceRequest(provider='keysight_z2091c_switch',
                           id='query_connected',
                           type='get',
                           args=[]))

        time.sleep(.1)

        assert component._inst is None
        assert dummy_test_class.func_1_times_called == 13
        assert dummy_test_class.func_1_last_value.id == 'query_connected'
        assert dummy_test_class.func_1_last_value.type == 'get'
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
            local_config={'resource-name': 'TCPIP0::4.3.2.1::INSTR'})
        component.initialize()

        assert component._inst is None

        self.context.rx['io_service_request'].on_next(
            ServiceRequest(provider='keysight_z2091c_switch',
                           id='connect',
                           type='set',
                           args=[]))

        time.sleep(.1)

        assert dummy_test_class.func_1_times_called == 1
        assert dummy_test_class.func_1_last_value.id == 'connect'
        assert dummy_test_class.func_1_last_value.type == 'set'
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
            ServiceRequest(provider='keysight_z2091c_switch',
                           id='disconnect',
                           type='set',
                           args=[]))

        time.sleep(.1)

        assert component._inst is None
        assert dummy_test_class.func_1_times_called == 1
        assert dummy_test_class.func_1_last_value.id == 'disconnect'
        assert dummy_test_class.func_1_last_value.type == 'set'
        assert dummy_test_class.func_1_last_value.value is None

    def test_service_invalid_signature(self):
        with pytest.raises(ComponentConfigException) as excinfo:
            SwitchMatrixKsZ2091c(self.context,
                                 local_config={
                                     'topics': {
                                         'CUSTOM_TOPIC': {
                                             'command':
                                             'SOURce:CUSTOM_SCPI {:}',
                                             'description':
                                             'Custom command description'
                                             'frequency',
                                             'signature': ['String']
                                         }
                                     }
                                 }).initialize()

        assert 'Signature of service "CUSTOM_TOPIC" is invalid. Format shall' \
               ' be [[arg_1, arg_2, ...], return_type]' in str(excinfo.value)

        with pytest.raises(ComponentConfigException) as excinfo:
            SwitchMatrixKsZ2091c(self.context,
                                 local_config={
                                     'topics': {
                                         'CUSTOM_TOPIC': {
                                             'command':
                                             'SOURce:CUSTOM_SCPI {:}',
                                             'description':
                                             'Custom command description'
                                             'frequency',
                                             'signature': ['String', str]
                                         }
                                     }
                                 }).initialize()

        assert 'Signature of service "CUSTOM_TOPIC" is invalid. Format shall' \
               ' be [[arg_1, arg_2, ...], return_type]' in str(excinfo.value)

        with pytest.raises(ComponentConfigException) as excinfo:
            SwitchMatrixKsZ2091c(self.context,
                                 local_config={
                                     'topics': {
                                         'CUSTOM_TOPIC': {
                                             'command':
                                             'SOURce:CUSTOM_SCPI {:}',
                                             'description':
                                             'Custom command description'
                                             'frequency',
                                             'signature':
                                             'String'
                                         }
                                     }
                                 }).initialize()

        assert 'Signature of service "CUSTOM_TOPIC" is invalid. Format shall' \
               ' be [[arg_1, arg_2, ...], return_type]' in str(excinfo.value)

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
            ServiceRequest(provider='keysight_z2091c_switch',
                           id='connect',
                           type='set',
                           args=[]))

        time.sleep(.1)

        assert component._inst is None
        assert dummy_test_class.func_1_times_called == 1
        assert dummy_test_class.func_1_last_value.id == 'connect'
        assert dummy_test_class.func_1_last_value.type == 'error'
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
