import pytest
import time
import socket

from mamba.core.context import Context
from mamba.core.testing.utils import CallbackTestClass
from mamba.component.protocol_translator import HvsProtocolTranslator
from mamba.component.mamba_tmtc import TcpSingleSocketServer
from mamba.component.protocol_controller import MambaProtocolController
from mamba.core.msg import Raw, ServiceResponse, ServiceRequest, ParameterType, ParameterInfo


def client_tc(ip, port, message):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.connect((ip, port))
        sock.sendall(bytes(message, 'ascii'))


class TestClass:
    def setup_method(self):
        """ setup_method called for every method """
        self.context = Context()

    def teardown_method(self):
        """ teardown_method called for every method """
        del self.context

    def test_component_tc_socket_hvs_tmtc(self):
        """ Test component external interface """
        dummy_test_class = CallbackTestClass()
        server = TcpSingleSocketServer(self.context)
        controller = HvsProtocolTranslator(self.context)
        protocol = MambaProtocolController(self.context)
        server.initialize()
        controller.initialize()
        protocol.initialize()

        # Subscribe to the 'tc' that shall be published
        self.context.rx['io_service_request'].subscribe(
            dummy_test_class.test_func_1)

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

        # Send single msg TC - 1. Set
        client_tc('127.0.0.1', 8080, 'tc test_provider_test_param_1 3\r\n')
        time.sleep(0.1)

        assert dummy_test_class.func_1_times_called == 1
        assert isinstance(dummy_test_class.func_1_last_value, ServiceRequest)
        assert dummy_test_class.func_1_last_value.provider == 'test_provider'
        assert dummy_test_class.func_1_last_value.id == 'test_param_1'
        assert dummy_test_class.func_1_last_value.type == ParameterType.set
        assert dummy_test_class.func_1_last_value.args == ['3']

        client_tc('127.0.0.1', 8080,
                  'tc test_provider_test_param_1 3 "arg_2"\r\n')
        time.sleep(0.1)

        assert dummy_test_class.func_1_times_called == 2
        assert isinstance(dummy_test_class.func_1_last_value, ServiceRequest)
        assert dummy_test_class.func_1_last_value.provider == 'test_provider'
        assert dummy_test_class.func_1_last_value.id == 'test_param_1'
        assert dummy_test_class.func_1_last_value.type == ParameterType.set
        assert dummy_test_class.func_1_last_value.args == ['3', 'arg_2']

        # Send single msg TC - 5. Get
        client_tc('127.0.0.1', 8080, 'tm test_provider_test_param_2 \r\n')
        time.sleep(0.1)

        assert dummy_test_class.func_1_times_called == 3
        assert isinstance(dummy_test_class.func_1_last_value, ServiceRequest)
        assert dummy_test_class.func_1_last_value.provider == 'test_provider'
        assert dummy_test_class.func_1_last_value.id == 'test_param_2'
        assert dummy_test_class.func_1_last_value.type == ParameterType.get
        assert dummy_test_class.func_1_last_value.args == []

        client_tc('127.0.0.1', 8080, 'tm test_provider_test_param_2\r\n')
        time.sleep(0.1)

        assert dummy_test_class.func_1_times_called == 4
        assert isinstance(dummy_test_class.func_1_last_value, ServiceRequest)
        assert dummy_test_class.func_1_last_value.provider == 'test_provider'
        assert dummy_test_class.func_1_last_value.id == 'test_param_2'
        assert dummy_test_class.func_1_last_value.type == ParameterType.get
        assert dummy_test_class.func_1_last_value.args == []

        client_tc('127.0.0.1', 8080, 'tm test_provider_test_param_2 5\r\n')
        time.sleep(0.1)

        assert dummy_test_class.func_1_times_called == 5
        assert isinstance(dummy_test_class.func_1_last_value, ServiceRequest)
        assert dummy_test_class.func_1_last_value.provider == 'test_provider'
        assert dummy_test_class.func_1_last_value.id == 'test_param_2'
        assert dummy_test_class.func_1_last_value.type == ParameterType.get
        assert dummy_test_class.func_1_last_value.args == ['5']

        # Close open threads
        server._close()

    def test_component_tm_hvs_tmtc_socket(self):
        """ Test component external interface """
        server = TcpSingleSocketServer(self.context)
        controller = HvsProtocolTranslator(self.context)
        protocol = MambaProtocolController(self.context)
        server.initialize()
        controller.initialize()
        protocol.initialize()

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

        # Establish socket connection
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.connect(('127.0.0.1', 8080))
            time.sleep(.1)

            # Send single TM - 1. Helo
            client_tc('127.0.0.1', 8080, "helo test\r\n")
            time.sleep(0.1)
            assert str(sock.recv(1024), 'ascii') == '> OK helo test\r\n'

            # Send single TM - 2. Set_Meta
            client_tc('127.0.0.1', 8080,
                      "tc_meta test_provider_test_param_1\r\n")
            time.sleep(0.1)
            assert str(
                sock.recv(1024), 'ascii'
            ) == '> OK test_provider_test_param_1;2;custom command  set 1\r\n'

            client_tc('127.0.0.1', 8080,
                      "tm_meta test_provider_test_param_1\r\n")
            time.sleep(0.1)
            assert str(
                sock.recv(1024), 'ascii'
            ) == '> ERROR test_provider_test_param_1 Not recognized command\r\n'

            # Send single TM - 3. Get_Meta
            client_tc('127.0.0.1', 8080,
                      "tm_meta test_provider_test_param_2\r\n")
            time.sleep(0.1)
            assert str(
                sock.recv(1024), 'ascii'
            ) == '> OK test_provider_test_param_2;str;str;custom command  get 2;7;4\r\n'

            client_tc('127.0.0.1', 8080,
                      "tc_meta test_provider_test_param_2\r\n")
            time.sleep(0.1)
            assert str(
                sock.recv(1024), 'ascii'
            ) == '> ERROR test_provider_test_param_2 Not recognized command\r\n'

            # Send multiple TM
            client_tc('127.0.0.1', 8080, "helo test_3\r\n")
            time.sleep(0.1)
            client_tc('127.0.0.1', 8080, "helo test_4\r\n")
            time.sleep(0.1)

            assert str(sock.recv(1024),
                       'ascii') == '> OK helo test_3\r\n> OK helo test_4\r\n'

        # Close open threads
        server._close()
