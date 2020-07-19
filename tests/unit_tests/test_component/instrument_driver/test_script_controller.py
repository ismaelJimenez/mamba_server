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

        assert 'mamba-server/mamba/marketplace/components/script/script_controller/scripts' in component._scripts_folder

    def test_w_default_context_component_initialization(self):
        """ Test component initialization behaviour with default context """
        component = ScriptInstrumentDriver(self.context)
        component.initialize()

        # Test default configuration load
        assert component._configuration == self.default_component_config

        # Test custom variables default values
        assert component._shared_memory == {}
        assert component._shared_memory_getter == {}
        assert component._shared_memory_setter == {}
        assert component._parameter_info == self.default_service_info
        assert component._inst == 0

        assert component._instrument.address == 'None'
        assert component._instrument.port == 0
        assert component._instrument.encoding == 'ascii'
        assert component._instrument.terminator_write == '\r\n'
        assert component._instrument.terminator_read == '\n'

        assert 'mamba-server/mamba/marketplace/components/script/script_controller/scripts' in component._scripts_folder

    def test_w_global_source_folder(self):
        """ Test component creation behaviour with default context """
        component = ScriptInstrumentDriver(self.context,
                                           local_config={
                                               'name': 'custom_name',
                                               'source_folder': {
                                                   'global': '/usr/test'
                                               }
                                           })
        component.initialize()

        custom_component_config = copy.deepcopy(self.default_component_config)
        custom_component_config['name'] = 'custom_name'
        custom_component_config['source_folder']['global'] = '/usr/test'

        # Test default configuration load
        assert component._configuration == custom_component_config

        # Test custom variables default values
        assert component._shared_memory == {}
        assert component._shared_memory_getter == {}
        assert component._shared_memory_setter == {}

        custom_service_info = compose_service_info(custom_component_config)
        assert component._parameter_info == custom_service_info
        assert component._inst == 0

        assert component._scripts_folder == '/usr/test'

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

        assert component._shared_memory == {}

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

        # 2 - Test generic python command execution
        self.context.rx['io_service_request'].on_next(
            ServiceRequest(provider='script_controller',
                           id='python_cmd_exec',
                           type=ParameterType.set,
                           args=['dump_to_file.py test_file.txt 1 2 3 4']))

        time.sleep(.1)

        assert exists('test_file.txt')
        f = open('test_file.txt', 'r')
        assert f.read() == '1 2 3 4'
        f.close()

        assert dummy_test_class.func_1_times_called == 1
        assert dummy_test_class.func_1_last_value.id == 'python_cmd_exec'
        assert dummy_test_class.func_1_last_value.type == ParameterType.set
        assert dummy_test_class.func_1_last_value.value is None

        # 3 - Test generic bash command execution
        self.context.rx['io_service_request'].on_next(
            ServiceRequest(provider='script_controller',
                           id='bash_cmd_exec',
                           type=ParameterType.set,
                           args=['clean_dump.sh test_file.txt']))

        time.sleep(.1)

        assert not exists('test_file.txt')

        assert dummy_test_class.func_1_times_called == 2
        assert dummy_test_class.func_1_last_value.id == 'bash_cmd_exec'
        assert dummy_test_class.func_1_last_value.type == ParameterType.set
        assert dummy_test_class.func_1_last_value.value is None

        # 4 - Test specific python command execution
        self.context.rx['io_service_request'].on_next(
            ServiceRequest(provider='script_controller',
                           id='dump_to_file',
                           type=ParameterType.set,
                           args=['test_file.txt 1 2 3 4']))

        time.sleep(.1)

        assert exists('test_file.txt')
        f = open('test_file.txt', 'r')
        assert f.read() == '1 2 3 4'
        f.close()

        assert dummy_test_class.func_1_times_called == 3
        assert dummy_test_class.func_1_last_value.id == 'dump_to_file'
        assert dummy_test_class.func_1_last_value.type == ParameterType.set
        assert dummy_test_class.func_1_last_value.value is None

        # 5 - Test specific bash command execution
        self.context.rx['io_service_request'].on_next(
            ServiceRequest(provider='script_controller',
                           id='clean_dump',
                           type=ParameterType.set,
                           args=['test_file.txt']))

        time.sleep(.1)

        assert not exists('test_file.txt')

        assert dummy_test_class.func_1_times_called == 4
        assert dummy_test_class.func_1_last_value.id == 'clean_dump'
        assert dummy_test_class.func_1_last_value.type == ParameterType.set
        assert dummy_test_class.func_1_last_value.value is None

        # 6 - Test generic bash command execution - Unexisting script
        self.context.rx['io_service_request'].on_next(
            ServiceRequest(provider='script_controller',
                           id='python_cmd_exec',
                           type=ParameterType.set,
                           args=['non_existing.px test_file.txt 1 2 3 4']))

        time.sleep(.1)

        assert not exists('test_file.txt')

        assert dummy_test_class.func_1_times_called == 5
        assert dummy_test_class.func_1_last_value.id == 'python_cmd_exec'
        assert dummy_test_class.func_1_last_value.type == ParameterType.error
        assert dummy_test_class.func_1_last_value.value == 'Script execution error.'

        self.context.rx['quit'].on_next(Empty())

        # 7 - Test generic python command execution - Missing parameters
        self.context.rx['io_service_request'].on_next(
            ServiceRequest(provider='script_controller',
                           id='python_cmd_exec',
                           type=ParameterType.set,
                           args=['dump_to_file.py']))

        time.sleep(.1)

        assert not exists('test_file.txt')

        assert dummy_test_class.func_1_times_called == 6
        assert dummy_test_class.func_1_last_value.id == 'python_cmd_exec'
        assert dummy_test_class.func_1_last_value.type == ParameterType.error
        assert dummy_test_class.func_1_last_value.value == 'Script execution error.'

        # 8 - Test valid generic python command execution
        self.context.rx['io_service_request'].on_next(
            ServiceRequest(provider='script_controller',
                           id='python_cmd_exec',
                           type=ParameterType.set,
                           args=['dump_to_file.py test_file.txt 1 2 3 4']))

        time.sleep(.1)

        assert exists('test_file.txt')
        f = open('test_file.txt', 'r')
        assert f.read() == '1 2 3 4'
        f.close()

        assert dummy_test_class.func_1_times_called == 7
        assert dummy_test_class.func_1_last_value.id == 'python_cmd_exec'
        assert dummy_test_class.func_1_last_value.type == ParameterType.set
        assert dummy_test_class.func_1_last_value.value is None

        # 9 - Test generic bash command execution - Unexisting script
        self.context.rx['io_service_request'].on_next(
            ServiceRequest(provider='script_controller',
                           id='bash_cmd_exec',
                           type=ParameterType.set,
                           args=['non_existing.sh test_file.txt']))

        time.sleep(.1)

        assert exists('test_file.txt')

        # 10 - Test generic bash command execution - Unexisting dump file
        self.context.rx['io_service_request'].on_next(
            ServiceRequest(provider='script_controller',
                           id='bash_cmd_exec',
                           type=ParameterType.set,
                           args=['clean_dump.sh non_existing.txt']))

        time.sleep(.1)

        assert exists('test_file.txt')

        assert dummy_test_class.func_1_times_called == 9
        assert dummy_test_class.func_1_last_value.id == 'bash_cmd_exec'
        assert dummy_test_class.func_1_last_value.type == ParameterType.error
        assert dummy_test_class.func_1_last_value.value == 'Script execution error.'

        # 11 - Test valid generic bash command execution
        self.context.rx['io_service_request'].on_next(
            ServiceRequest(provider='script_controller',
                           id='bash_cmd_exec',
                           type=ParameterType.set,
                           args=['clean_dump.sh test_file.txt']))

        time.sleep(.1)

        assert not exists('test_file.txt')

        assert dummy_test_class.func_1_times_called == 10
        assert dummy_test_class.func_1_last_value.id == 'bash_cmd_exec'
        assert dummy_test_class.func_1_last_value.type == ParameterType.set
        assert dummy_test_class.func_1_last_value.value is None

        self.context.rx['quit'].on_next(Empty())

        time.sleep(1)
