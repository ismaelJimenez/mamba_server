import pytest
import os

from mamba.core.context import Context
from mamba.component.drivers.socket_tmtc.hvs_socket_tmtc import Driver
from mamba.core.msg import Raw, ServiceResponse, ServiceRequest, ParameterType


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
                         'mamba'))

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
        assert component._configuration == {'name': 'hvs_socket_tmtc'}

    def test_component_observer_raw_tc_helo(self):
        """ Test component external interface """
        dummy_test_class = DummyTestClass()
        component = Driver(self.context)
        component.initialize()

        # Subscribe to the 'tc' that shall be published
        self.context.rx['tc'].subscribe(dummy_test_class.test_function)

        # Send single msg TC - 1. Helo
        self.context.rx['raw_tc'].on_next(Raw("helo test\r\n"))

        assert dummy_test_class.times_called == 1
        assert isinstance(dummy_test_class.last_value, ServiceRequest)
        assert dummy_test_class.last_value.id == 'test'
        assert dummy_test_class.last_value.type == 'helo'
        assert dummy_test_class.last_value.args == []

        # Send single msg TC - 2. Tc_Meta
        self.context.rx['raw_tc'].on_next(Raw("tc_meta test\r\n"))

        assert dummy_test_class.times_called == 2
        assert isinstance(dummy_test_class.last_value, ServiceRequest)
        assert dummy_test_class.last_value.id == 'test'
        assert dummy_test_class.last_value.type == 'tc_meta'
        assert dummy_test_class.last_value.args == []

        # Send single msg TC - 3. Tm_Meta
        self.context.rx['raw_tc'].on_next(Raw("tm_meta test\r\n"))

        assert dummy_test_class.times_called == 3
        assert isinstance(dummy_test_class.last_value, ServiceRequest)
        assert dummy_test_class.last_value.id == 'test'
        assert dummy_test_class.last_value.type == 'tm_meta'
        assert dummy_test_class.last_value.args == []

        # Send single msg TC - 4. Tc
        self.context.rx['raw_tc'].on_next(
            Raw('tc test "arg_1"\r\n'))

        assert dummy_test_class.times_called == 4
        assert isinstance(dummy_test_class.last_value, ServiceRequest)
        assert dummy_test_class.last_value.id == 'test'
        assert dummy_test_class.last_value.type == 'tc'
        assert dummy_test_class.last_value.args == ['arg_1']

        self.context.rx['raw_tc'].on_next(
            Raw('tc test "arg_1" "arg_2"\r\n'))

        assert dummy_test_class.times_called == 5
        assert isinstance(dummy_test_class.last_value, ServiceRequest)
        assert dummy_test_class.last_value.id == 'test'
        assert dummy_test_class.last_value.type == 'tc'
        assert dummy_test_class.last_value.args == ['arg_1', 'arg_2']

        self.context.rx['raw_tc'].on_next(
            Raw('tc test 2.3 arg_2\r\n'))

        assert dummy_test_class.times_called == 6
        assert isinstance(dummy_test_class.last_value, ServiceRequest)
        assert dummy_test_class.last_value.id == 'test'
        assert dummy_test_class.last_value.type == 'tc'
        assert dummy_test_class.last_value.args == ['2.3', 'arg_2']

        # Send single msg TC - 5. Tm
        self.context.rx['raw_tc'].on_next(Raw('tm test \r\n'))

        assert dummy_test_class.times_called == 7
        assert isinstance(dummy_test_class.last_value, ServiceRequest)
        assert dummy_test_class.last_value.id == 'test'
        assert dummy_test_class.last_value.type == 'tm'
        assert dummy_test_class.last_value.args == []

        self.context.rx['raw_tc'].on_next(Raw('tm test_2\r\n'))

        assert dummy_test_class.times_called == 8
        assert isinstance(dummy_test_class.last_value, ServiceRequest)
        assert dummy_test_class.last_value.id == 'test_2'
        assert dummy_test_class.last_value.type == 'tm'
        assert dummy_test_class.last_value.args == []

        # Send multiple msg TC
        self.context.rx['raw_tc'].on_next(
            Raw("helo test_2\r\nhelo test_3\r\n"))

        assert dummy_test_class.times_called == 10
        assert isinstance(dummy_test_class.last_value, ServiceRequest)
        assert dummy_test_class.last_value.id == 'test_3'
        assert dummy_test_class.last_value.type == 'helo'
        assert dummy_test_class.last_value.args == []

        # Send unexisting TC type
        self.context.rx['raw_tc'].on_next(Raw("wrong test\r\n"))

        assert dummy_test_class.times_called == 11
        assert isinstance(dummy_test_class.last_value, ServiceRequest)
        assert dummy_test_class.last_value.id == 'test'
        assert dummy_test_class.last_value.type == 'wrong'
        assert dummy_test_class.last_value.args == []

    def test_component_observer_tm(self):
        """ Test component external interface """
        dummy_test_class = DummyTestClass()
        component = Driver(self.context)
        component.initialize()

        # Subscribe to the 'tc' that shall be published
        self.context.rx['raw_tm'].subscribe(dummy_test_class.test_function)

        # Send single TM - 1. Helo
        self.context.rx['tm'].on_next(ServiceResponse(id='test', type='helo'))

        assert dummy_test_class.times_called == 1
        assert isinstance(dummy_test_class.last_value, Raw)
        assert dummy_test_class.last_value.raw == '> OK helo test\r\n'

        # Send single TM - 2. Tc_Meta
        self.context.rx['tm'].on_next(
            ServiceResponse(id='test',
                      type='tc_meta',
                      value={
                          'signature': [['str', 'int'], 'str'],
                          'description': 'description test 1'
                      }))

        assert dummy_test_class.times_called == 2
        assert isinstance(dummy_test_class.last_value, Raw)
        assert dummy_test_class.last_value.raw == '> OK test;2;description test 1\r\n'

        # Send single TM - 3. Tm_Meta
        self.context.rx['tm'].on_next(
            ServiceResponse(id='test',
                      type='tm_meta',
                      value={
                          'signature': [['str', 'int'], 'str'],
                          'description': 'description test 1'
                      }))

        assert dummy_test_class.times_called == 3
        assert isinstance(dummy_test_class.last_value, Raw)
        assert dummy_test_class.last_value.raw == '> OK test;str;str;description test 1;7;4\r\n'

        # Send single TM - 4. Tc
        self.context.rx['tm'].on_next(ServiceResponse(id='test', type='tc'))

        assert dummy_test_class.times_called == 4
        assert isinstance(dummy_test_class.last_value, Raw)
        assert dummy_test_class.last_value.raw == '> OK test\r\n'

        # Send single TM - 5. Tm
        self.context.rx['tm'].on_next(
            ServiceResponse(id='test', type='tm', value=1))

        assert dummy_test_class.times_called == 5
        assert isinstance(dummy_test_class.last_value, Raw)
        assert '> OK test;' in dummy_test_class.last_value.raw
        assert ';1;1;0;1\r\n' in dummy_test_class.last_value.raw

        # Send single TM - 6. Error
        self.context.rx['tm'].on_next(
            ServiceResponse(id='test', type=ParameterType.error, value='error msg'))

        assert dummy_test_class.times_called == 6
        assert isinstance(dummy_test_class.last_value, Raw)
        assert dummy_test_class.last_value.raw == '> ERROR test error msg\r\n'

        # Send multiple TM
        self.context.rx['tm'].on_next(ServiceResponse(id='test_3',
                                                type='helo'))
        self.context.rx['tm'].on_next(ServiceResponse(id='test_4',
                                                type='helo'))

        assert dummy_test_class.times_called == 8
        assert isinstance(dummy_test_class.last_value, Raw)
        assert dummy_test_class.last_value.raw == '> OK helo test_4\r\n'
