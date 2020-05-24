import pytest
import os

from mamba_server.context import Context
from mamba_server.components.protocol_controller.hvs_protocol_controller import Driver
from mamba_server.components.observable_types import Telemetry, Telecommand, \
    IoServiceRequest
from mamba_server.exceptions import ComponentConfigException


class DummyTestClass:
    def __init__(self):
        super(DummyTestClass, self).__init__()
        self.times_called_io = 0
        self.last_value_io = None
        self.times_called_tm = 0
        self.last_value_tm = None

    def test_function_io(self, rx_on_set=None):
        self.times_called_io += 1
        self.last_value_io = rx_on_set

    def test_function_tm(self, rx_on_set=None):
        self.times_called_tm += 1
        self.last_value_tm = rx_on_set


class TestClass:
    def setup_class(self):
        """ setup_class called once for the class """
        pass

    def teardown_class(self):
        """ teardown_class called once for the class """
        pass

    def setup_method(self):
        """ setup_method called for every method """
        self.context = Context()
        self.context.set(
            'mamba_dir',
            os.path.join(os.path.dirname(__file__), '..', '..', '..', '..',
                         'mamba_server'))

    def teardown_method(self):
        """ teardown_method called for every method """
        del self.context

    def test_component_wo_context(self):
        with pytest.raises(TypeError) as excinfo:
            Driver()

        assert "missing 1 required positional argument" in str(excinfo.value)

    def test_component_w_empty_context(self):
        component = Driver(Context())
        component.initialize()

        # Test default configuration
        assert component._configuration == {'name': 'hvs_protocol_controller'}
        assert component._io_services == {}

    def test_component_observer_io_service_signature(self):
        """ Test component external interface """
        component = Driver(self.context)
        component.initialize()

        # 1 - Test 1 signature message
        self.context.rx['io_service_signature'].on_next({
            'provider': 'test_provider',
            'services': {
                'TEST_TC_1': {
                    'description': "custom command 1",
                    'signature': [['str'], 'None']
                },
                'TEST_TC_2': {
                    'description': "custom command 2",
                    'signature': [[], 'str']
                }
            }
        })

        assert component._io_services == {
            'TEST_TC_1': {
                'description': 'custom command 1',
                'signature': [['str'], 'None']
            },
            'TEST_TC_2': {
                'description': 'custom command 2',
                'signature': [[], 'str']
            }
        }

        # 2 - Test with second signature message
        self.context.rx['io_service_signature'].on_next({
            'provider': 'test_provider_2',
            'services': {
                'TEST_TC_3': {
                    'description': "custom command 3",
                    'signature': [['str'], 'str']
                }
            }
        })

        assert component._io_services == {
            'TEST_TC_1': {
                'description': 'custom command 1',
                'signature': [['str'], 'None']
            },
            'TEST_TC_2': {
                'description': 'custom command 2',
                'signature': [[], 'str']
            },
            'TEST_TC_3': {
                'description': 'custom command 3',
                'signature': [['str'], 'str']
            }
        }

        # 3 - Test with repeated service key
        with pytest.raises(ComponentConfigException) as excinfo:
            self.context.rx['io_service_signature'].on_next({
                'provider': 'test_provider_3',
                'services': {
                    'TEST_TC_3': {
                        'description': "custom command 3-a",
                        'signature': [['str'], 'str']
                    }
                }
            })

        assert "Received conflicting service key: TEST_TC_3" in str(
            excinfo.value)

        # 4 - Test with wrong signature
        with pytest.raises(ComponentConfigException) as excinfo:
            self.context.rx['io_service_signature'].on_next({
                'provider': 'test_provider_2',
                'services': {
                    'TEST_TC_4': {
                        'description': "custom command 4",
                        'signature': 'wrong'
                    }
                }
            })

        assert 'Signature of service "TEST_TC_4" is invalid. Format shall be' \
               ' [[arg_1, arg_2, ...], return_type]' in str(excinfo.value)

    def test_component_observer_tc(self):
        """ Test component external interface """
        dummy_test_class = DummyTestClass()
        component = Driver(self.context)
        component.initialize()

        # Initialize service signatures
        self.context.rx['io_service_signature'].on_next({
            'provider': 'test_provider',
            'services': {
                'TEST_TC_1': {
                    'description': "custom command 1",
                    'signature': [['str', 'int'], 'None']
                },
                'TEST_TC_2': {
                    'description': "custom command 2",
                    'signature': [[], 'str']
                },
                'TEST_TC_3': {
                    'description': "custom command 3",
                    'signature': [['int'], 'str']
                }
            }
        })

        # Subscribe to the 'tc' that shall be published
        self.context.rx['io_service_request'].subscribe(
            dummy_test_class.test_function_io)
        self.context.rx['tm'].subscribe(dummy_test_class.test_function_tm)

        # Send single TC - 1. Helo
        self.context.rx['tc'].on_next(
            Telecommand(tc_id='test', tc_type='helo', args=[]))

        assert dummy_test_class.times_called_tm == 1
        assert isinstance(dummy_test_class.last_value_tm, Telemetry)
        assert dummy_test_class.last_value_tm.id == 'test'
        assert dummy_test_class.last_value_tm.type == 'helo'
        assert dummy_test_class.last_value_tm.value is None

        # Send single raw TC - 2. Tc_Meta
        self.context.rx['tc'].on_next(
            Telecommand(tc_id='TEST_TC_3', tc_type='tc_meta', args=[]))

        assert dummy_test_class.times_called_tm == 2
        assert isinstance(dummy_test_class.last_value_tm, Telemetry)
        assert dummy_test_class.last_value_tm.id == 'TEST_TC_3'
        assert dummy_test_class.last_value_tm.type == 'tc_meta'
        assert dummy_test_class.last_value_tm.value == {
            'description': 'custom command 3',
            'signature': [['int'], 'str']
        }

        # Send single raw TC - 3. Tm_Meta
        self.context.rx['tc'].on_next(
            Telecommand(tc_id='TEST_TC_3', tc_type='tm_meta', args=[]))

        assert dummy_test_class.times_called_tm == 3
        assert isinstance(dummy_test_class.last_value_tm, Telemetry)
        assert dummy_test_class.last_value_tm.id == 'TEST_TC_3'
        assert dummy_test_class.last_value_tm.type == 'tm_meta'
        assert dummy_test_class.last_value_tm.value == {
            'description': 'custom command 3',
            'signature': [['int'], 'str']
        }

        # Send single raw TC - 4. Tc
        self.context.rx['tc'].on_next(
            Telecommand(tc_id='TEST_TC_3', tc_type='tc', args=[3]))

        assert dummy_test_class.times_called_io == 1
        assert isinstance(dummy_test_class.last_value_io, IoServiceRequest)
        assert dummy_test_class.last_value_io.id == 'TEST_TC_3'
        assert dummy_test_class.last_value_io.type == 'tc'
        assert dummy_test_class.last_value_io.args == [3]

        self.context.rx['tc'].on_next(
            Telecommand(tc_id='TEST_TC_3', tc_type='tc', args=[3, 'test_arg']))

        assert dummy_test_class.times_called_io == 2
        assert isinstance(dummy_test_class.last_value_io, IoServiceRequest)
        assert dummy_test_class.last_value_io.id == 'TEST_TC_3'
        assert dummy_test_class.last_value_io.type == 'tc'
        assert dummy_test_class.last_value_io.args == [3, 'test_arg']

        # Send single raw TC - 5. Tm
        self.context.rx['tc'].on_next(
            Telecommand(tc_id='TEST_TC_3', tc_type='tm', args=[]))

        assert dummy_test_class.times_called_io == 3
        assert isinstance(dummy_test_class.last_value_io, IoServiceRequest)
        assert dummy_test_class.last_value_io.id == 'TEST_TC_3'
        assert dummy_test_class.last_value_io.type == 'tm'
        assert dummy_test_class.last_value_io.args == []

        self.context.rx['tc'].on_next(
            Telecommand(tc_id='TEST_TC_3', tc_type='tm', args=[1]))

        assert dummy_test_class.times_called_io == 4
        assert isinstance(dummy_test_class.last_value_io, IoServiceRequest)
        assert dummy_test_class.last_value_io.id == 'TEST_TC_3'
        assert dummy_test_class.last_value_io.type == 'tm'
        assert dummy_test_class.last_value_io.args == [1]

        # Send unexisting TC type
        self.context.rx['tc'].on_next(
            Telecommand(tc_id='TEST_TC_3', tc_type='wrong', args=[1]))

        assert dummy_test_class.times_called_tm == 4
        assert isinstance(dummy_test_class.last_value_tm, Telemetry)
        assert dummy_test_class.last_value_tm.id == 'TEST_TC_3'
        assert dummy_test_class.last_value_tm.type == 'error'
        assert dummy_test_class.last_value_tm.value == 'Not recognized command type'

        # Send unexisting TC id
        self.context.rx['tc'].on_next(
            Telecommand(tc_id='TEST_TC_WRONG', tc_type='tc', args=[1]))

        assert dummy_test_class.times_called_tm == 5
        assert isinstance(dummy_test_class.last_value_tm, Telemetry)
        assert dummy_test_class.last_value_tm.id == 'TEST_TC_WRONG'
        assert dummy_test_class.last_value_tm.type == 'error'
        assert dummy_test_class.last_value_tm.value == 'Not recognized command'
