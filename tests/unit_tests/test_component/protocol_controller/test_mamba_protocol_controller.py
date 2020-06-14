import pytest
import os

from mamba.core.context import Context
from mamba.component.protocol_controller import MambaProtocolController
from mamba.core.testing.utils import CallbackTestClass
from mamba.core.msg import ServiceResponse, ServiceRequest, ParameterInfo, ParameterType
from mamba.core.exceptions import ComponentConfigException


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
            MambaProtocolController()

        assert "missing 1 required positional argument" in str(excinfo.value)

    def test_component_w_empty_context(self):
        component = MambaProtocolController(Context())
        component.initialize()

        # Test default configuration
        assert component._configuration == {
            'name': 'mamba_protocol_controller'
        }
        assert component._provider_params == {}
        assert component._io_result_subs is None

    def test_component_observer_io_service_signature(self):
        """ Test component external interface """
        component = MambaProtocolController(self.context)
        component.initialize()

        # 1 - Test 1 signature message
        self.context.rx['io_service_signature'].on_next([
            ParameterInfo(provider='test_provider',
                          param_id='test_param_1',
                          param_type=ParameterType.set,
                          signature=[['str'], 'None'],
                          description='custom command  set 1'),
            ParameterInfo(provider='test_provider',
                          param_id='test_param_2',
                          param_type=ParameterType.get,
                          signature=[['str'], 'None'],
                          description='custom command  get 2')
        ])

        assert list(component._provider_params.keys()) == [
            ('test_provider_test_param_1', ParameterType.set),
            ('test_provider_test_param_2', ParameterType.get)
        ]

        assert isinstance(
            component._provider_params[('test_provider_test_param_1',
                                        ParameterType.set)], ParameterInfo)
        assert isinstance(
            component._provider_params[('test_provider_test_param_2',
                                        ParameterType.get)], ParameterInfo)

        assert component._provider_params[('test_provider_test_param_1',
                                           ParameterType.set)].signature == [[
                                               'str'
                                           ], 'None']
        assert component._provider_params[(
            'test_provider_test_param_2',
            ParameterType.get)].type == ParameterType.get

        # 2 - Test with second signature message
        self.context.rx['io_service_signature'].on_next([
            ParameterInfo(provider='test_provider_2',
                          param_id='test_param_1',
                          param_type=ParameterType.set,
                          signature=[['str'], 'None'],
                          description='custom command  set 1')
        ])

        assert list(component._provider_params.keys()) == [
            ('test_provider_test_param_1', ParameterType.set),
            ('test_provider_test_param_2', ParameterType.get),
            ('test_provider_2_test_param_1', ParameterType.set)
        ]

        assert isinstance(
            component._provider_params[('test_provider_2_test_param_1',
                                        ParameterType.set)], ParameterInfo)

        assert component._provider_params[('test_provider_2_test_param_1',
                                           ParameterType.set)].signature == [[
                                               'str'
                                           ], 'None']
        assert component._provider_params[(
            'test_provider_2_test_param_1',
            ParameterType.set)].type == ParameterType.set

        # 3 - Test with repeated service key
        with pytest.raises(ComponentConfigException) as excinfo:
            self.context.rx['io_service_signature'].on_next([
                ParameterInfo(provider='test_provider_2',
                              param_id='test_param_1',
                              param_type=ParameterType.set,
                              signature=[['str'], 'None'],
                              description='custom command  set 1')
            ])

        assert "Received conflicting parameter key: test_provider_2_test_param_1" in str(
            excinfo.value)

        # 4 - Test with wrong signature
        with pytest.raises(ComponentConfigException) as excinfo:
            self.context.rx['io_service_signature'].on_next([
                ParameterInfo(provider='test_provider_3',
                              param_id='test_param_1',
                              param_type=ParameterType.set,
                              signature='wrong',
                              description='custom command  set 1')
            ])

        assert 'Signature of service test_provider_3 -> "test_param_1" is invalid.' \
               ' Format shall be [[arg_1, arg_2, ...], return_type]' in str(excinfo.value)

    def test_component_observer_tc(self):
        """ Test component external interface """
        dummy_test_class = CallbackTestClass()
        component = MambaProtocolController(self.context)
        component.initialize()

        # Initialize service signatures
        self.context.rx['io_service_signature'].on_next([
            ParameterInfo(provider='test_provider',
                          param_id='test_param_1',
                          param_type=ParameterType.set,
                          signature=[['str', 'int'], 'None'],
                          description='custom command  set 1'),
            ParameterInfo(provider='test_provider',
                          param_id='test_param_2',
                          param_type=ParameterType.get,
                          signature=[[], 'str'],
                          description='custom command  get 2'),
            ParameterInfo(provider='test_provider_1',
                          param_id='test_param_1',
                          param_type=ParameterType.get,
                          signature=[['int'], 'str'],
                          description='custom command  get 1')
        ])

        # Subscribe to the 'tc' that shall be published
        self.context.rx['io_service_request'].subscribe(
            dummy_test_class.test_func_1)
        self.context.rx['tm'].subscribe(dummy_test_class.test_func_2)

        # Send single TC - 1. Helo
        self.context.rx['tc'].on_next(
            ServiceRequest(id='test', type=ParameterType.helo, args=[]))

        assert dummy_test_class.func_2_times_called == 1
        assert isinstance(dummy_test_class.func_2_last_value, ServiceResponse)
        assert dummy_test_class.func_2_last_value.id == 'test'
        assert dummy_test_class.func_2_last_value.type == ParameterType.helo
        assert dummy_test_class.func_2_last_value.value is None

        # Send single msg TC - 2. Set_Meta
        self.context.rx['tc'].on_next(
            ServiceRequest(id='test_provider_test_param_1',
                           type=ParameterType.set_meta,
                           args=[]))

        assert dummy_test_class.func_2_times_called == 2
        assert isinstance(dummy_test_class.func_2_last_value, ServiceResponse)
        assert dummy_test_class.func_2_last_value.id == 'test_provider_test_param_1'
        assert dummy_test_class.func_2_last_value.type == ParameterType.set_meta
        assert dummy_test_class.func_2_last_value.value == {
            'description': 'custom command  set 1',
            'signature': [['str', 'int'], 'None']
        }

        # Send single msg TC - 3. Get_Meta
        self.context.rx['tc'].on_next(
            ServiceRequest(id='test_provider_test_param_2',
                           type=ParameterType.get_meta,
                           args=[]))

        assert dummy_test_class.func_2_times_called == 3
        assert isinstance(dummy_test_class.func_2_last_value, ServiceResponse)
        assert dummy_test_class.func_2_last_value.id == 'test_provider_test_param_2'
        assert dummy_test_class.func_2_last_value.type == ParameterType.get_meta
        assert dummy_test_class.func_2_last_value.value == {
            'description': 'custom command  get 2',
            'signature': [[], 'str']
        }

        # Send single msg TC - 3. Get_Meta - Non existing
        self.context.rx['tc'].on_next(
            ServiceRequest(id='test_provider_test_param_1',
                           type=ParameterType.get_meta,
                           args=[]))

        assert dummy_test_class.func_2_times_called == 4
        assert isinstance(dummy_test_class.func_2_last_value, ServiceResponse)
        assert dummy_test_class.func_2_last_value.id == 'test_provider_test_param_1'
        assert dummy_test_class.func_2_last_value.type == ParameterType.error
        assert dummy_test_class.func_2_last_value.value == 'Not recognized command'

        # Send single msg TC - 4. Tc
        self.context.rx['tc'].on_next(
            ServiceRequest(id='test_provider_test_param_1',
                           type=ParameterType.set,
                           args=['a', 3]))

        assert dummy_test_class.func_1_times_called == 1
        assert isinstance(dummy_test_class.func_1_last_value, ServiceRequest)
        assert dummy_test_class.func_1_last_value.provider == 'test_provider'
        assert dummy_test_class.func_1_last_value.id == 'test_param_1'
        assert dummy_test_class.func_1_last_value.type == ParameterType.set
        assert dummy_test_class.func_1_last_value.args == ['a', 3]

        self.context.rx['tc'].on_next(
            ServiceRequest(provider='test_provider',
                           id='test_param_1',
                           type=ParameterType.set,
                           args=['a', 3]))

        assert dummy_test_class.func_1_times_called == 2
        assert isinstance(dummy_test_class.func_1_last_value, ServiceRequest)
        assert dummy_test_class.func_1_last_value.provider == 'test_provider'
        assert dummy_test_class.func_1_last_value.id == 'test_param_1'
        assert dummy_test_class.func_1_last_value.type == ParameterType.set
        assert dummy_test_class.func_1_last_value.args == ['a', 3]

        # Send single msg TC - 4. Tc - Wrong number of arguments
        self.context.rx['tc'].on_next(
            ServiceRequest(id='test_provider_test_param_1',
                           type=ParameterType.set,
                           args=['a']))

        assert dummy_test_class.func_1_times_called == 3
        assert isinstance(dummy_test_class.func_1_last_value, ServiceRequest)
        assert dummy_test_class.func_1_last_value.provider == 'test_provider'
        assert dummy_test_class.func_1_last_value.id == 'test_param_1'
        assert dummy_test_class.func_1_last_value.type == ParameterType.set
        assert dummy_test_class.func_1_last_value.args == ['a']

        # Send single msg TC - 5. Tm
        self.context.rx['tc'].on_next(
            ServiceRequest(id='test_provider_test_param_2',
                           type=ParameterType.get,
                           args=[]))

        assert dummy_test_class.func_1_times_called == 4
        assert isinstance(dummy_test_class.func_1_last_value, ServiceRequest)
        assert dummy_test_class.func_1_last_value.provider == 'test_provider'
        assert dummy_test_class.func_1_last_value.id == 'test_param_2'
        assert dummy_test_class.func_1_last_value.type == ParameterType.get
        assert dummy_test_class.func_1_last_value.args == []

        self.context.rx['tc'].on_next(
            ServiceRequest(provider='test_provider',
                           id='test_param_2',
                           type=ParameterType.get,
                           args=[]))

        assert dummy_test_class.func_1_times_called == 5
        assert isinstance(dummy_test_class.func_1_last_value, ServiceRequest)
        assert dummy_test_class.func_1_last_value.provider == 'test_provider'
        assert dummy_test_class.func_1_last_value.id == 'test_param_2'
        assert dummy_test_class.func_1_last_value.type == ParameterType.get
        assert dummy_test_class.func_1_last_value.args == []

        self.context.rx['tc'].on_next(
            ServiceRequest(id='test_provider_test_param_2',
                           type=ParameterType.get,
                           args=[1]))

        assert dummy_test_class.func_1_times_called == 6
        assert isinstance(dummy_test_class.func_1_last_value, ServiceRequest)
        assert dummy_test_class.func_1_last_value.provider == 'test_provider'
        assert dummy_test_class.func_1_last_value.id == 'test_param_2'
        assert dummy_test_class.func_1_last_value.type == ParameterType.get
        assert dummy_test_class.func_1_last_value.args == [1]

        # Send unexisting TC type
        self.context.rx['tc'].on_next(
            ServiceRequest(id='test_provider_test_param_2',
                           type='wrong',
                           args=[1]))

        assert dummy_test_class.func_2_times_called == 5
        assert isinstance(dummy_test_class.func_2_last_value, ServiceResponse)
        assert dummy_test_class.func_2_last_value.provider is None
        assert dummy_test_class.func_2_last_value.id == 'test_provider_test_param_2'
        assert dummy_test_class.func_2_last_value.type == ParameterType.error
        assert dummy_test_class.func_2_last_value.value == 'Not recognized command'

        # Send unexisting TC id
        self.context.rx['tc'].on_next(
            ServiceRequest(id='TEST_TC_WRONG',
                           type=ParameterType.set,
                           args=[1]))

        assert dummy_test_class.func_2_times_called == 6
        assert isinstance(dummy_test_class.func_2_last_value, ServiceResponse)
        assert dummy_test_class.func_2_last_value.provider is None
        assert dummy_test_class.func_2_last_value.id == 'TEST_TC_WRONG'
        assert dummy_test_class.func_2_last_value.type == ParameterType.error
        assert dummy_test_class.func_2_last_value.value == 'Not recognized command'
