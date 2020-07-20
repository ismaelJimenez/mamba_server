import os
import pytest
import copy
import time
import socket

from rx import operators as op

from mamba.core.testing.utils import compose_service_info, get_config_dict, CallbackTestClass, get_provider_params_info
from mamba.core.context import Context
from mamba.mock.tcp.spacewire_gateway.hvs_h8823_gateway_tmtc_mock import H8823GatewayTmTcMock
from mamba.marketplace.components.spacewire_gateway.hvs_h8823_tmtc import H8823TmTcController
from mamba.core.exceptions import ComponentConfigException
from mamba.core.msg import Empty, ServiceRequest, ServiceResponse, ParameterType

component_path = os.path.join('marketplace', 'components', 'spacewire_gateway',
                              'hvs_h8823_tmtc')


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
            H8823TmTcController()

        assert "missing 1 required positional argument" in str(excinfo.value)

    def test_w_default_context_component_creation(self):
        """ Test component creation behaviour with default context """
        component = H8823TmTcController(self.context)

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
        assert component._instrument.tc_port == 12345
        assert component._instrument.tm_port == 12346
        assert component._instrument.encoding == 'utf-8'
        assert component._instrument.terminator_write == '\n'
        assert component._instrument.terminator_read == '\n'

    def test_w_default_context_component_initialization(self):
        """ Test component initialization behaviour with default context """
        component = H8823TmTcController(self.context)
        component.initialize()

        # Test default configuration load
        assert component._configuration == self.default_component_config

        # Test custom variables default values
        assert component._shared_memory == {
            'bytes_received_counter': '0 0 0 0',
            'connected': 0,
            'credit_error_counter': '0 0 0 0',
            'disconnect_error_counter': '0 0 0 0',
            'eep_received_counter': '0 0 0 0',
            'eep_sent_counter': '0 0 0 0',
            'eop_received_counter': '0 0 0 0',
            'eop_sent_counter': '0 0 0 0',
            'escape_error_counter': '0 0 0 0',
            'parity_error_counter': '0 0 0 0',
            'spw_link_autostart': '0 0 0 0',
            'spw_link_bytes_sent_counter': '0 0 0 0',
            'spw_link_enabled': '0 0 0 0',
            'spw_link_running': '0 0 0 0',
            'spw_link_rx_rate': '0 0 0 0',
            'spw_link_start': '0 0 0 0',
            'spw_link_status': '0 0 0 0',
            'spw_link_tcp_connected': '0 0 0 0',
            'spw_link_timecode_enabled': '0 0 0 0',
            'spw_link_tx_rate': '0 0 0 0',
            'ticks_received_counter': '0 0 0 0'
        }
        assert component._shared_memory_getter == {
            'bytes_received_counter': 'bytes_received_counter',
            'connected': 'connected',
            'credit_error_counter': 'credit_error_counter',
            'disconnect_error_counter': 'disconnect_error_counter',
            'eep_received_counter': 'eep_received_counter',
            'eep_sent_counter': 'eep_sent_counter',
            'eop_received_counter': 'eop_received_counter',
            'eop_sent_counter': 'eop_sent_counter',
            'escape_error_counter': 'escape_error_counter',
            'parity_error_counter': 'parity_error_counter',
            'spw_link_autostart': 'spw_link_autostart',
            'spw_link_bytes_sent_counter': 'spw_link_bytes_sent_counter',
            'spw_link_enabled': 'spw_link_enabled',
            'spw_link_running': 'spw_link_running',
            'spw_link_rx_rate': 'spw_link_rx_rate',
            'spw_link_start': 'spw_link_start',
            'spw_link_status': 'spw_link_status',
            'spw_link_tcp_connected': 'spw_link_tcp_connected',
            'spw_link_timecode_enabled': 'spw_link_timecode_enabled',
            'spw_link_tx_rate': 'spw_link_tx_rate',
            'ticks_received_counter': 'ticks_received_counter'
        }
        assert component._shared_memory_setter == {
            'bytes_received_counter': 'bytes_received_counter',
            'connect': 'connected',
            'credit_error_counter': 'credit_error_counter',
            'disconnect_error_counter': 'disconnect_error_counter',
            'eep_received_counter': 'eep_received_counter',
            'eep_sent_counter': 'eep_sent_counter',
            'eop_received_counter': 'eop_received_counter',
            'eop_sent_counter': 'eop_sent_counter',
            'escape_error_counter': 'escape_error_counter',
            'parity_error_counter': 'parity_error_counter',
            'spw_link_autostart': 'spw_link_autostart',
            'spw_link_bytes_sent_counter': 'spw_link_bytes_sent_counter',
            'spw_link_enabled': 'spw_link_enabled',
            'spw_link_running': 'spw_link_running',
            'spw_link_rx_rate': 'spw_link_rx_rate',
            'spw_link_start': 'spw_link_start',
            'spw_link_status': 'spw_link_status',
            'spw_link_tcp_connected': 'spw_link_tcp_connected',
            'spw_link_timecode_enabled': 'spw_link_timecode_enabled',
            'spw_link_tx_rate': 'spw_link_tx_rate',
            'ticks_received_counter': 'ticks_received_counter'
        }
        assert component._parameter_info == self.default_service_info
        assert component._inst is None
        assert component._inst_cyclic_tm is None
        assert component._inst_cyclic_tm_thread is None
        assert component._cyclic_tm_mapping == {
            'bytes_received_counter': 'SPWG_TM_SPW_RX_BYTE_CTR {:}',
            'credit_error_counter': 'SPWG_TM_SPW_CRED_ERR_CTR {:}',
            'disconnect_error_counter': 'SPWG_TM_SPW_DISC_ERR_CTR {:}',
            'eep_received_counter': 'SWPG_TM_SPW_RX_EEP_CTR {:}',
            'eep_sent_counter': 'SPWG_TM_SPW_TX_EEP_CTR {:}',
            'eop_received_counter': 'SPWG_TM_SPW_RX_EOP_CTR {:}',
            'eop_sent_counter': 'SPWG_TM_SPW_TX_EOP_CTR {:}',
            'escape_error_counter': 'SPWG_TM_SPW_ESC_ERR_CTR {:}',
            'parity_error_counter': 'SPWG_TM_SPW_PAR_ERR_CTR {:}',
            'spw_link_autostart': 'SPWG_TM_SPW_AUTOSTART {:}',
            'spw_link_bytes_sent_counter': 'SPWG_TM_SPW_TX_BYTE_CTR {:}',
            'spw_link_enabled': 'SPWG_TM_SPW_ENABLED {:}',
            'spw_link_running': 'SPWG_TM_SPW_RUNNING {:}',
            'spw_link_rx_rate': 'SPWG_TM_SPW_RX_RATE {:}',
            'spw_link_start': 'SPWG_TM_SPW_START {:}',
            'spw_link_status': 'SPWG_TM_SPW_STS {:}',
            'spw_link_tcp_connected': 'SPWG_TM_SPW_TCP_CONN {:}',
            'spw_link_timecode_enabled': 'SPWG_TM_SPW_TIMECODE_ENABLED {:}',
            'spw_link_tx_rate': 'SPWG_TM_SPW_TX_CLK {:}',
            'ticks_received_counter': 'SPWG_TM_SPW_RX_TICK_CTR {:}'
        }

        assert component._instrument.address == '0.0.0.0'
        assert component._instrument.port is None
        assert component._instrument.tc_port == 12345
        assert component._instrument.tm_port == 12346
        assert component._instrument.encoding == 'utf-8'
        assert component._instrument.terminator_write == '\n'
        assert component._instrument.terminator_read == '\n'

    def test_w_custom_context(self):
        """ Test component creation behaviour with default context """
        component = H8823TmTcController(
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
            'bytes_received_counter': '0 0 0 0',
            'connected': 0,
            'credit_error_counter': '0 0 0 0',
            'disconnect_error_counter': '0 0 0 0',
            'eep_received_counter': '0 0 0 0',
            'eep_sent_counter': '0 0 0 0',
            'eop_received_counter': '0 0 0 0',
            'eop_sent_counter': '0 0 0 0',
            'escape_error_counter': '0 0 0 0',
            'parity_error_counter': '0 0 0 0',
            'spw_link_autostart': '0 0 0 0',
            'spw_link_bytes_sent_counter': '0 0 0 0',
            'spw_link_enabled': '0 0 0 0',
            'spw_link_running': '0 0 0 0',
            'spw_link_rx_rate': '0 0 0 0',
            'spw_link_start': '0 0 0 0',
            'spw_link_status': '0 0 0 0',
            'spw_link_tcp_connected': '0 0 0 0',
            'spw_link_timecode_enabled': '0 0 0 0',
            'spw_link_tx_rate': '0 0 0 0',
            'ticks_received_counter': '0 0 0 0'
        }
        assert component._shared_memory_getter == {
            'bytes_received_counter': 'bytes_received_counter',
            'connected': 'connected',
            'credit_error_counter': 'credit_error_counter',
            'disconnect_error_counter': 'disconnect_error_counter',
            'eep_received_counter': 'eep_received_counter',
            'eep_sent_counter': 'eep_sent_counter',
            'eop_received_counter': 'eop_received_counter',
            'eop_sent_counter': 'eop_sent_counter',
            'escape_error_counter': 'escape_error_counter',
            'parity_error_counter': 'parity_error_counter',
            'spw_link_autostart': 'spw_link_autostart',
            'spw_link_bytes_sent_counter': 'spw_link_bytes_sent_counter',
            'spw_link_enabled': 'spw_link_enabled',
            'spw_link_running': 'spw_link_running',
            'spw_link_rx_rate': 'spw_link_rx_rate',
            'spw_link_start': 'spw_link_start',
            'spw_link_status': 'spw_link_status',
            'spw_link_tcp_connected': 'spw_link_tcp_connected',
            'spw_link_timecode_enabled': 'spw_link_timecode_enabled',
            'spw_link_tx_rate': 'spw_link_tx_rate',
            'ticks_received_counter': 'ticks_received_counter'
        }
        assert component._shared_memory_setter == {
            'bytes_received_counter': 'bytes_received_counter',
            'connect': 'connected',
            'credit_error_counter': 'credit_error_counter',
            'disconnect_error_counter': 'disconnect_error_counter',
            'eep_received_counter': 'eep_received_counter',
            'eep_sent_counter': 'eep_sent_counter',
            'eop_received_counter': 'eop_received_counter',
            'eop_sent_counter': 'eop_sent_counter',
            'escape_error_counter': 'escape_error_counter',
            'parity_error_counter': 'parity_error_counter',
            'spw_link_autostart': 'spw_link_autostart',
            'spw_link_bytes_sent_counter': 'spw_link_bytes_sent_counter',
            'spw_link_enabled': 'spw_link_enabled',
            'spw_link_running': 'spw_link_running',
            'spw_link_rx_rate': 'spw_link_rx_rate',
            'spw_link_start': 'spw_link_start',
            'spw_link_status': 'spw_link_status',
            'spw_link_tcp_connected': 'spw_link_tcp_connected',
            'spw_link_timecode_enabled': 'spw_link_timecode_enabled',
            'spw_link_tx_rate': 'spw_link_tx_rate',
            'ticks_received_counter': 'ticks_received_counter'
        }

        custom_service_info = compose_service_info(custom_component_config)
        assert component._parameter_info == custom_service_info
        assert component._inst is None
        assert component._inst_cyclic_tm is None
        assert component._inst_cyclic_tm_thread is None
        assert component._cyclic_tm_mapping == {
            'bytes_received_counter': 'SPWG_TM_SPW_RX_BYTE_CTR {:}',
            'credit_error_counter': 'SPWG_TM_SPW_CRED_ERR_CTR {:}',
            'disconnect_error_counter': 'SPWG_TM_SPW_DISC_ERR_CTR {:}',
            'eep_received_counter': 'SWPG_TM_SPW_RX_EEP_CTR {:}',
            'eep_sent_counter': 'SPWG_TM_SPW_TX_EEP_CTR {:}',
            'eop_received_counter': 'SPWG_TM_SPW_RX_EOP_CTR {:}',
            'eop_sent_counter': 'SPWG_TM_SPW_TX_EOP_CTR {:}',
            'escape_error_counter': 'SPWG_TM_SPW_ESC_ERR_CTR {:}',
            'parity_error_counter': 'SPWG_TM_SPW_PAR_ERR_CTR {:}',
            'spw_link_autostart': 'SPWG_TM_SPW_AUTOSTART {:}',
            'spw_link_bytes_sent_counter': 'SPWG_TM_SPW_TX_BYTE_CTR {:}',
            'spw_link_enabled': 'SPWG_TM_SPW_ENABLED {:}',
            'spw_link_running': 'SPWG_TM_SPW_RUNNING {:}',
            'spw_link_rx_rate': 'SPWG_TM_SPW_RX_RATE {:}',
            'spw_link_start': 'SPWG_TM_SPW_START {:}',
            'spw_link_status': 'SPWG_TM_SPW_STS {:}',
            'spw_link_tcp_connected': 'SPWG_TM_SPW_TCP_CONN {:}',
            'spw_link_timecode_enabled': 'SPWG_TM_SPW_TIMECODE_ENABLED {:}',
            'spw_link_tx_rate': 'SPWG_TM_SPW_TX_CLK {:}',
            'ticks_received_counter': 'SPWG_TM_SPW_RX_TICK_CTR {:}'
        }

    def test_w_wrong_custom_context(self):
        """ Test component creation behaviour with default context """

        # Test with wrong topics dictionary
        with pytest.raises(ComponentConfigException) as excinfo:
            H8823TmTcController(self.context,
                                local_config={
                                    'parameters': 'wrong'
                                }).initialize()
        assert 'Parameters configuration: wrong format' in str(excinfo.value)

        # In case no new parameters are given, use the default ones
        component = H8823TmTcController(self.context,
                                        local_config={'parameters': {}})
        component.initialize()

        assert component._configuration == self.default_component_config

        # Test with missing address
        with pytest.raises(ComponentConfigException) as excinfo:
            H8823TmTcController(self.context,
                                local_config={
                                    'instrument': {
                                        'address': None
                                    }
                                }).initialize()
        assert "Missing address in Instrument Configuration" in str(
            excinfo.value)

        # Test with missing port
        with pytest.raises(ComponentConfigException) as excinfo:
            H8823TmTcController(self.context,
                                local_config={
                                    'instrument': {
                                        'port': None
                                    }
                                }).initialize()
        assert "Missing port in Instrument Configuration" in str(excinfo.value)

        # Test case properties do not have a getter, setter or default
        component = H8823TmTcController(
            self.context, local_config={'parameters': {
                'new_param': {}
            }})
        component.initialize()

        assert component._shared_memory == {
            'bytes_received_counter': '0 0 0 0',
            'connected': 0,
            'credit_error_counter': '0 0 0 0',
            'disconnect_error_counter': '0 0 0 0',
            'eep_received_counter': '0 0 0 0',
            'eep_sent_counter': '0 0 0 0',
            'eop_received_counter': '0 0 0 0',
            'eop_sent_counter': '0 0 0 0',
            'escape_error_counter': '0 0 0 0',
            'parity_error_counter': '0 0 0 0',
            'spw_link_autostart': '0 0 0 0',
            'spw_link_bytes_sent_counter': '0 0 0 0',
            'spw_link_enabled': '0 0 0 0',
            'spw_link_running': '0 0 0 0',
            'spw_link_rx_rate': '0 0 0 0',
            'spw_link_start': '0 0 0 0',
            'spw_link_status': '0 0 0 0',
            'spw_link_tcp_connected': '0 0 0 0',
            'spw_link_timecode_enabled': '0 0 0 0',
            'spw_link_tx_rate': '0 0 0 0',
            'ticks_received_counter': '0 0 0 0'
        }

    def test_io_signature_publication(self):
        """ Test component io_signature observable """
        dummy_test_class = CallbackTestClass()

        # Subscribe to the topic that shall be published
        self.context.rx['io_service_signature'].subscribe(
            dummy_test_class.test_func_1)

        component = H8823TmTcController(self.context)
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

        component = H8823TmTcController(
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
        mock = H8823GatewayTmTcMock(self.context)
        mock.initialize()

        # Start Test
        component = H8823TmTcController(self.context)
        component.initialize()
        dummy_test_class = CallbackTestClass()

        # Subscribe to the topic that shall be published
        self.context.rx['io_result'].pipe(
            op.filter(lambda value: value.type != ParameterType.set and value.
                      type != ParameterType.error)).subscribe(
                          dummy_test_class.test_func_1)

        self.context.rx['io_result'].pipe(
            op.filter(lambda value: value.type == ParameterType.set or value.
                      type == ParameterType.error)).subscribe(
                          dummy_test_class.test_func_2)

        # 1 - Test that component only gets activated for implemented services
        self.context.rx['io_service_request'].on_next(
            ServiceRequest(
                provider='hvs_h8823_spacewire_ethernet_gateway_tmtc',
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
                provider='hvs_h8823_spacewire_ethernet_gateway_tmtc',
                id='spw_link_autostart',
                type=ParameterType.get,
                args=[]))

        time.sleep(.1)

        assert dummy_test_class.func_1_times_called == 1
        assert dummy_test_class.func_1_last_value.id == 'spw_link_autostart'
        assert dummy_test_class.func_1_last_value.type == ParameterType.get
        assert dummy_test_class.func_1_last_value.value == '0 0 0 0'

        # 3 - Test connection to the instrument
        assert component._inst is None

        self.context.rx['io_service_request'].on_next(
            ServiceRequest(
                provider='hvs_h8823_spacewire_ethernet_gateway_tmtc',
                id='connect',
                type=ParameterType.set,
                args=['1']))

        time.sleep(.1)

        assert component._inst is not None
        assert dummy_test_class.func_2_times_called == 1
        assert dummy_test_class.func_2_last_value.id == 'connect'
        assert dummy_test_class.func_2_last_value.type == ParameterType.set
        assert dummy_test_class.func_2_last_value.value is None

        assert component._inst_cyclic_tm is not None
        assert component._inst_cyclic_tm_thread is not None
        assert dummy_test_class.func_1_times_called == 21
        assert dummy_test_class.func_1_last_value.id == 'ticks_received_counter'
        assert dummy_test_class.func_1_last_value.type == ParameterType.get
        assert dummy_test_class.func_1_last_value.value == '0 0 0 0'

        # 4 - Test generic command with wrong number of parameters
        self.context.rx['io_service_request'].on_next(
            ServiceRequest(
                provider='hvs_h8823_spacewire_ethernet_gateway_tmtc',
                id='spw_link_reset',
                type=ParameterType.set,
                args=[]))

        time.sleep(.1)

        assert dummy_test_class.func_2_times_called == 2
        assert dummy_test_class.func_2_last_value.id == 'spw_link_reset'
        assert dummy_test_class.func_2_last_value.type == ParameterType.error
        assert dummy_test_class.func_2_last_value.value == "Wrong number or arguments for spw_link_reset.\n Expected: [{'port': {'type': 'int', 'range': [0, 3]}}];\n Received: []"

        # 5 - Test generic command
        self.context.rx['io_service_request'].on_next(
            ServiceRequest(
                provider='hvs_h8823_spacewire_ethernet_gateway_tmtc',
                id='spw_link_reset',
                type=ParameterType.set,
                args=['0']))

        time.sleep(.1)

        assert dummy_test_class.func_2_times_called == 3
        assert dummy_test_class.func_2_last_value.id == 'spw_link_reset'
        assert dummy_test_class.func_2_last_value.type == ParameterType.set
        assert dummy_test_class.func_2_last_value.value is None

        # 6 - Test generic query
        self.context.rx['io_service_request'].on_next(
            ServiceRequest(
                provider='hvs_h8823_spacewire_ethernet_gateway_tmtc',
                id='spw_link_enabled',
                type=ParameterType.get,
                args=[]))

        time.sleep(.1)

        assert dummy_test_class.func_1_times_called == 22
        assert dummy_test_class.func_1_last_value.id == 'spw_link_enabled'
        assert dummy_test_class.func_1_last_value.type == ParameterType.get
        assert dummy_test_class.func_1_last_value.value == '0 0 0 0'

        # 7 - Test shared memory set
        assert component._shared_memory == {
            'bytes_received_counter': '0 0 0 0',
            'connected': 1,
            'credit_error_counter': '0 0 0 0',
            'disconnect_error_counter': '0 0 0 0',
            'eep_received_counter': '0 0 0 0',
            'eep_sent_counter': '0 0 0 0',
            'eop_received_counter': '0 0 0 0',
            'eop_sent_counter': '0 0 0 0',
            'escape_error_counter': '0 0 0 0',
            'parity_error_counter': '0 0 0 0',
            'spw_link_autostart': '0 0 0 0',
            'spw_link_bytes_sent_counter': '0 0 0 0',
            'spw_link_enabled': '0 0 0 0',
            'spw_link_running': '0 0 0 0',
            'spw_link_rx_rate': '0 0 0 0',
            'spw_link_start': '0 0 0 0',
            'spw_link_status': '0 0 0 0',
            'spw_link_tcp_connected': '0 0 0 0',
            'spw_link_timecode_enabled': '0 0 0 0',
            'spw_link_tx_rate': '0 0 0 0',
            'ticks_received_counter': '0 0 0 0'
        }

        self.context.rx['io_service_request'].on_next(
            ServiceRequest(
                provider='hvs_h8823_spacewire_ethernet_gateway_tmtc',
                id='spw_link_tx_rate',
                type=ParameterType.set,
                args=['0', '10']))

        time.sleep(.1)

        assert component._shared_memory == {
            'bytes_received_counter': '0 0 0 0',
            'connected': 1,
            'credit_error_counter': '0 0 0 0',
            'disconnect_error_counter': '0 0 0 0',
            'eep_received_counter': '0 0 0 0',
            'eep_sent_counter': '0 0 0 0',
            'eop_received_counter': '0 0 0 0',
            'eop_sent_counter': '0 0 0 0',
            'escape_error_counter': '0 0 0 0',
            'parity_error_counter': '0 0 0 0',
            'spw_link_autostart': '0 0 0 0',
            'spw_link_bytes_sent_counter': '0 0 0 0',
            'spw_link_enabled': '0 0 0 0',
            'spw_link_running': '0 0 0 0',
            'spw_link_rx_rate': '0 0 0 0',
            'spw_link_start': '0 0 0 0',
            'spw_link_status': '0 0 0 0',
            'spw_link_tcp_connected': '0 0 0 0',
            'spw_link_timecode_enabled': '0 0 0 0',
            'spw_link_tx_rate': '0 0 0 0',
            'ticks_received_counter': '0 0 0 0'
        }

        assert dummy_test_class.func_2_times_called == 4
        assert dummy_test_class.func_2_last_value.id == 'spw_link_tx_rate'
        assert dummy_test_class.func_2_last_value.type == ParameterType.set
        assert dummy_test_class.func_2_last_value.value is None

        time.sleep(4.6)

        assert component._shared_memory == {
            'bytes_received_counter': '0 0 0 0',
            'connected': 1,
            'credit_error_counter': '0 0 0 0',
            'disconnect_error_counter': '0 0 0 0',
            'eep_received_counter': '0 0 0 0',
            'eep_sent_counter': '0 0 0 0',
            'eop_received_counter': '0 0 0 0',
            'eop_sent_counter': '0 0 0 0',
            'escape_error_counter': '0 0 0 0',
            'parity_error_counter': '0 0 0 0',
            'spw_link_autostart': '0 0 0 0',
            'spw_link_bytes_sent_counter': '0 0 0 0',
            'spw_link_enabled': '0 0 0 0',
            'spw_link_running': '0 0 0 0',
            'spw_link_rx_rate': '0 0 0 0',
            'spw_link_start': '0 0 0 0',
            'spw_link_status': '0 0 0 0',
            'spw_link_tcp_connected': '0 0 0 0',
            'spw_link_timecode_enabled': '0 0 0 0',
            'spw_link_tx_rate': '10 0 0 0',
            'ticks_received_counter': '0 0 0 0'
        }

        # 8 - Test shared memory get
        assert dummy_test_class.func_1_times_called == 42

        self.context.rx['io_service_request'].on_next(
            ServiceRequest(
                provider='hvs_h8823_spacewire_ethernet_gateway_tmtc',
                id='spw_link_tx_rate',
                type=ParameterType.get,
                args=[]))

        time.sleep(.1)

        assert dummy_test_class.func_1_times_called == 43
        assert dummy_test_class.func_1_last_value.id == 'spw_link_tx_rate'
        assert dummy_test_class.func_1_last_value.type == ParameterType.get
        assert dummy_test_class.func_1_last_value.value == '10 0 0 0'

        # 9 - Test disconnection to the instrument
        self.context.rx['io_service_request'].on_next(
            ServiceRequest(
                provider='hvs_h8823_spacewire_ethernet_gateway_tmtc',
                id='connect',
                type=ParameterType.set,
                args=['0']))

        time.sleep(.1)

        assert component._inst is None
        assert dummy_test_class.func_2_times_called == 5
        assert dummy_test_class.func_2_last_value.id == 'connect'
        assert dummy_test_class.func_2_last_value.type == ParameterType.set
        assert dummy_test_class.func_2_last_value.value is None

        self.context.rx['io_service_request'].on_next(
            ServiceRequest(
                provider='hvs_h8823_spacewire_ethernet_gateway_tmtc',
                id='connected',
                type=ParameterType.get,
                args=[]))

        time.sleep(.1)

        assert component._inst is None
        assert dummy_test_class.func_1_times_called == 44
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
        component = H8823TmTcController(
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
            ServiceRequest(
                provider='hvs_h8823_spacewire_ethernet_gateway_tmtc',
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
        component = H8823TmTcController(self.context)
        component.initialize()

        assert component._inst is None

        self.context.rx['io_service_request'].on_next(
            ServiceRequest(
                provider='hvs_h8823_spacewire_ethernet_gateway_tmtc',
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
        mock = H8823GatewayTmTcMock(
            self.context,
            local_config={'instrument': {
                'port': {
                    'tc': 6300,
                    'tm': 6301
                }
            }})
        mock.initialize()

        dummy_test_class = CallbackTestClass()

        # Subscribe to the topic that shall be published
        self.context.rx['io_result'].pipe(
            op.filter(lambda value: value.type != ParameterType.set and value.
                      type != ParameterType.error)).subscribe(
                          dummy_test_class.test_func_1)

        self.context.rx['io_result'].pipe(
            op.filter(lambda value: value.type == ParameterType.set or value.
                      type == ParameterType.error)).subscribe(
                          dummy_test_class.test_func_2)

        component = H8823TmTcController(
            self.context,
            local_config={
                'instrument': {
                    'port': {
                        'tc': 6300,
                        'tm': 6301
                    }
                },
                'parameters': {
                    'new_param': {
                        'description': 'New parameter description',
                        'set': {
                            'signature': [{
                                'status': {
                                    'type': 'str'
                                }
                            }, {
                                'port': {
                                    'type': 'int'
                                }
                            }],
                            'instrument_command': [{
                                'write':
                                'SPWG_TC_SPW_LINK_AUTO_{0}_{1}'
                            }, {
                                'write':
                                'SPWG_TC_SPW_LINK_{0}_{1}'
                            }]
                        }
                    }
                }
            })

        component.initialize()

        # Connect to instrument and check initial status
        self.context.rx['io_service_request'].on_next(
            ServiceRequest(
                provider='hvs_h8823_spacewire_ethernet_gateway_tmtc',
                id='connect',
                type=ParameterType.set,
                args=['1']))

        time.sleep(.1)

        assert component._shared_memory == {
            'bytes_received_counter': '0 0 0 0',
            'connected': 1,
            'credit_error_counter': '0 0 0 0',
            'disconnect_error_counter': '0 0 0 0',
            'eep_received_counter': '0 0 0 0',
            'eep_sent_counter': '0 0 0 0',
            'eop_received_counter': '0 0 0 0',
            'eop_sent_counter': '0 0 0 0',
            'escape_error_counter': '0 0 0 0',
            'parity_error_counter': '0 0 0 0',
            'spw_link_autostart': '0 0 0 0',
            'spw_link_bytes_sent_counter': '0 0 0 0',
            'spw_link_enabled': '0 0 0 0',
            'spw_link_running': '0 0 0 0',
            'spw_link_rx_rate': '0 0 0 0',
            'spw_link_start': '0 0 0 0',
            'spw_link_status': '0 0 0 0',
            'spw_link_tcp_connected': '0 0 0 0',
            'spw_link_timecode_enabled': '0 0 0 0',
            'spw_link_tx_rate': '0 0 0 0',
            'ticks_received_counter': '0 0 0 0'
        }

        assert component._inst_cyclic_tm is not None
        assert component._inst_cyclic_tm_thread is not None
        assert dummy_test_class.func_2_times_called == 1
        assert dummy_test_class.func_2_last_value.id == 'connect'
        assert dummy_test_class.func_2_last_value.type == ParameterType.set
        assert dummy_test_class.func_2_last_value.value is None

        # Call new parameter
        self.context.rx['io_service_request'].on_next(
            ServiceRequest(
                provider='hvs_h8823_spacewire_ethernet_gateway_tmtc',
                id='new_param',
                type=ParameterType.set,
                args=['ENA', '1']))

        time.sleep(.1)

        assert component._shared_memory == {
            'bytes_received_counter': '0 0 0 0',
            'connected': 1,
            'credit_error_counter': '0 0 0 0',
            'disconnect_error_counter': '0 0 0 0',
            'eep_received_counter': '0 0 0 0',
            'eep_sent_counter': '0 0 0 0',
            'eop_received_counter': '0 0 0 0',
            'eop_sent_counter': '0 0 0 0',
            'escape_error_counter': '0 0 0 0',
            'parity_error_counter': '0 0 0 0',
            'spw_link_autostart': '0 0 0 0',
            'spw_link_bytes_sent_counter': '0 0 0 0',
            'spw_link_enabled': '0 0 0 0',
            'spw_link_running': '0 0 0 0',
            'spw_link_rx_rate': '0 0 0 0',
            'spw_link_start': '0 0 0 0',
            'spw_link_status': '0 0 0 0',
            'spw_link_tcp_connected': '0 0 0 0',
            'spw_link_timecode_enabled': '0 0 0 0',
            'spw_link_tx_rate': '0 0 0 0',
            'ticks_received_counter': '0 0 0 0'
        }

        assert dummy_test_class.func_2_times_called == 2
        assert dummy_test_class.func_2_last_value.id == 'new_param'
        assert dummy_test_class.func_2_last_value.type == ParameterType.set
        assert dummy_test_class.func_2_last_value.value is None

        time.sleep(5)

        assert component._shared_memory == {
            'bytes_received_counter': '0 0 0 0',
            'connected': 1,
            'credit_error_counter': '0 0 0 0',
            'disconnect_error_counter': '0 0 0 0',
            'eep_received_counter': '0 0 0 0',
            'eep_sent_counter': '0 0 0 0',
            'eop_received_counter': '0 0 0 0',
            'eop_sent_counter': '0 0 0 0',
            'escape_error_counter': '0 0 0 0',
            'parity_error_counter': '0 0 0 0',
            'spw_link_autostart': '0 1 0 0',
            'spw_link_bytes_sent_counter': '0 0 0 0',
            'spw_link_enabled': '0 1 0 0',
            'spw_link_running': '0 0 0 0',
            'spw_link_rx_rate': '0 0 0 0',
            'spw_link_start': '0 0 0 0',
            'spw_link_status': '0 0 0 0',
            'spw_link_tcp_connected': '0 0 0 0',
            'spw_link_timecode_enabled': '0 0 0 0',
            'spw_link_tx_rate': '0 0 0 0',
            'ticks_received_counter': '0 0 0 0'
        }

        self.context.rx['quit'].on_next(Empty())

        time.sleep(1)

    def test_service_invalid_info(self):
        with pytest.raises(ComponentConfigException) as excinfo:
            H8823TmTcController(self.context,
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
            H8823TmTcController(self.context,
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
            H8823TmTcController(self.context,
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

    def test_half_tm_received(self):
        mock = H8823GatewayTmTcMock(self.context,
                                    local_config={
                                        'instrument': {
                                            'port': {
                                                'tc': 45678,
                                                'tm': 45679
                                            }
                                        },
                                        'half_tm': 1
                                    })
        mock.initialize()

        component = H8823TmTcController(
            self.context,
            local_config={'instrument': {
                'port': {
                    'tc': 45678,
                    'tm': 45679
                }
            }})
        component.initialize()

        # Connect to instrument and check initial status
        self.context.rx['io_service_request'].on_next(
            ServiceRequest(
                provider='hvs_h8823_spacewire_ethernet_gateway_tmtc',
                id='connect',
                type=ParameterType.set,
                args=['1']))

        time.sleep(1.1)

        assert component._shared_memory == {
            'bytes_received_counter': '0 0 0 0',
            'connected': 1,
            'credit_error_counter': '0 0 0 0',
            'disconnect_error_counter': '0 0 0 0',
            'eep_received_counter': '0 0 0 0',
            'eep_sent_counter': '0 0 0 0',
            'eop_received_counter': '0 0 0 0',
            'eop_sent_counter': '4 3 2 1',
            'escape_error_counter': '0 0 0 0',
            'parity_error_counter': '0 0 0 0',
            'spw_link_autostart': '0 0 0 0',
            'spw_link_bytes_sent_counter': '0 0 0 0',
            'spw_link_enabled': '0 0 0 0',
            'spw_link_running': '0 0 0 0',
            'spw_link_rx_rate': '0 0 0 0',
            'spw_link_start': '0 0 0 0',
            'spw_link_status': '0 0 0 0',
            'spw_link_tcp_connected': '0 0 0 0',
            'spw_link_timecode_enabled': '0 0 0 0',
            'spw_link_tx_rate': '0 0 0 0',
            'ticks_received_counter': '0 0 0 0'
        }

        time.sleep(2)

        assert component._shared_memory == {
            'bytes_received_counter': '0 0 0 0',
            'connected': 1,
            'credit_error_counter': '0 0 0 0',
            'disconnect_error_counter': '0 0 0 0',
            'eep_received_counter': '0 0 0 0',
            'eep_sent_counter': '0 1 2 3',
            'eop_received_counter': '0 0 0 0',
            'eop_sent_counter': '4 3 2 1',
            'escape_error_counter': '0 0 0 0',
            'parity_error_counter': '0 0 0 0',
            'spw_link_autostart': '0 0 0 0',
            'spw_link_bytes_sent_counter': '0 0 0 0',
            'spw_link_enabled': '0 0 0 0',
            'spw_link_running': '0 0 0 0',
            'spw_link_rx_rate': '0 0 0 0',
            'spw_link_start': '0 0 0 0',
            'spw_link_status': '0 0 0 0',
            'spw_link_tcp_connected': '0 0 0 0',
            'spw_link_timecode_enabled': '0 0 0 0',
            'spw_link_tx_rate': '0 0 0 0',
            'ticks_received_counter': '6 7 8 9'
        }

        self.context.rx['quit'].on_next(Empty())

        time.sleep(1)

    def test_quit_observer(self):
        """ Test component quit observer """
        class Test:
            called = False

            def close(self):
                self.called = True

        component = H8823TmTcController(self.context)
        component.initialize()

        # Test quit while on load window
        component._inst = Test()

        assert not component._inst.called

        self.context.rx['quit'].on_next(Empty())

        # Test connection to the instrument has been closed
        assert component._inst is None
