import pytest
import os

from mamba.core.context import Context
from mamba.core.testing.utils import CallbackTestClass
from mamba.component.protocol_translator import HvsProtocolTranslator
from mamba.core.msg import Raw, ServiceResponse, ServiceRequest, ParameterType


class TestClass:
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
            HvsProtocolTranslator()

        assert "missing 1 required positional argument" in str(excinfo.value)

    def test_component_w_empty_context(self):
        component = HvsProtocolTranslator(Context())
        component.initialize()

        # Test default configuration
        assert component._configuration == {'name': 'hvs_protocol_translator'}

    def test_component_observer_raw_tc_helo(self):
        """ Test component external interface """
        dummy_test_class = CallbackTestClass()
        component = HvsProtocolTranslator(self.context)
        component.initialize()

        # Subscribe to the 'tc' that shall be published
        self.context.rx['tc'].subscribe(dummy_test_class.test_func_1)

        # Send single msg TC - 1. Helo
        self.context.rx['raw_tc'].on_next(Raw("helo test\r\n"))

        assert dummy_test_class.func_1_times_called == 1
        assert isinstance(dummy_test_class.func_1_last_value, ServiceRequest)
        assert dummy_test_class.func_1_last_value.id == 'test'
        assert dummy_test_class.func_1_last_value.type == ParameterType.helo
        assert dummy_test_class.func_1_last_value.args == []

        # Send single msg TC - 2. Tc_Meta
        self.context.rx['raw_tc'].on_next(Raw("tc_meta test\r\n"))

        assert dummy_test_class.func_1_times_called == 2
        assert isinstance(dummy_test_class.func_1_last_value, ServiceRequest)
        assert dummy_test_class.func_1_last_value.id == 'test'
        assert dummy_test_class.func_1_last_value.type == ParameterType.set_meta
        assert dummy_test_class.func_1_last_value.args == []

        # Send single msg TC - 3. Tm_Meta
        self.context.rx['raw_tc'].on_next(Raw("tm_meta test\r\n"))

        assert dummy_test_class.func_1_times_called == 3
        assert isinstance(dummy_test_class.func_1_last_value, ServiceRequest)
        assert dummy_test_class.func_1_last_value.id == 'test'
        assert dummy_test_class.func_1_last_value.type == ParameterType.get_meta
        assert dummy_test_class.func_1_last_value.args == []

        # Send single msg TC - 4. Tc
        self.context.rx['raw_tc'].on_next(
            Raw('tc test "arg_1"\r\n'))

        assert dummy_test_class.func_1_times_called == 4
        assert isinstance(dummy_test_class.func_1_last_value, ServiceRequest)
        assert dummy_test_class.func_1_last_value.id == 'test'
        assert dummy_test_class.func_1_last_value.type == ParameterType.set
        assert dummy_test_class.func_1_last_value.args == ['arg_1']

        self.context.rx['raw_tc'].on_next(
            Raw('tc test "arg_1" "arg_2"\r\n'))

        assert dummy_test_class.func_1_times_called == 5
        assert isinstance(dummy_test_class.func_1_last_value, ServiceRequest)
        assert dummy_test_class.func_1_last_value.id == 'test'
        assert dummy_test_class.func_1_last_value.type == ParameterType.set
        assert dummy_test_class.func_1_last_value.args == ['arg_1', 'arg_2']

        self.context.rx['raw_tc'].on_next(
            Raw('tc test 2.3 arg_2\r\n'))

        assert dummy_test_class.func_1_times_called == 6
        assert isinstance(dummy_test_class.func_1_last_value, ServiceRequest)
        assert dummy_test_class.func_1_last_value.id == 'test'
        assert dummy_test_class.func_1_last_value.type == ParameterType.set
        assert dummy_test_class.func_1_last_value.args == ['2.3', 'arg_2']

        # Send single msg TC - 5. Tm
        self.context.rx['raw_tc'].on_next(Raw('tm test \r\n'))

        assert dummy_test_class.func_1_times_called == 7
        assert isinstance(dummy_test_class.func_1_last_value, ServiceRequest)
        assert dummy_test_class.func_1_last_value.id == 'test'
        assert dummy_test_class.func_1_last_value.type == ParameterType.get
        assert dummy_test_class.func_1_last_value.args == []

        self.context.rx['raw_tc'].on_next(Raw('tm test_2\r\n'))

        assert dummy_test_class.func_1_times_called == 8
        assert isinstance(dummy_test_class.func_1_last_value, ServiceRequest)
        assert dummy_test_class.func_1_last_value.id == 'test_2'
        assert dummy_test_class.func_1_last_value.type == ParameterType.get
        assert dummy_test_class.func_1_last_value.args == []

        # Send multiple msg TC
        self.context.rx['raw_tc'].on_next(
            Raw("helo test_2\r\nhelo test_3\r\n"))

        assert dummy_test_class.func_1_times_called == 10
        assert isinstance(dummy_test_class.func_1_last_value, ServiceRequest)
        assert dummy_test_class.func_1_last_value.id == 'test_3'
        assert dummy_test_class.func_1_last_value.type == ParameterType.helo
        assert dummy_test_class.func_1_last_value.args == []

        # Send unexisting TC type
        with pytest.raises(KeyError) as excinfo:
            self.context.rx['raw_tc'].on_next(Raw("wrong test\r\n"))

        assert str(excinfo.value) == "'wrong'"

    def test_component_observer_tm(self):
        """ Test component external interface """
        dummy_test_class = CallbackTestClass()
        component = HvsProtocolTranslator(self.context)
        component.initialize()

        # Subscribe to the 'tc' that shall be published
        self.context.rx['raw_tm'].subscribe(dummy_test_class.test_func_1)

        # Send single TM - 1. Helo
        self.context.rx['tm'].on_next(ServiceResponse(id='test', type=ParameterType.helo))

        assert dummy_test_class.func_1_times_called == 1
        assert isinstance(dummy_test_class.func_1_last_value, Raw)
        assert dummy_test_class.func_1_last_value.msg == '> OK helo test\r\n'

        # Send single TM - 2. Tc_Meta
        self.context.rx['tm'].on_next(
            ServiceResponse(id='test',
                      type=ParameterType.set_meta,
                      value={
                          'signature': [['str', 'int'], 'str'],
                          'description': 'description test 1'
                      }))

        assert dummy_test_class.func_1_times_called == 2
        assert isinstance(dummy_test_class.func_1_last_value, Raw)
        assert dummy_test_class.func_1_last_value.msg == '> OK test;2;description test 1\r\n'

        # Send single TM - 3. Tm_Meta
        self.context.rx['tm'].on_next(
            ServiceResponse(id='test',
                      type=ParameterType.get_meta,
                      value={
                          'signature': [['str', 'int'], 'str'],
                          'description': 'description test 1'
                      }))

        assert dummy_test_class.func_1_times_called == 3
        assert isinstance(dummy_test_class.func_1_last_value, Raw)
        assert dummy_test_class.func_1_last_value.msg == '> OK test;str;str;description test 1;7;4\r\n'

        # Send single TM - 4. Tc
        self.context.rx['tm'].on_next(ServiceResponse(id='test', type=ParameterType.set))

        assert dummy_test_class.func_1_times_called == 4
        assert isinstance(dummy_test_class.func_1_last_value, Raw)
        assert dummy_test_class.func_1_last_value.msg == '> OK test\r\n'

        # Send single TM - 5. Tm
        self.context.rx['tm'].on_next(
            ServiceResponse(id='test', type=ParameterType.get, value=1))

        assert dummy_test_class.func_1_times_called == 5
        assert isinstance(dummy_test_class.func_1_last_value, Raw)
        assert '> OK test;' in dummy_test_class.func_1_last_value.msg
        assert ';1;1;0;1\r\n' in dummy_test_class.func_1_last_value.msg

        # Send single TM - 6. Error
        self.context.rx['tm'].on_next(
            ServiceResponse(id='test', type=ParameterType.error, value='error msg'))

        assert dummy_test_class.func_1_times_called == 6
        assert isinstance(dummy_test_class.func_1_last_value, Raw)
        assert dummy_test_class.func_1_last_value.msg == '> ERROR test error msg\r\n'

        # Send multiple TM
        self.context.rx['tm'].on_next(ServiceResponse(id='test_3',
                                                type=ParameterType.helo))
        self.context.rx['tm'].on_next(ServiceResponse(id='test_4',
                                                type=ParameterType.helo))

        assert dummy_test_class.func_1_times_called == 8
        assert isinstance(dummy_test_class.func_1_last_value, Raw)
        assert dummy_test_class.func_1_last_value.msg == '> OK helo test_4\r\n'
