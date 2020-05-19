import pytest
import os

from mamba_server.context import Context
from mamba_server.components.drivers.socket_tmtc.hvs_socket_tmtc import Driver


class DummyTestClass:
    def __init__(self):
        super(DummyTestClass, self).__init__()
        self.times_called = 0
        self.last_value = None

    def test_function(self, rx_on_set=None):
        self.times_called += 1
        self.last_value = rx_on_set


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
        assert component._configuration == {}

    def test_component_observer_raw_tc_helo(self):
        """ Test component external interface """
        dummy_test_class = DummyTestClass()
        component = Driver(self.context)
        component.initialize()

        # Subscribe to the 'tc' that shall be published
        self.context.rx['tc'].subscribe(dummy_test_class.test_function)

        # Send single raw TC
        self.context.rx['raw_tc'].on_next("helo test\r\n")

        assert dummy_test_class.times_called == 1
        assert dummy_test_class.last_value == ['helo', 'test']

        # Send multiple raw TC
        self.context.rx['raw_tc'].on_next("helo test_2\r\nhelo test_3\r\n")

        assert dummy_test_class.times_called == 3
        assert dummy_test_class.last_value == ['helo', 'test_3']

    def test_component_observer_tm_ack(self):
        """ Test component external interface """
        dummy_test_class = DummyTestClass()
        component = Driver(self.context)
        component.initialize()

        # Subscribe to the 'tc' that shall be published
        self.context.rx['raw_tm'].subscribe(dummy_test_class.test_function)

        # Send single TM
        self.context.rx['tm'].on_next(['ACK', 'helo', 'test_1'])

        assert dummy_test_class.times_called == 1
        assert dummy_test_class.last_value == '> OK helo test_1\r\n'

        # Send multiple TM
        self.context.rx['tm'].on_next(['ACK', 'helo', 'test_2'])
        self.context.rx['tm'].on_next(['ACK', 'helo', 'test_3'])

        assert dummy_test_class.times_called == 3
        assert dummy_test_class.last_value == '> OK helo test_3\r\n'
