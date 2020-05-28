import os
import pytest
import time
from tempfile import NamedTemporaryFile

from rx import operators as op

from mamba.context import Context
from mamba.components.io_controller import RfSignalGenerator
from mamba.internal.exceptions import ComponentConfigException
from mamba.components.observable_types import Empty, IoServiceRequest, Telemetry


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

    def test_wo_context(self):
        """ Test component behaviour without required context """
        with pytest.raises(TypeError) as excinfo:
            RfSignalGenerator()

        assert "missing 1 required positional argument" in str(excinfo.value)

    def test_w_default_context_component_creation(self):
        """ Test component creation behaviour with default context """
        component = RfSignalGenerator(self.context)

        # Test default configuration load
        assert component._configuration == {
            'name': 'smb100b',
            'parameters': {
                'connected': {
                    'default': False,
                    'getter': {
                        'SMB_QUERY_CONNECTED': None
                    },
                    'setter': {
                        'SMB_CONNECT': None,
                        'SMB_DISCONNECT': None
                    }
                },
                'query_raw_result': {
                    'default': '',
                    'getter': {
                        'SMB_TM_QUERY_RAW': None
                    },
                    'setter': {
                        'SMB_TC_QUERY_RAW': None
                    }
                }
            },
            'resource-name': 'TCPIP0::1.2.3.4::INSTR',
            'topics': {
                'SMB_CLOCK_SRC': {
                    'command': 'SOURce:ROSCillator:SOURce {:}',
                    'description': 'Sets the source of the reference '
                    'frequency',
                    'signature': [['str'], 'None']
                },
                'SMB_CONNECT': {
                    'description': 'Establish Connection with SMB',
                    'key': '@connect'
                },
                'SMB_CW_FREQ': {
                    'command': 'FREQuency:CW {:}',
                    'description': 'Sets the frequency of the RF '
                    'output signal',
                    'signature': [['int'], 'None']
                },
                'SMB_DISCONNECT': {
                    'description': 'Close connection with SMB',
                    'key': '@disconnect'
                },
                'SMB_FREQ_MODE': {
                    'command': 'FREQuency:MODE {:}',
                    'description': 'Set the frequency mode for '
                    'generating the RF output signal',
                    'signature': [['str'], 'None']
                },
                'SMB_OUT_POWER': {
                    'command': 'OUTP {:}',
                    'description': 'Set the RF output signal',
                    'signature': [['str'], 'None']
                },
                'SMB_POWER_LEVEL': {
                    'command': 'POWer {:}',
                    'description': 'Sets the RF level applied to '
                    'the device under tests',
                    'signature': [['float'], 'None']
                },
                'SMB_QUERY_CLOCK_SRC': {
                    'command': 'SOURce:ROSCillator:SOURce?',
                    'description': 'Query the source of the '
                    'reference frequency',
                    'signature': [[], 'str']
                },
                'SMB_QUERY_CONNECTED': {
                    'description': 'Query the connection '
                    'status to the instrument',
                    'signature': [[], 'bool']
                },
                'SMB_QUERY_CW_FREQ': {
                    'command': 'FREQuency:CW?',
                    'description': 'Query the frequency of the '
                    'RF output signal',
                    'signature': [[], 'int']
                },
                'SMB_QUERY_FREQ_MODE': {
                    'command':
                    'FREQuency:MODE?',
                    'description':
                    'Query the frequency mode '
                    'for generating the RF '
                    'output signal',
                    'signature': [[], 'str']
                },
                'SMB_QUERY_IDN': {
                    'command': '*IDN?',
                    'description': 'Query the instrument '
                    'identification',
                    'signature': [[], 'str']
                },
                'SMB_QUERY_OUT_POWER': {
                    'command': 'OUTP?',
                    'description': 'Query the RF output signal',
                    'signature': [[], 'int']
                },
                'SMB_QUERY_POWER_LEVEL': {
                    'command': 'POWer?',
                    'description': 'Query the RF level '
                    'applied to the device '
                    'under tests',
                    'signature': [[], 'float']
                },
                'SMB_RAW': {
                    'command': '{:}',
                    'description': 'Send a raw command to the instrument',
                    'signature': [['str'], 'None']
                },
                'SMB_RST': {
                    'command': '*CLS',
                    'description': 'Clear the output buffer'
                },
                'SMB_TC_QUERY_RAW': {
                    'command': '{:}',
                    'description': 'Perform raw query to the '
                    'instrument',
                    'signature': [['str'], 'str']
                },
                'SMB_TM_QUERY_RAW': {
                    'command': '{:}',
                    'description': 'Retrieve the value of the '
                    'last raw query',
                    'signature': [[], 'str']
                }
            },
            'visa-sim': 'simulator/rf_signal_generator/rs_smb100b.yaml'
        }

        # Test custom variables default values
        assert component._shared_memory == {}
        assert component._shared_memory_getter == {}
        assert component._shared_memory_setter == {}
        assert component._service_info == {}
        assert component._inst is None
        assert component._simulation_file is None

    def test_w_default_context_component_initialization(self):
        """ Test component initialization behaviour with default context """
        component = RfSignalGenerator(self.context)
        component.initialize()

        # Test default configuration load
        assert component._configuration == {
            'name': 'smb100b',
            'parameters': {
                'connected': {
                    'default': False,
                    'getter': {
                        'SMB_QUERY_CONNECTED': None
                    },
                    'setter': {
                        'SMB_CONNECT': None,
                        'SMB_DISCONNECT': None
                    }
                },
                'query_raw_result': {
                    'default': '',
                    'getter': {
                        'SMB_TM_QUERY_RAW': None
                    },
                    'setter': {
                        'SMB_TC_QUERY_RAW': None
                    }
                }
            },
            'resource-name': 'TCPIP0::1.2.3.4::INSTR',
            'topics': {
                'SMB_CLOCK_SRC': {
                    'command': 'SOURce:ROSCillator:SOURce {:}',
                    'description': 'Sets the source of the reference '
                    'frequency',
                    'signature': [['str'], 'None']
                },
                'SMB_CONNECT': {
                    'description': 'Establish Connection with SMB',
                    'key': '@connect'
                },
                'SMB_CW_FREQ': {
                    'command': 'FREQuency:CW {:}',
                    'description': 'Sets the frequency of the RF '
                    'output signal',
                    'signature': [['int'], 'None']
                },
                'SMB_DISCONNECT': {
                    'description': 'Close connection with SMB',
                    'key': '@disconnect'
                },
                'SMB_FREQ_MODE': {
                    'command': 'FREQuency:MODE {:}',
                    'description': 'Set the frequency mode for '
                    'generating the RF output signal',
                    'signature': [['str'], 'None']
                },
                'SMB_OUT_POWER': {
                    'command': 'OUTP {:}',
                    'description': 'Set the RF output signal',
                    'signature': [['str'], 'None']
                },
                'SMB_POWER_LEVEL': {
                    'command': 'POWer {:}',
                    'description': 'Sets the RF level applied to '
                    'the device under tests',
                    'signature': [['float'], 'None']
                },
                'SMB_QUERY_CLOCK_SRC': {
                    'command': 'SOURce:ROSCillator:SOURce?',
                    'description': 'Query the source of the '
                    'reference frequency',
                    'signature': [[], 'str']
                },
                'SMB_QUERY_CONNECTED': {
                    'description': 'Query the connection '
                    'status to the instrument',
                    'signature': [[], 'bool']
                },
                'SMB_QUERY_CW_FREQ': {
                    'command': 'FREQuency:CW?',
                    'description': 'Query the frequency of the '
                    'RF output signal',
                    'signature': [[], 'int']
                },
                'SMB_QUERY_FREQ_MODE': {
                    'command':
                    'FREQuency:MODE?',
                    'description':
                    'Query the frequency mode '
                    'for generating the RF '
                    'output signal',
                    'signature': [[], 'str']
                },
                'SMB_QUERY_IDN': {
                    'command': '*IDN?',
                    'description': 'Query the instrument '
                    'identification',
                    'signature': [[], 'str']
                },
                'SMB_QUERY_OUT_POWER': {
                    'command': 'OUTP?',
                    'description': 'Query the RF output signal',
                    'signature': [[], 'int']
                },
                'SMB_QUERY_POWER_LEVEL': {
                    'command': 'POWer?',
                    'description': 'Query the RF level '
                    'applied to the device '
                    'under tests',
                    'signature': [[], 'float']
                },
                'SMB_RAW': {
                    'command': '{:}',
                    'description': 'Send a raw command to the instrument',
                    'signature': [['str'], 'None']
                },
                'SMB_RST': {
                    'command': '*CLS',
                    'description': 'Clear the output buffer'
                },
                'SMB_TC_QUERY_RAW': {
                    'command': '{:}',
                    'description': 'Perform raw query to the '
                    'instrument',
                    'signature': [['str'], 'str']
                },
                'SMB_TM_QUERY_RAW': {
                    'command': '{:}',
                    'description': 'Retrieve the value of the '
                    'last raw query',
                    'signature': [[], 'str']
                }
            },
            'visa-sim': 'simulator/rf_signal_generator/rs_smb100b.yaml'
        }

        # Test custom variables default values
        assert component._shared_memory == {
            'connected': False,
            'query_raw_result': ''
        }
        assert component._shared_memory_getter == {
            'SMB_QUERY_CONNECTED': 'connected',
            'SMB_TM_QUERY_RAW': 'query_raw_result'
        }
        assert component._shared_memory_setter == {
            'SMB_CONNECT': 'connected',
            'SMB_DISCONNECT': 'connected',
            'SMB_TC_QUERY_RAW': 'query_raw_result'
        }
        assert component._service_info == {
            'SMB_CLOCK_SRC': {
                'command': 'SOURce:ROSCillator:SOURce {:}',
                'description': 'Sets the source of the reference frequency',
                'key': None,
                'signature': [['str'], 'None']
            },
            'SMB_CONNECT': {
                'command': None,
                'description': 'Establish Connection with SMB',
                'key': '@connect',
                'signature': [[], None]
            },
            'SMB_CW_FREQ': {
                'command': 'FREQuency:CW {:}',
                'description': 'Sets the frequency of the RF output signal',
                'key': None,
                'signature': [['int'], 'None']
            },
            'SMB_DISCONNECT': {
                'command': None,
                'description': 'Close connection with SMB',
                'key': '@disconnect',
                'signature': [[], None]
            },
            'SMB_FREQ_MODE': {
                'command': 'FREQuency:MODE {:}',
                'description': 'Set the frequency mode for generating the '
                'RF output signal',
                'key': None,
                'signature': [['str'], 'None']
            },
            'SMB_OUT_POWER': {
                'command': 'OUTP {:}',
                'description': 'Set the RF output signal',
                'key': None,
                'signature': [['str'], 'None']
            },
            'SMB_POWER_LEVEL': {
                'command': 'POWer {:}',
                'description': 'Sets the RF level applied to the device '
                'under tests',
                'key': None,
                'signature': [['float'], 'None']
            },
            'SMB_QUERY_CLOCK_SRC': {
                'command': 'SOURce:ROSCillator:SOURce?',
                'description': 'Query the source of the reference '
                'frequency',
                'key': None,
                'signature': [[], 'str']
            },
            'SMB_QUERY_CONNECTED': {
                'command': None,
                'description': 'Query the connection status to the '
                'instrument',
                'key': None,
                'signature': [[], 'bool']
            },
            'SMB_QUERY_CW_FREQ': {
                'command': 'FREQuency:CW?',
                'description': 'Query the frequency of the RF output '
                'signal',
                'key': None,
                'signature': [[], 'int']
            },
            'SMB_QUERY_FREQ_MODE': {
                'command': 'FREQuency:MODE?',
                'description': 'Query the frequency mode for '
                'generating the RF output signal',
                'key': None,
                'signature': [[], 'str']
            },
            'SMB_QUERY_IDN': {
                'command': '*IDN?',
                'description': 'Query the instrument identification',
                'key': None,
                'signature': [[], 'str']
            },
            'SMB_QUERY_OUT_POWER': {
                'command': 'OUTP?',
                'description': 'Query the RF output signal',
                'key': None,
                'signature': [[], 'int']
            },
            'SMB_QUERY_POWER_LEVEL': {
                'command': 'POWer?',
                'description': 'Query the RF level applied to the '
                'device under tests',
                'key': None,
                'signature': [[], 'float']
            },
            'SMB_RAW': {
                'command': '{:}',
                'description': 'Send a raw command to the instrument',
                'key': None,
                'signature': [['str'], 'None']
            },
            'SMB_RST': {
                'command': '*CLS',
                'description': 'Clear the output buffer',
                'key': None,
                'signature': [[], None]
            },
            'SMB_TC_QUERY_RAW': {
                'command': '{:}',
                'description': 'Perform raw query to the instrument',
                'key': None,
                'signature': [['str'], 'str']
            },
            'SMB_TM_QUERY_RAW': {
                'command': '{:}',
                'description': 'Retrieve the value of the last raw query',
                'key': None,
                'signature': [[], 'str']
            }
        }
        assert component._inst is None
        assert 'rs_smb100b.yaml' in component._simulation_file

    def test_visa_sim_local_from_project_folder(self):
        """ Test component creation behaviour with default context """
        temp_file = NamedTemporaryFile(delete=False)

        temp_file_folder = temp_file.name.rsplit('/', 1)[0]
        temp_file_name = temp_file.name.rsplit('/', 1)[1]

        os.chdir(temp_file_folder)

        component = RfSignalGenerator(
            self.context, local_config={'visa-sim': temp_file_name})
        component.initialize()

        temp_file.close()

    def test_visa_sim_mamba_from_project_folder(self):
        """ Test component creation behaviour with default context """
        os.chdir('/tmp')

        component = RfSignalGenerator(self.context)
        component.initialize()

    def test_w_custom_context(self):
        """ Test component creation behaviour with default context """
        component = RfSignalGenerator(
            self.context,
            local_config={
                'name': 'custom_name',
                'visa-sim': None,
                'topics': {
                    'CUSTOM_TOPIC': {
                        'command': 'SOURce:ROSCillator:SOURce {:}',
                        'description': 'Sets the source of the reference '
                        'frequency',
                        'signature': [['str'], None]
                    }
                }
            })
        component.initialize()

        # Test default configuration load
        assert component._configuration == {
            'name': 'custom_name',
            'parameters': {
                'connected': {
                    'default': False,
                    'getter': {
                        'SMB_QUERY_CONNECTED': None
                    },
                    'setter': {
                        'SMB_CONNECT': None,
                        'SMB_DISCONNECT': None
                    }
                },
                'query_raw_result': {
                    'default': '',
                    'getter': {
                        'SMB_TM_QUERY_RAW': None
                    },
                    'setter': {
                        'SMB_TC_QUERY_RAW': None
                    }
                }
            },
            'resource-name': 'TCPIP0::1.2.3.4::INSTR',
            'topics': {
                'CUSTOM_TOPIC': {
                    'command': 'SOURce:ROSCillator:SOURce {:}',
                    'description': 'Sets the source of the reference '
                    'frequency',
                    'signature': [['str'], None]
                },
                'SMB_CLOCK_SRC': {
                    'command': 'SOURce:ROSCillator:SOURce {:}',
                    'description': 'Sets the source of the reference '
                    'frequency',
                    'signature': [['str'], 'None']
                },
                'SMB_CONNECT': {
                    'description': 'Establish Connection with SMB',
                    'key': '@connect'
                },
                'SMB_CW_FREQ': {
                    'command': 'FREQuency:CW {:}',
                    'description': 'Sets the frequency of the RF '
                    'output signal',
                    'signature': [['int'], 'None']
                },
                'SMB_DISCONNECT': {
                    'description': 'Close connection with SMB',
                    'key': '@disconnect'
                },
                'SMB_FREQ_MODE': {
                    'command': 'FREQuency:MODE {:}',
                    'description': 'Set the frequency mode for '
                    'generating the RF output signal',
                    'signature': [['str'], 'None']
                },
                'SMB_OUT_POWER': {
                    'command': 'OUTP {:}',
                    'description': 'Set the RF output signal',
                    'signature': [['str'], 'None']
                },
                'SMB_POWER_LEVEL': {
                    'command': 'POWer {:}',
                    'description': 'Sets the RF level applied to '
                    'the device under tests',
                    'signature': [['float'], 'None']
                },
                'SMB_QUERY_CLOCK_SRC': {
                    'command': 'SOURce:ROSCillator:SOURce?',
                    'description': 'Query the source of the '
                    'reference frequency',
                    'signature': [[], 'str']
                },
                'SMB_QUERY_CONNECTED': {
                    'description': 'Query the connection '
                    'status to the instrument',
                    'signature': [[], 'bool']
                },
                'SMB_QUERY_CW_FREQ': {
                    'command': 'FREQuency:CW?',
                    'description': 'Query the frequency of the '
                    'RF output signal',
                    'signature': [[], 'int']
                },
                'SMB_QUERY_FREQ_MODE': {
                    'command':
                    'FREQuency:MODE?',
                    'description':
                    'Query the frequency mode '
                    'for generating the RF '
                    'output signal',
                    'signature': [[], 'str']
                },
                'SMB_QUERY_IDN': {
                    'command': '*IDN?',
                    'description': 'Query the instrument '
                    'identification',
                    'signature': [[], 'str']
                },
                'SMB_QUERY_OUT_POWER': {
                    'command': 'OUTP?',
                    'description': 'Query the RF output signal',
                    'signature': [[], 'int']
                },
                'SMB_QUERY_POWER_LEVEL': {
                    'command': 'POWer?',
                    'description': 'Query the RF level '
                    'applied to the device '
                    'under tests',
                    'signature': [[], 'float']
                },
                'SMB_RAW': {
                    'command': '{:}',
                    'description': 'Send a raw command to the instrument',
                    'signature': [['str'], 'None']
                },
                'SMB_RST': {
                    'command': '*CLS',
                    'description': 'Clear the output buffer'
                },
                'SMB_TC_QUERY_RAW': {
                    'command': '{:}',
                    'description': 'Perform raw query to the '
                    'instrument',
                    'signature': [['str'], 'str']
                },
                'SMB_TM_QUERY_RAW': {
                    'command': '{:}',
                    'description': 'Retrieve the value of the '
                    'last raw query',
                    'signature': [[], 'str']
                }
            },
            'visa-sim': None
        }

        # Test custom variables default values
        assert component._shared_memory == {
            'connected': False,
            'query_raw_result': ''
        }
        assert component._shared_memory_getter == {
            'SMB_QUERY_CONNECTED': 'connected',
            'SMB_TM_QUERY_RAW': 'query_raw_result'
        }
        assert component._shared_memory_setter == {
            'SMB_CONNECT': 'connected',
            'SMB_DISCONNECT': 'connected',
            'SMB_TC_QUERY_RAW': 'query_raw_result'
        }
        assert component._service_info == {
            'CUSTOM_TOPIC': {
                'command': 'SOURce:ROSCillator:SOURce {:}',
                'description': 'Sets the source of the reference frequency',
                'key': None,
                'signature': [['str'], None]
            },
            'SMB_CLOCK_SRC': {
                'command': 'SOURce:ROSCillator:SOURce {:}',
                'description': 'Sets the source of the reference frequency',
                'key': None,
                'signature': [['str'], 'None']
            },
            'SMB_CONNECT': {
                'command': None,
                'description': 'Establish Connection with SMB',
                'key': '@connect',
                'signature': [[], None]
            },
            'SMB_CW_FREQ': {
                'command': 'FREQuency:CW {:}',
                'description': 'Sets the frequency of the RF output signal',
                'key': None,
                'signature': [['int'], 'None']
            },
            'SMB_DISCONNECT': {
                'command': None,
                'description': 'Close connection with SMB',
                'key': '@disconnect',
                'signature': [[], None]
            },
            'SMB_FREQ_MODE': {
                'command': 'FREQuency:MODE {:}',
                'description': 'Set the frequency mode for generating the '
                'RF output signal',
                'key': None,
                'signature': [['str'], 'None']
            },
            'SMB_OUT_POWER': {
                'command': 'OUTP {:}',
                'description': 'Set the RF output signal',
                'key': None,
                'signature': [['str'], 'None']
            },
            'SMB_POWER_LEVEL': {
                'command': 'POWer {:}',
                'description': 'Sets the RF level applied to the device '
                'under tests',
                'key': None,
                'signature': [['float'], 'None']
            },
            'SMB_QUERY_CLOCK_SRC': {
                'command': 'SOURce:ROSCillator:SOURce?',
                'description': 'Query the source of the reference '
                'frequency',
                'key': None,
                'signature': [[], 'str']
            },
            'SMB_QUERY_CONNECTED': {
                'command': None,
                'description': 'Query the connection status to the '
                'instrument',
                'key': None,
                'signature': [[], 'bool']
            },
            'SMB_QUERY_CW_FREQ': {
                'command': 'FREQuency:CW?',
                'description': 'Query the frequency of the RF output '
                'signal',
                'key': None,
                'signature': [[], 'int']
            },
            'SMB_QUERY_FREQ_MODE': {
                'command': 'FREQuency:MODE?',
                'description': 'Query the frequency mode for '
                'generating the RF output signal',
                'key': None,
                'signature': [[], 'str']
            },
            'SMB_QUERY_IDN': {
                'command': '*IDN?',
                'description': 'Query the instrument identification',
                'key': None,
                'signature': [[], 'str']
            },
            'SMB_QUERY_OUT_POWER': {
                'command': 'OUTP?',
                'description': 'Query the RF output signal',
                'key': None,
                'signature': [[], 'int']
            },
            'SMB_QUERY_POWER_LEVEL': {
                'command': 'POWer?',
                'description': 'Query the RF level applied to the '
                'device under tests',
                'key': None,
                'signature': [[], 'float']
            },
            'SMB_RAW': {
                'command': '{:}',
                'description': 'Send a raw command to the instrument',
                'key': None,
                'signature': [['str'], 'None']
            },
            'SMB_RST': {
                'command': '*CLS',
                'description': 'Clear the output buffer',
                'key': None,
                'signature': [[], None]
            },
            'SMB_TC_QUERY_RAW': {
                'command': '{:}',
                'description': 'Perform raw query to the instrument',
                'key': None,
                'signature': [['str'], 'str']
            },
            'SMB_TM_QUERY_RAW': {
                'command': '{:}',
                'description': 'Retrieve the value of the last raw query',
                'key': None,
                'signature': [[], 'str']
            }
        }
        assert component._inst is None
        assert component._simulation_file is None

    def test_w_wrong_custom_context(self):
        """ Test component creation behaviour with default context """

        # Test with wrong topics dictionary
        with pytest.raises(ComponentConfigException) as excinfo:
            RfSignalGenerator(self.context, local_config={
                'topics': 'wrong'
            }).initialize()
        assert "Topics configuration: wrong format" in str(excinfo.value)

        # In case no new topics are given, use the default ones
        component = RfSignalGenerator(self.context,
                                      local_config={'topics': {}})
        component.initialize()

        assert len(component._configuration['topics']) == 18

        # Test with missing simulation file
        with pytest.raises(ComponentConfigException) as excinfo:
            RfSignalGenerator(self.context,
                              local_config={
                                  'visa-sim': 'non-existing'
                              }).initialize()
        assert "Visa-sim file has not been found" in str(excinfo.value)

        # In case properties do not have a getter, setter or default
        component = RfSignalGenerator(
            self.context, local_config={'parameters': {
                'new_param': {}
            }})
        component.initialize()

        assert component._shared_memory == {
            'connected': False,
            'new_param': None,
            'query_raw_result': ''
        }

    def test_io_signature_publication(self):
        """ Test component io_signature observable """
        dummy_test_class = DummyTestClass()

        # Subscribe to the topic that shall be published
        self.context.rx['io_service_signature'].pipe(
            op.filter(lambda value: isinstance(value, dict))).subscribe(
                dummy_test_class.test_function)

        component = RfSignalGenerator(self.context)
        component.initialize()

        time.sleep(.1)

        assert dummy_test_class.times_called == 1
        assert dummy_test_class.last_value == {
            'provider': 'smb100b',
            'services': {
                'SMB_CLOCK_SRC': {
                    'description':
                    'Sets the source of the reference frequency',
                    'signature': [['str'], 'None']
                },
                'SMB_CONNECT': {
                    'description': 'Establish Connection with SMB',
                    'signature': [[], None]
                },
                'SMB_CW_FREQ': {
                    'description':
                    'Sets the frequency of the RF output signal',
                    'signature': [['int'], 'None']
                },
                'SMB_DISCONNECT': {
                    'description': 'Close connection with SMB',
                    'signature': [[], None]
                },
                'SMB_FREQ_MODE': {
                    'description': 'Set the frequency mode for generating the '
                    'RF output signal',
                    'signature': [['str'], 'None']
                },
                'SMB_OUT_POWER': {
                    'description': 'Set the RF output signal',
                    'signature': [['str'], 'None']
                },
                'SMB_POWER_LEVEL': {
                    'description': 'Sets the RF level applied to the device '
                    'under tests',
                    'signature': [['float'], 'None']
                },
                'SMB_QUERY_CLOCK_SRC': {
                    'description': 'Query the source of the reference '
                    'frequency',
                    'signature': [[], 'str']
                },
                'SMB_QUERY_CONNECTED': {
                    'description': 'Query the connection status to the '
                    'instrument',
                    'signature': [[], 'bool']
                },
                'SMB_QUERY_CW_FREQ': {
                    'description': 'Query the frequency of the RF output '
                    'signal',
                    'signature': [[], 'int']
                },
                'SMB_QUERY_FREQ_MODE': {
                    'description': 'Query the frequency mode for '
                    'generating the RF output signal',
                    'signature': [[], 'str']
                },
                'SMB_QUERY_IDN': {
                    'description': 'Query the instrument identification',
                    'signature': [[], 'str']
                },
                'SMB_QUERY_OUT_POWER': {
                    'description': 'Query the RF output signal',
                    'signature': [[], 'int']
                },
                'SMB_QUERY_POWER_LEVEL': {
                    'description': 'Query the RF level applied to the '
                    'device under tests',
                    'signature': [[], 'float']
                },
                'SMB_RAW': {
                    'description': 'Send a raw command to the instrument',
                    'signature': [['str'], 'None']
                },
                'SMB_RST': {
                    'description': 'Clear the output buffer',
                    'signature': [[], None]
                },
                'SMB_TC_QUERY_RAW': {
                    'description': 'Perform raw query to the instrument',
                    'signature': [['str'], 'str']
                },
                'SMB_TM_QUERY_RAW': {
                    'description': 'Retrieve the value of the last raw query',
                    'signature': [[], 'str']
                }
            }
        }

        component = RfSignalGenerator(
            self.context,
            local_config={
                'topics': {
                    'CUSTOM_TOPIC': {
                        'command': 'SOURce:ROSCillator:SOURce {:}',
                        'description': 'Sets the source of the reference '
                        'frequency',
                        'signature': [['str'], None]
                    }
                }
            })
        component.initialize()

        time.sleep(.1)

        assert dummy_test_class.times_called == 2
        assert dummy_test_class.last_value == {
            'provider': 'smb100b',
            'services': {
                'CUSTOM_TOPIC': {
                    'description': 'Sets the source of the '
                    'reference frequency',
                    'signature': [['str'], None]
                },
                'SMB_CLOCK_SRC': {
                    'description': 'Sets the source of the '
                    'reference frequency',
                    'signature': [['str'], 'None']
                },
                'SMB_CONNECT': {
                    'description': 'Establish Connection with SMB',
                    'signature': [[], None]
                },
                'SMB_CW_FREQ': {
                    'description': 'Sets the frequency of the RF '
                    'output signal',
                    'signature': [['int'], 'None']
                },
                'SMB_DISCONNECT': {
                    'description': 'Close connection with SMB',
                    'signature': [[], None]
                },
                'SMB_FREQ_MODE': {
                    'description':
                    'Set the frequency mode for '
                    'generating the RF output '
                    'signal',
                    'signature': [['str'], 'None']
                },
                'SMB_OUT_POWER': {
                    'description': 'Set the RF output signal',
                    'signature': [['str'], 'None']
                },
                'SMB_POWER_LEVEL': {
                    'description': 'Sets the RF level applied to '
                    'the device under tests',
                    'signature': [['float'], 'None']
                },
                'SMB_QUERY_CLOCK_SRC': {
                    'description': 'Query the source of the '
                    'reference frequency',
                    'signature': [[], 'str']
                },
                'SMB_QUERY_CONNECTED': {
                    'description': 'Query the connection '
                    'status to the instrument',
                    'signature': [[], 'bool']
                },
                'SMB_QUERY_CW_FREQ': {
                    'description': 'Query the frequency of the '
                    'RF output signal',
                    'signature': [[], 'int']
                },
                'SMB_QUERY_FREQ_MODE': {
                    'description':
                    'Query the frequency mode '
                    'for generating the RF '
                    'output signal',
                    'signature': [[], 'str']
                },
                'SMB_QUERY_IDN': {
                    'description': 'Query the instrument '
                    'identification',
                    'signature': [[], 'str']
                },
                'SMB_QUERY_OUT_POWER': {
                    'description': 'Query the RF output '
                    'signal',
                    'signature': [[], 'int']
                },
                'SMB_QUERY_POWER_LEVEL': {
                    'description': 'Query the RF level '
                    'applied to the device '
                    'under tests',
                    'signature': [[], 'float']
                },
                'SMB_RAW': {
                    'description': 'Send a raw command to the instrument',
                    'signature': [['str'], 'None']
                },
                'SMB_RST': {
                    'description': 'Clear the output buffer',
                    'signature': [[], None]
                },
                'SMB_TC_QUERY_RAW': {
                    'description': 'Perform raw query to the '
                    'instrument',
                    'signature': [['str'], 'str']
                },
                'SMB_TM_QUERY_RAW': {
                    'description': 'Retrieve the value of the '
                    'last raw query',
                    'signature': [[], 'str']
                }
            }
        }

    def test_io_service_request_observer(self):
        """ Test component io_service_request observer """
        component = RfSignalGenerator(self.context)
        component.initialize()
        dummy_test_class = DummyTestClass()

        # Subscribe to the topic that shall be published
        self.context.rx['io_result'].pipe(
            op.filter(lambda value: isinstance(value, Telemetry))).subscribe(
                dummy_test_class.test_function)

        # 1 - Test that component only gets activated for implemented services
        self.context.rx['io_service_request'].on_next(
            IoServiceRequest(id='NOT_EXISTING', type='any', args=[]))

        assert dummy_test_class.times_called == 0
        assert dummy_test_class.last_value is None

        # 2 - Test generic command before connection to the instrument has been established
        self.context.rx['io_service_request'].on_next(
            IoServiceRequest(id='SMB_RST', type='tc', args=[]))

        time.sleep(.1)

        assert dummy_test_class.times_called == 1
        assert dummy_test_class.last_value.id == 'SMB_RST'
        assert dummy_test_class.last_value.type == 'error'
        assert dummy_test_class.last_value.value == 'Not possible to perform command before connection is established'

        # 3 - Test connection to the instrument
        assert component._inst is None

        self.context.rx['io_service_request'].on_next(
            IoServiceRequest(id='SMB_CONNECT', type='tc', args=[]))

        time.sleep(.1)

        assert component._inst is not None
        assert dummy_test_class.times_called == 2
        assert dummy_test_class.last_value.id == 'SMB_CONNECT'
        assert dummy_test_class.last_value.type == 'tc'
        assert dummy_test_class.last_value.value is None

        # 4 - Test generic command
        self.context.rx['io_service_request'].on_next(
            IoServiceRequest(id='SMB_OUT_POWER', type='tc', args=[1]))

        time.sleep(.1)

        assert dummy_test_class.times_called == 3
        assert dummy_test_class.last_value.id == 'SMB_OUT_POWER'
        assert dummy_test_class.last_value.type == 'tc'
        assert dummy_test_class.last_value.value is None

        # 5 - Test generic query
        self.context.rx['io_service_request'].on_next(
            IoServiceRequest(id='SMB_QUERY_OUT_POWER', type='tm', args=[]))

        time.sleep(.1)

        assert dummy_test_class.times_called == 4
        assert dummy_test_class.last_value.id == 'SMB_QUERY_OUT_POWER'
        assert dummy_test_class.last_value.type == 'tm'
        assert dummy_test_class.last_value.value == '1'

        # 6 - Test shared memory set
        assert component._shared_memory == {
            'connected': 1,
            'query_raw_result': ''
        }

        self.context.rx['io_service_request'].on_next(
            IoServiceRequest(id='SMB_TC_QUERY_RAW', type='tc', args=['OUTP?']))

        time.sleep(.1)

        assert component._shared_memory == {
            'connected': 1,
            'query_raw_result': '1'
        }

        assert dummy_test_class.times_called == 5
        assert dummy_test_class.last_value.id == 'SMB_TC_QUERY_RAW'
        assert dummy_test_class.last_value.type == 'tc'
        assert dummy_test_class.last_value.value is None

        # 7 - Test shared memory get
        self.context.rx['io_service_request'].on_next(
            IoServiceRequest(id='SMB_TM_QUERY_RAW', type='tm', args=[]))

        time.sleep(.1)

        assert dummy_test_class.times_called == 6
        assert dummy_test_class.last_value.id == 'SMB_TM_QUERY_RAW'
        assert dummy_test_class.last_value.type == 'tm'
        assert dummy_test_class.last_value.value == '1'

        # 8 - Test special case of raw command
        self.context.rx['io_service_request'].on_next(
            IoServiceRequest(id='SMB_RAW', type='tc', args=['OUTP', '0']))

        time.sleep(.1)

        assert dummy_test_class.times_called == 7
        assert dummy_test_class.last_value.id == 'SMB_RAW'
        assert dummy_test_class.last_value.type == 'tc'
        assert dummy_test_class.last_value.value is None

        self.context.rx['io_service_request'].on_next(
            IoServiceRequest(id='SMB_QUERY_OUT_POWER', type='tm', args=[]))

        time.sleep(.1)

        assert dummy_test_class.times_called == 8
        assert dummy_test_class.last_value.id == 'SMB_QUERY_OUT_POWER'
        assert dummy_test_class.last_value.type == 'tm'
        assert dummy_test_class.last_value.value == '0'

    def test_connection_cases_sim_normal(self):
        dummy_test_class = DummyTestClass()

        # Subscribe to the topic that shall be published
        self.context.rx['io_result'].pipe(
            op.filter(lambda value: isinstance(value, Telemetry))).subscribe(
                dummy_test_class.test_function)

        # Test simulated normal connection to the instrument
        component = RfSignalGenerator(self.context)
        component.initialize()

        assert component._inst is None

        self.context.rx['io_service_request'].on_next(
            IoServiceRequest(id='SMB_CONNECT', type='tc', args=[]))

        time.sleep(.1)

        assert component._inst is not None
        assert dummy_test_class.times_called == 1
        assert dummy_test_class.last_value.id == 'SMB_CONNECT'
        assert dummy_test_class.last_value.type == 'tc'
        assert dummy_test_class.last_value.value is None

    def test_connection_cases_sim_wrong_instrument_address(self):
        dummy_test_class = DummyTestClass()

        # Subscribe to the topic that shall be published
        self.context.rx['io_result'].pipe(
            op.filter(lambda value: isinstance(value, Telemetry))).subscribe(
                dummy_test_class.test_function)

        # Test simulated normal connection to the instrument
        component = RfSignalGenerator(
            self.context,
            local_config={'resource-name': 'TCPIP0::4.3.2.1::INSTR'})
        component.initialize()

        assert component._inst is None

        self.context.rx['io_service_request'].on_next(
            IoServiceRequest(id='SMB_CONNECT', type='tc', args=[]))

        time.sleep(.1)

        assert component._inst is not None
        assert dummy_test_class.times_called == 1
        assert dummy_test_class.last_value.id == 'SMB_CONNECT'
        assert dummy_test_class.last_value.type == 'tc'
        assert dummy_test_class.last_value.value is None

    def test_disconnection_w_no_connection(self):
        dummy_test_class = DummyTestClass()

        # Subscribe to the topic that shall be published
        self.context.rx['io_result'].pipe(
            op.filter(lambda value: isinstance(value, Telemetry))).subscribe(
                dummy_test_class.test_function)

        # Test real connection to missing instrument
        component = RfSignalGenerator(self.context)
        component.initialize()

        assert component._inst is None

        self.context.rx['io_service_request'].on_next(
            IoServiceRequest(id='SMB_DISCONNECT', type='tc', args=[]))

        time.sleep(.1)

        assert component._inst is None
        assert dummy_test_class.times_called == 1
        assert dummy_test_class.last_value.id == 'SMB_DISCONNECT'
        assert dummy_test_class.last_value.type == 'tc'
        assert dummy_test_class.last_value.value is None

    def test_service_invalid_signature(self):
        with pytest.raises(ComponentConfigException) as excinfo:
            RfSignalGenerator(self.context,
                              local_config={
                                  'topics': {
                                      'CUSTOM_TOPIC': {
                                          'command':
                                          'SOURce:ROSCillator:SOURce {:}',
                                          'description':
                                          'Sets the source of the reference '
                                          'frequency',
                                          'signature': ['String']
                                      }
                                  }
                              }).initialize()

        assert 'Signature of service "CUSTOM_TOPIC" is invalid. Format shall' \
               ' be [[arg_1, arg_2, ...], return_type]' in str(excinfo.value)

        with pytest.raises(ComponentConfigException) as excinfo:
            RfSignalGenerator(self.context,
                              local_config={
                                  'topics': {
                                      'CUSTOM_TOPIC': {
                                          'command':
                                          'SOURce:ROSCillator:SOURce {:}',
                                          'description':
                                          'Sets the source of the reference '
                                          'frequency',
                                          'signature': ['String', str]
                                      }
                                  }
                              }).initialize()

        assert 'Signature of service "CUSTOM_TOPIC" is invalid. Format shall' \
               ' be [[arg_1, arg_2, ...], return_type]' in str(excinfo.value)

        with pytest.raises(ComponentConfigException) as excinfo:
            RfSignalGenerator(self.context,
                              local_config={
                                  'topics': {
                                      'CUSTOM_TOPIC': {
                                          'command':
                                          'SOURce:ROSCillator:SOURce {:}',
                                          'description':
                                          'Sets the source of the reference '
                                          'frequency',
                                          'signature':
                                          'String'
                                      }
                                  }
                              }).initialize()

        assert 'Signature of service "CUSTOM_TOPIC" is invalid. Format shall' \
               ' be [[arg_1, arg_2, ...], return_type]' in str(excinfo.value)

    def test_connection_cases_normal_fail(self):
        dummy_test_class = DummyTestClass()

        # Subscribe to the topic that shall be published
        self.context.rx['io_result'].pipe(
            op.filter(lambda value: isinstance(value, Telemetry))).subscribe(
                dummy_test_class.test_function)

        # Test real connection to missing instrument
        component = RfSignalGenerator(self.context,
                                      local_config={'visa-sim': None})
        component.initialize()

        assert component._inst is None

        self.context.rx['io_service_request'].on_next(
            IoServiceRequest(id='SMB_CONNECT', type='tc', args=[]))

        time.sleep(.1)

        assert component._inst is None
        assert dummy_test_class.times_called == 1
        assert dummy_test_class.last_value.id == 'SMB_CONNECT'
        assert dummy_test_class.last_value.type == 'error'
        assert dummy_test_class.last_value.value == 'Instrument is unreachable'

    def test_quit_observer(self):
        """ Test component quit observer """
        class Test:
            called = False

            def close(self):
                self.called = True

        component = RfSignalGenerator(self.context)
        component.initialize()

        # Test quit while on load window
        component._inst = Test()

        assert not component._inst.called

        self.context.rx['quit'].on_next(Empty())

        # Test connection to the instrument has been closed
        assert component._inst is None
