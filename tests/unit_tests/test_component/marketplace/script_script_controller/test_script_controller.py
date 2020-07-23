import os
import pytest
import copy
import time

from os.path import join, exists
from rx import operators as op

from mamba.core.testing.utils import compose_service_info, get_config_dict, CallbackTestClass, get_provider_params_info
from mamba.core.context import Context
from mamba.marketplace.components.script.script_controller import ScriptInstrumentDriver
from mamba.core.exceptions import ComponentConfigException
from mamba.core.msg import Empty, ServiceRequest, ServiceResponse, ParameterType

component_path = os.path.join('marketplace', 'components', 'script',
                              'script_controller')


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
            ScriptInstrumentDriver()

        assert "missing 1 required positional argument" in str(excinfo.value)

    def test_w_default_context_component_creation(self):
        """ Test component creation behaviour with default context """
        component = ScriptInstrumentDriver(self.context)

        # Test default configuration load
        assert component._configuration == self.default_component_config

        # Test custom variables default values
        assert component._shared_memory == {}
        assert component._shared_memory_getter == {}
        assert component._shared_memory_setter == {}
        assert component._parameter_info == {}
        assert component._inst is None

        assert component._instrument.address == 'None'
        assert component._instrument.port == 0
        assert component._instrument.encoding == 'ascii'
        assert component._instrument.terminator_write == '\r\n'
        assert component._instrument.terminator_read == '\n'

    def test_w_default_context_component_initialization(self):
        """ Test component initialization behaviour with default context """
        component = ScriptInstrumentDriver(self.context)
        component.initialize()

        # Test default configuration load
        assert component._configuration == self.default_component_config

        # Test custom variables default values
        assert component._shared_memory == {'bash_cmd': None, 'python_cmd': None}
        assert component._shared_memory_getter == {'bash_cmd': 'bash_cmd', 'python_cmd': 'python_cmd'}
        assert component._shared_memory_setter == {'bash_cmd': 'bash_cmd', 'python_cmd': 'python_cmd'}
        assert component._parameter_info == self.default_service_info
        assert component._inst == 0

        assert component._instrument.address == 'None'
        assert component._instrument.port == 0
        assert component._instrument.encoding == 'ascii'
        assert component._instrument.terminator_write == '\r\n'
        assert component._instrument.terminator_read == '\n'

    def test_w_wrong_custom_context(self):
        """ Test component creation behaviour with default context """

        # Test with wrong topics dictionary
        with pytest.raises(ComponentConfigException) as excinfo:
            ScriptInstrumentDriver(self.context,
                                   local_config={
                                       'parameters': 'wrong'
                                   }).initialize()
        assert 'Parameters configuration: wrong format' in str(excinfo.value)

        # In case no new parameters are given, use the default ones
        component = ScriptInstrumentDriver(self.context,
                                           local_config={'parameters': {}})
        component.initialize()

        assert component._configuration == self.default_component_config

        # Test with missing address
        with pytest.raises(ComponentConfigException) as excinfo:
            ScriptInstrumentDriver(self.context,
                                   local_config={
                                       'instrument': {
                                           'address': None
                                       }
                                   }).initialize()
        assert "Missing address in Instrument Configuration" in str(
            excinfo.value)

        # Test case properties do not have a getter, setter or default
        component = ScriptInstrumentDriver(
            self.context, local_config={'parameters': {
                'new_param': {}
            }})
        component.initialize()

        assert component._shared_memory == {'bash_cmd': None, 'python_cmd': None}

    def test_io_signature_publication(self):
        """ Test component io_signature observable """
        dummy_test_class = CallbackTestClass()

        # Subscribe to the topic that shall be published
        self.context.rx['io_service_signature'].subscribe(
            dummy_test_class.test_func_1)

        component = ScriptInstrumentDriver(self.context)
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

    def test_io_service_request_observer(self):
        """ Test component io_service_request observer """
        # Start Test
        component = ScriptInstrumentDriver(self.context)
        component.initialize()
        dummy_test_class = CallbackTestClass()

        # Subscribe to the topic that shall be published
        self.context.rx['io_result'].pipe(
            op.filter(
                lambda value: isinstance(value, ServiceResponse))).subscribe(
                    dummy_test_class.test_func_1)

        # 1 - Test that component only gets activated for implemented services
        self.context.rx['io_service_request'].on_next(
            ServiceRequest(provider='script_controller',
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

        # 2 - Test CWD
        self.context.rx['io_service_request'].on_next(
            ServiceRequest(provider='script_controller',
                           id='cwd',
                           type=ParameterType.get))

        assert dummy_test_class.func_1_times_called == 1
        assert dummy_test_class.func_1_last_value.id == 'cwd'
        assert dummy_test_class.func_1_last_value.type == ParameterType.get

        self.context.rx['io_service_request'].on_next(
            ServiceRequest(provider='script_controller',
                           id='cwd',
                           type=ParameterType.set,
                           args=['..']))

        assert dummy_test_class.func_1_times_called == 2
        assert dummy_test_class.func_1_last_value.id == 'cwd'
        assert dummy_test_class.func_1_last_value.type == ParameterType.set
        assert dummy_test_class.func_1_last_value.value is None

        self.context.rx['io_service_request'].on_next(
            ServiceRequest(provider='script_controller',
                           id='cwd',
                           type=ParameterType.get))

        assert dummy_test_class.func_1_times_called == 3
        assert dummy_test_class.func_1_last_value.id == 'cwd'
        assert dummy_test_class.func_1_last_value.type == ParameterType.get
        assert 'tests' not in dummy_test_class.func_1_last_value.value

        # 3 - Test bash command
        self.context.rx['io_service_request'].on_next(
            ServiceRequest(provider='script_controller',
                           id='bash_cmd',
                           type=ParameterType.set,
                           args=[os.path.join(self.mamba_path, 'marketplace', 'components', 'script',
                                'script_controller', 'scripts', 'script_1')]))

        assert dummy_test_class.func_1_times_called == 4
        assert dummy_test_class.func_1_last_value.id == 'bash_cmd'
        assert dummy_test_class.func_1_last_value.type == ParameterType.set
        assert dummy_test_class.func_1_last_value.value is None

        self.context.rx['io_service_request'].on_next(
            ServiceRequest(provider='script_controller',
                           id='bash_cmd',
                           type=ParameterType.get))

        assert dummy_test_class.func_1_times_called == 5
        assert dummy_test_class.func_1_last_value.id == 'bash_cmd'
        assert dummy_test_class.func_1_last_value.type == ParameterType.get
        assert dummy_test_class.func_1_last_value.value == 'script 1\n'

        self.context.rx['io_service_request'].on_next(
            ServiceRequest(provider='script_controller',
                           id='bash_cmd',
                           type=ParameterType.set,
                           args=[os.path.join(self.mamba_path, 'marketplace', 'components', 'script',
                                'script_controller', 'scripts', 'script_2')]))

        assert dummy_test_class.func_1_times_called == 6
        assert dummy_test_class.func_1_last_value.id == 'bash_cmd'
        assert dummy_test_class.func_1_last_value.type == ParameterType.error
        assert dummy_test_class.func_1_last_value.value == 'Return code 1'

        self.context.rx['io_service_request'].on_next(
            ServiceRequest(provider='script_controller',
                           id='bash_cmd',
                           type=ParameterType.get))

        assert dummy_test_class.func_1_times_called == 7
        assert dummy_test_class.func_1_last_value.id == 'bash_cmd'
        assert dummy_test_class.func_1_last_value.type == ParameterType.get
        assert dummy_test_class.func_1_last_value.value == ''

        # 4 - Test python command
        self.context.rx['io_service_request'].on_next(
            ServiceRequest(provider='script_controller',
                           id='python_cmd',
                           type=ParameterType.set,
                           args=[os.path.join(self.mamba_path, 'marketplace', 'components', 'script',
                                'script_controller', 'scripts', 'script_3')]))

        assert dummy_test_class.func_1_times_called == 8
        assert dummy_test_class.func_1_last_value.id == 'python_cmd'
        assert dummy_test_class.func_1_last_value.type == ParameterType.set
        assert dummy_test_class.func_1_last_value.value is None

        self.context.rx['io_service_request'].on_next(
            ServiceRequest(provider='script_controller',
                           id='python_cmd',
                           type=ParameterType.get))

        assert dummy_test_class.func_1_times_called == 9
        assert dummy_test_class.func_1_last_value.id == 'python_cmd'
        assert dummy_test_class.func_1_last_value.type == ParameterType.get
        assert dummy_test_class.func_1_last_value.value == 'script 3\n'

        self.context.rx['io_service_request'].on_next(
            ServiceRequest(provider='script_controller',
                           id='python_cmd',
                           type=ParameterType.set,
                           args=[os.path.join(self.mamba_path, 'marketplace', 'components', 'script',
                                'script_controller', 'scripts', 'script_4')]))

        assert dummy_test_class.func_1_times_called == 10
        assert dummy_test_class.func_1_last_value.id == 'python_cmd'
        assert dummy_test_class.func_1_last_value.type == ParameterType.error
        assert dummy_test_class.func_1_last_value.value == 'Return code 1'

        self.context.rx['io_service_request'].on_next(
            ServiceRequest(provider='script_controller',
                           id='python_cmd',
                           type=ParameterType.get))

        assert dummy_test_class.func_1_times_called == 11
        assert dummy_test_class.func_1_last_value.id == 'python_cmd'
        assert dummy_test_class.func_1_last_value.type == ParameterType.get
        assert dummy_test_class.func_1_last_value.value == ''

        self.context.rx['io_service_request'].on_next(
            ServiceRequest(provider='script_controller',
                           id='python_cmd',
                           type=ParameterType.set,
                           args=[os.path.join(self.mamba_path, 'marketplace', 'components', 'script',
                                'script_controller', 'scripts', 'non-existing')]))

        assert dummy_test_class.func_1_times_called == 12
        assert dummy_test_class.func_1_last_value.id == 'python_cmd'
        assert dummy_test_class.func_1_last_value.type == ParameterType.error
        assert dummy_test_class.func_1_last_value.value == 'Return code 2'

        self.context.rx['io_service_request'].on_next(
            ServiceRequest(provider='script_controller',
                           id='python_cmd',
                           type=ParameterType.get))

        assert dummy_test_class.func_1_times_called == 13
        assert dummy_test_class.func_1_last_value.id == 'python_cmd'
        assert dummy_test_class.func_1_last_value.type == ParameterType.get
        assert 'No such file or directory' in dummy_test_class.func_1_last_value.value

        # 5 - Test bash command locally
        self.context.rx['io_service_request'].on_next(
            ServiceRequest(provider='script_controller',
                           id='bash_cmd',
                           type=ParameterType.set,
                           args=[os.path.join(self.mamba_path, 'marketplace', 'components', 'script',
                                'script_controller', 'scripts', 'script_5'), '1', '2', '3']))

        assert dummy_test_class.func_1_times_called == 14
        assert dummy_test_class.func_1_last_value.id == 'bash_cmd'
        assert dummy_test_class.func_1_last_value.type == ParameterType.set
        assert dummy_test_class.func_1_last_value.value is None

        self.context.rx['io_service_request'].on_next(
            ServiceRequest(provider='script_controller',
                           id='bash_cmd',
                           type=ParameterType.get))

        assert dummy_test_class.func_1_times_called == 15
        assert dummy_test_class.func_1_last_value.id == 'bash_cmd'
        assert dummy_test_class.func_1_last_value.type == ParameterType.get
        assert dummy_test_class.func_1_last_value.value == '1 2 3\n'

        # 6 - Test bash command locally
        self.context.rx['io_service_request'].on_next(
            ServiceRequest(provider='script_controller',
                           id='bash_cmd',
                           type=ParameterType.set,
                           args=['./script_1']))

        assert dummy_test_class.func_1_times_called == 16
        assert dummy_test_class.func_1_last_value.id == 'bash_cmd'
        assert dummy_test_class.func_1_last_value.type == ParameterType.error
        assert dummy_test_class.func_1_last_value.value == 'Return code 127'

        self.context.rx['io_service_request'].on_next(
            ServiceRequest(provider='script_controller',
                           id='cwd',
                           type=ParameterType.set,
                           args=[os.path.join(self.mamba_path, 'marketplace', 'components', 'script',
                                'script_controller', 'scripts')]))

        assert dummy_test_class.func_1_times_called == 17
        assert dummy_test_class.func_1_last_value.id == 'cwd'
        assert dummy_test_class.func_1_last_value.type == ParameterType.set
        assert dummy_test_class.func_1_last_value.value is None

        self.context.rx['io_service_request'].on_next(
            ServiceRequest(provider='script_controller',
                           id='bash_cmd',
                           type=ParameterType.set,
                           args=['./script_1']))

        assert dummy_test_class.func_1_times_called == 18
        assert dummy_test_class.func_1_last_value.id == 'bash_cmd'
        assert dummy_test_class.func_1_last_value.type == ParameterType.set
        assert dummy_test_class.func_1_last_value.value is None
