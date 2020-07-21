import os
import pytest
import copy
import time

from rx import operators as op

from mamba.core.testing.utils import compose_service_info, get_config_dict, CallbackTestClass, get_provider_params_info
from mamba.core.context import Context
from mamba.mock.tcp.spacewire_gateway.hvs_h8823_gateway_spw_rmap_mock import H8823GatewaySpwRmapMock
from mamba.marketplace.components.spacewire_gateway.hvs_h8823_rmap import H8823SpwRmapController
from mamba.core.exceptions import ComponentConfigException
from mamba.core.msg import Empty, ServiceRequest, ServiceResponse, ParameterType

component_path = os.path.join('marketplace', 'components', 'spacewire_gateway',
                              'hvs_h8823_rmap')


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
            H8823SpwRmapController()

        assert "missing 1 required positional argument" in str(excinfo.value)

    def test_w_default_context_component_creation(self):
        """ Test component creation behaviour with default context """
        component = H8823SpwRmapController(self.context)

        # Test default configuration load
        assert component._configuration == self.default_component_config

        # Test custom variables default values
        assert component._shared_memory == {}
        assert component._shared_memory_getter == {}
        assert component._shared_memory_setter == {}
        assert component._parameter_info == {}
        assert component._inst is None

        assert component._instrument.address == '0.0.0.0'
        assert component._instrument.port == 5002
        assert component._instrument.encoding == 'ascii'
        assert component._instrument.terminator_write == '\r\n'
        assert component._instrument.terminator_read == '\n'
        assert component._instrument.reply_timeout == 10

        assert component._rmap.target_logical_address == 0x32
        assert component._rmap.protocol_identifier == 1
        assert component._rmap.key == 0x20
        assert component._rmap.initiator_logical_address == 0x20
        assert component._rmap.transaction_id == 1

    def test_w_default_context_component_initialization(self):
        """ Test component initialization behaviour with default context """
        component = H8823SpwRmapController(self.context)
        component.initialize()

        # Test default configuration load
        assert component._configuration == self.default_component_config

        # Test custom variables default values
        assert component._shared_memory == {
            'connected': 0,
            'last_raw_cmd': '',
            'last_raw_reply': '',
            'raw_query': '',
            'read_inc_addr': '',
            'read_single_addr': ''
        }
        assert component._shared_memory_getter == {
            'connected': 'connected',
            'last_raw_cmd': 'last_raw_cmd',
            'last_raw_reply': 'last_raw_reply',
            'raw_query': 'raw_query',
            'read_inc_addr': 'read_inc_addr',
            'read_single_addr': 'read_single_addr'
        }
        assert component._shared_memory_setter == {
            'connect': 'connected',
            'last_raw_cmd': 'last_raw_cmd',
            'last_raw_reply': 'last_raw_reply',
            'raw_query': 'raw_query',
            'read_inc_addr': 'read_inc_addr',
            'read_single_addr': 'read_single_addr'
        }
        assert component._parameter_info == self.default_service_info
        assert component._inst is None

        assert component._instrument.address == '0.0.0.0'
        assert component._instrument.port == 5002
        assert component._instrument.encoding == 'ascii'
        assert component._instrument.terminator_write == '\r\n'
        assert component._instrument.terminator_read == '\n'
        assert component._instrument.reply_timeout == 10

        assert component._rmap.target_logical_address == 0x32
        assert component._rmap.protocol_identifier == 1
        assert component._rmap.key == 0x20
        assert component._rmap.initiator_logical_address == 0x20
        assert component._rmap.transaction_id == 1

    def test_w_custom_context(self):
        """ Test component creation behaviour with default context """
        component = H8823SpwRmapController(
            self.context,
            local_config={
                'name': 'custom_name',
                'instrument': {
                    'port': 8078
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
        custom_component_config['instrument']['port'] = 8078
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
            'last_raw_cmd': '',
            'last_raw_reply': '',
            'raw_query': '',
            'read_inc_addr': '',
            'read_single_addr': ''
        }
        assert component._shared_memory_getter == {
            'connected': 'connected',
            'last_raw_cmd': 'last_raw_cmd',
            'last_raw_reply': 'last_raw_reply',
            'raw_query': 'raw_query',
            'read_inc_addr': 'read_inc_addr',
            'read_single_addr': 'read_single_addr'
        }
        assert component._shared_memory_setter == {
            'connect': 'connected',
            'last_raw_cmd': 'last_raw_cmd',
            'last_raw_reply': 'last_raw_reply',
            'raw_query': 'raw_query',
            'read_inc_addr': 'read_inc_addr',
            'read_single_addr': 'read_single_addr'
        }

        custom_service_info = compose_service_info(custom_component_config)
        assert component._parameter_info == custom_service_info
        assert component._inst is None

    def test_w_wrong_custom_context(self):
        """ Test component creation behaviour with default context """

        # Test with wrong topics dictionary
        with pytest.raises(ComponentConfigException) as excinfo:
            H8823SpwRmapController(self.context,
                                   local_config={
                                       'parameters': 'wrong'
                                   }).initialize()
        assert 'Parameters configuration: wrong format' in str(excinfo.value)

        # In case no new parameters are given, use the default ones
        component = H8823SpwRmapController(self.context,
                                           local_config={'parameters': {}})
        component.initialize()

        assert component._configuration == self.default_component_config

        # Test with missing address
        with pytest.raises(ComponentConfigException) as excinfo:
            H8823SpwRmapController(self.context,
                                   local_config={
                                       'instrument': {
                                           'address': None
                                       }
                                   }).initialize()
        assert "Missing address in Instrument Configuration" in str(
            excinfo.value)

        # Test with missing port
        with pytest.raises(ComponentConfigException) as excinfo:
            H8823SpwRmapController(self.context,
                                   local_config={
                                       'instrument': {
                                           'port': None
                                       }
                                   }).initialize()
        assert "Missing port in Instrument Configuration" in str(excinfo.value)

        # Test case properties do not have a getter, setter or default
        component = H8823SpwRmapController(
            self.context, local_config={'parameters': {
                'new_param': {}
            }})
        component.initialize()

        assert component._shared_memory == {
            'connected': 0,
            'last_raw_cmd': '',
            'last_raw_reply': '',
            'raw_query': '',
            'read_inc_addr': '',
            'read_single_addr': ''
        }

    def test_io_signature_publication(self):
        """ Test component io_signature observable """
        dummy_test_class = CallbackTestClass()

        # Subscribe to the topic that shall be published
        self.context.rx['io_service_signature'].subscribe(
            dummy_test_class.test_func_1)

        component = H8823SpwRmapController(self.context)
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

        component = H8823SpwRmapController(
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
        mock = H8823GatewaySpwRmapMock(self.context)
        mock.initialize()

        # Start Test
        component = H8823SpwRmapController(self.context)
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
                provider='hvs_h8823_spacewire_ethernet_gateway_rmap',
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
                provider='hvs_h8823_spacewire_ethernet_gateway_rmap',
                id='read_single_addr',
                type=ParameterType.get,
                args=[]))

        time.sleep(.1)

        assert dummy_test_class.func_1_times_called == 1
        assert dummy_test_class.func_1_last_value.id == 'read_single_addr'
        assert dummy_test_class.func_1_last_value.type == ParameterType.get
        assert dummy_test_class.func_1_last_value.value == ''

        self.context.rx['io_service_request'].on_next(
            ServiceRequest(
                provider='hvs_h8823_spacewire_ethernet_gateway_rmap',
                id='read_single_addr',
                type=ParameterType.set,
                args=['0']))

        time.sleep(.1)

        assert dummy_test_class.func_1_times_called == 2
        assert dummy_test_class.func_1_last_value.id == 'read_single_addr'
        assert dummy_test_class.func_1_last_value.type == ParameterType.error
        assert dummy_test_class.func_1_last_value.value == 'Not possible to perform command before connection is established'

        # 3 - Test connection to the instrument
        assert component._inst is None

        self.context.rx['io_service_request'].on_next(
            ServiceRequest(
                provider='hvs_h8823_spacewire_ethernet_gateway_rmap',
                id='connect',
                type=ParameterType.set,
                args=['1']))

        time.sleep(.1)

        assert component._inst is not None
        assert dummy_test_class.func_1_times_called == 3
        assert dummy_test_class.func_1_last_value.id == 'connect'
        assert dummy_test_class.func_1_last_value.type == ParameterType.set
        assert dummy_test_class.func_1_last_value.value is None

        # 4 - Test read single address
        last_raw_reply = component._shared_memory['last_raw_reply']

        self.context.rx['io_service_request'].on_next(
            ServiceRequest(
                provider='hvs_h8823_spacewire_ethernet_gateway_rmap',
                id='read_single_addr',
                type=ParameterType.set,
                args=['0']))

        time.sleep(.1)

        assert dummy_test_class.func_1_times_called == 4
        assert dummy_test_class.func_1_last_value.id == 'read_single_addr'
        assert dummy_test_class.func_1_last_value.type == ParameterType.set
        assert dummy_test_class.func_1_last_value.value is None

        assert component._shared_memory[
            'last_raw_cmd'] == '3201482020000100000000000000041D'
        assert component._shared_memory['last_raw_reply'] != last_raw_reply
        last_raw_reply = component._shared_memory['last_raw_reply']

        self.context.rx['io_service_request'].on_next(
            ServiceRequest(
                provider='hvs_h8823_spacewire_ethernet_gateway_rmap',
                id='read_single_addr',
                type=ParameterType.get,
                args=[]))

        time.sleep(.1)

        assert dummy_test_class.func_1_times_called == 5
        assert dummy_test_class.func_1_last_value.id == 'read_single_addr'
        assert dummy_test_class.func_1_last_value.type == ParameterType.get
        assert dummy_test_class.func_1_last_value.value == '00000000'

        # 5 - Test raw write
        self.context.rx['io_service_request'].on_next(
            ServiceRequest(
                provider='hvs_h8823_spacewire_ethernet_gateway_rmap',
                id='raw_write',
                type=ParameterType.set,
                args=['32016420200001000000000000000170aba4']))

        time.sleep(.1)

        assert dummy_test_class.func_1_times_called == 6
        assert dummy_test_class.func_1_last_value.id == 'raw_write'
        assert dummy_test_class.func_1_last_value.type == ParameterType.set
        assert dummy_test_class.func_1_last_value.value is None

        assert component._shared_memory[
            'last_raw_cmd'] == '32016420200001000000000000000170aba4'
        assert component._shared_memory['last_raw_reply'] == last_raw_reply

        self.context.rx['io_service_request'].on_next(
            ServiceRequest(
                provider='hvs_h8823_spacewire_ethernet_gateway_rmap',
                id='read_single_addr',
                type=ParameterType.set,
                args=['0']))

        time.sleep(.1)

        self.context.rx['io_service_request'].on_next(
            ServiceRequest(
                provider='hvs_h8823_spacewire_ethernet_gateway_rmap',
                id='read_single_addr',
                type=ParameterType.get,
                args=[]))

        time.sleep(.1)

        assert dummy_test_class.func_1_times_called == 8
        assert dummy_test_class.func_1_last_value.id == 'read_single_addr'
        assert dummy_test_class.func_1_last_value.type == ParameterType.get
        assert dummy_test_class.func_1_last_value.value == '000000AB'

        # 6 - Test raw query
        self.context.rx['io_service_request'].on_next(
            ServiceRequest(
                provider='hvs_h8823_spacewire_ethernet_gateway_rmap',
                id='raw_query',
                type=ParameterType.set,
                args=['3201482020000100000000000000041D']))

        time.sleep(.1)

        assert dummy_test_class.func_1_times_called == 9
        assert dummy_test_class.func_1_last_value.id == 'raw_query'
        assert dummy_test_class.func_1_last_value.type == ParameterType.set
        assert dummy_test_class.func_1_last_value.value is None

        assert component._shared_memory[
            'last_raw_cmd'] == '3201482020000100000000000000041D'
        assert component._shared_memory['last_raw_reply'] != last_raw_reply

        self.context.rx['io_service_request'].on_next(
            ServiceRequest(
                provider='hvs_h8823_spacewire_ethernet_gateway_rmap',
                id='raw_query',
                type=ParameterType.get,
                args=[]))

        time.sleep(.1)

        assert dummy_test_class.func_1_times_called == 10
        assert dummy_test_class.func_1_last_value.id == 'raw_query'
        assert dummy_test_class.func_1_last_value.type == ParameterType.get
        assert dummy_test_class.func_1_last_value.value == component._shared_memory[
            'last_raw_reply']

        # 7 - Test get last raw cmd/reply
        self.context.rx['io_service_request'].on_next(
            ServiceRequest(
                provider='hvs_h8823_spacewire_ethernet_gateway_rmap',
                id='last_raw_cmd',
                type=ParameterType.get,
                args=[]))

        time.sleep(.1)

        assert dummy_test_class.func_1_times_called == 11
        assert dummy_test_class.func_1_last_value.id == 'last_raw_cmd'
        assert dummy_test_class.func_1_last_value.type == ParameterType.get
        assert dummy_test_class.func_1_last_value.value == '3201482020000100000000000000041D'

        self.context.rx['io_service_request'].on_next(
            ServiceRequest(
                provider='hvs_h8823_spacewire_ethernet_gateway_rmap',
                id='last_raw_reply',
                type=ParameterType.get,
                args=[]))

        time.sleep(.1)

        assert dummy_test_class.func_1_times_called == 12
        assert dummy_test_class.func_1_last_value.id == 'last_raw_reply'
        assert dummy_test_class.func_1_last_value.type == ParameterType.get
        assert dummy_test_class.func_1_last_value.value == component._shared_memory[
            'last_raw_reply']

        # 8 - Test special case of msg command with multiple args
        self.context.rx['io_service_request'].on_next(
            ServiceRequest(
                provider='hvs_h8823_spacewire_ethernet_gateway_rmap',
                id='write_inc_addr_no_verify_send_reply',
                type=ParameterType.set,
                args=['ABCD', 'AB']))

        time.sleep(.1)

        assert dummy_test_class.func_1_times_called == 13
        assert dummy_test_class.func_1_last_value.id == 'write_inc_addr_no_verify_send_reply'
        assert dummy_test_class.func_1_last_value.type == ParameterType.set
        assert dummy_test_class.func_1_last_value.value is None

        self.context.rx['io_service_request'].on_next(
            ServiceRequest(
                provider='hvs_h8823_spacewire_ethernet_gateway_rmap',
                id='read_single_addr',
                type=ParameterType.set,
                args=['ABCD']))

        time.sleep(.1)

        self.context.rx['io_service_request'].on_next(
            ServiceRequest(
                provider='hvs_h8823_spacewire_ethernet_gateway_rmap',
                id='read_single_addr',
                type=ParameterType.get,
                args=[]))

        time.sleep(.1)

        assert dummy_test_class.func_1_times_called == 15
        assert dummy_test_class.func_1_last_value.id == 'read_single_addr'
        assert dummy_test_class.func_1_last_value.type == ParameterType.get
        assert dummy_test_class.func_1_last_value.value == '000000AB'

        # 9 - Test reply status failed
        self.context.rx['io_service_request'].on_next(
            ServiceRequest(
                provider='hvs_h8823_spacewire_ethernet_gateway_rmap',
                id='read_single_addr',
                type=ParameterType.set,
                args=['B']))

        time.sleep(.1)

        assert dummy_test_class.func_1_times_called == 16
        assert dummy_test_class.func_1_last_value.id == 'read_single_addr'
        assert dummy_test_class.func_1_last_value.type == ParameterType.error
        assert dummy_test_class.func_1_last_value.value == 'RMAP Reply error'

        # 10 - Test reply with delay
        self.context.rx['io_service_request'].on_next(
            ServiceRequest(
                provider='hvs_h8823_spacewire_ethernet_gateway_rmap',
                id='read_single_addr',
                type=ParameterType.set,
                args=['D']))

        time.sleep(.1)

        assert dummy_test_class.func_1_times_called == 17
        assert dummy_test_class.func_1_last_value.id == 'read_single_addr'
        assert dummy_test_class.func_1_last_value.type == ParameterType.set
        assert dummy_test_class.func_1_last_value.value is None

        self.context.rx['io_service_request'].on_next(
            ServiceRequest(
                provider='hvs_h8823_spacewire_ethernet_gateway_rmap',
                id='read_single_addr',
                type=ParameterType.get,
                args=[]))

        time.sleep(.1)

        assert dummy_test_class.func_1_times_called == 18
        assert dummy_test_class.func_1_last_value.id == 'read_single_addr'
        assert dummy_test_class.func_1_last_value.type == ParameterType.get
        assert dummy_test_class.func_1_last_value.value == '00000000'

        # 11 - Test disconnection to the instrument
        self.context.rx['io_service_request'].on_next(
            ServiceRequest(
                provider='hvs_h8823_spacewire_ethernet_gateway_rmap',
                id='connect',
                type=ParameterType.set,
                args=['0']))

        time.sleep(.1)

        assert component._inst is None
        assert dummy_test_class.func_1_times_called == 19
        assert dummy_test_class.func_1_last_value.id == 'connect'
        assert dummy_test_class.func_1_last_value.type == ParameterType.set
        assert dummy_test_class.func_1_last_value.value is None

        self.context.rx['io_service_request'].on_next(
            ServiceRequest(
                provider='hvs_h8823_spacewire_ethernet_gateway_rmap',
                id='connected',
                type=ParameterType.get,
                args=[]))

        time.sleep(.1)

        assert component._inst is None
        assert dummy_test_class.func_1_times_called == 20
        assert dummy_test_class.func_1_last_value.id == 'connected'
        assert dummy_test_class.func_1_last_value.type == ParameterType.get
        assert dummy_test_class.func_1_last_value.value == 0

        self.context.rx['quit'].on_next(Empty())
        time.sleep(1)

    def test_rmap_failed_format(self):
        # Start Mock
        mock = H8823GatewaySpwRmapMock(
            self.context, local_config={'instrument': {
                'port': 60000
            }})
        mock.initialize()

        # Start Test
        component = H8823SpwRmapController(
            self.context, local_config={'instrument': {
                'port': 60000
            }})
        component.initialize()
        dummy_test_class = CallbackTestClass()

        # Subscribe to the topic that shall be published
        self.context.rx['io_result'].pipe(
            op.filter(
                lambda value: isinstance(value, ServiceResponse))).subscribe(
                    dummy_test_class.test_func_1)

        self.context.rx['io_service_request'].on_next(
            ServiceRequest(
                provider='hvs_h8823_spacewire_ethernet_gateway_rmap',
                id='connect',
                type=ParameterType.set,
                args=['1']))

        time.sleep(.1)

        self.context.rx['io_service_request'].on_next(
            ServiceRequest(
                provider='hvs_h8823_spacewire_ethernet_gateway_rmap',
                id='write_inc_addr_no_verify_send_reply',
                type=ParameterType.set,
                args=['ABCD012345678ABCD012345678ABCD012345678', 'AB']))

        time.sleep(.1)

        assert dummy_test_class.func_1_times_called == 2
        assert dummy_test_class.func_1_last_value.id == 'write_inc_addr_no_verify_send_reply'
        assert dummy_test_class.func_1_last_value.type == ParameterType.set
        assert dummy_test_class.func_1_last_value.value is None

        assert component._shared_memory[
            'last_raw_cmd'] == '32016C2020000100123456780000013BABA4'

        self.context.rx['io_service_request'].on_next(
            ServiceRequest(
                provider='hvs_h8823_spacewire_ethernet_gateway_rmap',
                id='read_single_addr',
                type=ParameterType.set,
                args=['ABCD012345678ABCD012345678ABCD012345678']))

        time.sleep(.1)

        assert dummy_test_class.func_1_times_called == 3
        assert dummy_test_class.func_1_last_value.id == 'read_single_addr'
        assert dummy_test_class.func_1_last_value.type == ParameterType.set
        assert dummy_test_class.func_1_last_value.value is None

        assert component._shared_memory[
            'last_raw_cmd'] == '320148202000020012345678000004DC'

        self.context.rx['io_service_request'].on_next(
            ServiceRequest(
                provider='hvs_h8823_spacewire_ethernet_gateway_rmap',
                id='read_single_addr',
                type=ParameterType.get,
                args=[]))

        time.sleep(.1)

        assert dummy_test_class.func_1_times_called == 4
        assert dummy_test_class.func_1_last_value.id == 'read_single_addr'
        assert dummy_test_class.func_1_last_value.type == ParameterType.get
        assert dummy_test_class.func_1_last_value.value == '000000AB'

        self.context.rx['io_service_request'].on_next(
            ServiceRequest(
                provider='hvs_h8823_spacewire_ethernet_gateway_rmap',
                id='write_inc_addr_no_verify_send_reply',
                type=ParameterType.set,
                args=['1', 'A']))

        time.sleep(.1)

        assert dummy_test_class.func_1_times_called == 5
        assert dummy_test_class.func_1_last_value.id == 'write_inc_addr_no_verify_send_reply'
        assert dummy_test_class.func_1_last_value.type == ParameterType.error
        assert dummy_test_class.func_1_last_value.value == 'Parameter error'

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
        component = H8823SpwRmapController(
            self.context, local_config={'instrument': {
                'port': 8095
            }})
        component.initialize()

        assert component._inst is None

        self.context.rx['io_service_request'].on_next(
            ServiceRequest(
                provider='hvs_h8823_spacewire_ethernet_gateway_rmap',
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
        component = H8823SpwRmapController(self.context)
        component.initialize()

        assert component._inst is None

        self.context.rx['io_service_request'].on_next(
            ServiceRequest(
                provider='hvs_h8823_spacewire_ethernet_gateway_rmap',
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
            H8823SpwRmapController(self.context,
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
            H8823SpwRmapController(self.context,
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
            H8823SpwRmapController(self.context,
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
        mock = H8823GatewaySpwRmapMock(
            self.context, local_config={'instrument': {
                'port': 60001
            }})
        mock.initialize()

        # Start Test
        component = H8823SpwRmapController(
            self.context, local_config={'instrument': {
                'port': 60001
            }})
        component.initialize()
        dummy_test_class = CallbackTestClass()

        # Subscribe to the topic that shall be published
        self.context.rx['io_result'].pipe(
            op.filter(
                lambda value: isinstance(value, ServiceResponse))).subscribe(
                    dummy_test_class.test_func_1)

        # 1 - Test connection to the instrument
        assert component._inst is None

        self.context.rx['io_service_request'].on_next(
            ServiceRequest(
                provider='hvs_h8823_spacewire_ethernet_gateway_rmap',
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
            ServiceRequest(
                provider='hvs_h8823_spacewire_ethernet_gateway_rmap',
                id='read_single_addr',
                type=ParameterType.set,
                args=['0']))

        time.sleep(.1)

        assert dummy_test_class.func_1_times_called == 2
        assert dummy_test_class.func_1_last_value.id == 'read_single_addr'
        assert dummy_test_class.func_1_last_value.type == ParameterType.set
        assert dummy_test_class.func_1_last_value.value is None

        # Force connection close
        component._inst.close()

        self.context.rx['io_service_request'].on_next(
            ServiceRequest(
                provider='hvs_h8823_spacewire_ethernet_gateway_rmap',
                id='read_single_addr',
                type=ParameterType.set,
                args=['0']))

        time.sleep(.1)

        assert dummy_test_class.func_1_times_called == 3
        assert dummy_test_class.func_1_last_value.id == 'read_single_addr'
        assert dummy_test_class.func_1_last_value.type == ParameterType.set
        assert dummy_test_class.func_1_last_value.value is None

        self.context.rx['quit'].on_next(Empty())

        time.sleep(1)

    def test_quit_observer(self):
        """ Test component quit observer """
        class Test:
            called = False

            def close(self):
                self.called = True

        component = H8823SpwRmapController(self.context)
        component.initialize()

        # Test quit while on load window
        component._inst = Test()

        assert not component._inst.called

        self.context.rx['quit'].on_next(Empty())

        # Test connection to the instrument has been closed
        assert component._inst is None
