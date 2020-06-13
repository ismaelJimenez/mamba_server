import pytest
import time
import socket

from mamba.core.context import Context
from mamba.core.testing.utils import CallbackTestClass
from mamba.component.protocol_translator import HvsProtocolTranslator
from mamba.component.mamba_tmtc import TcpSingleSocketServer
from mamba.core.msg import Raw, ServiceResponse, ServiceRequest, ParameterType


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
        server.initialize()
        controller.initialize()

        # Subscribe to the 'tc' that shall be published
        self.context.rx['tc'].subscribe(dummy_test_class.test_func_1)

        # Send single msg TC - 1. Helo
        client_tc('127.0.0.1', 8080, "helo test\r\n")
        time.sleep(0.1)

        assert dummy_test_class.func_1_times_called == 1
        assert isinstance(dummy_test_class.func_1_last_value, ServiceRequest)
        assert dummy_test_class.func_1_last_value.id == 'test'
        assert dummy_test_class.func_1_last_value.type == ParameterType.helo
        assert dummy_test_class.func_1_last_value.args == []

        # Send single msg TC - 2. Tc_Meta
        client_tc('127.0.0.1', 8080, "tc_meta test\r\n")
        time.sleep(0.1)

        assert dummy_test_class.func_1_times_called == 2
        assert isinstance(dummy_test_class.func_1_last_value, ServiceRequest)
        assert dummy_test_class.func_1_last_value.id == 'test'
        assert dummy_test_class.func_1_last_value.type == ParameterType.set_meta
        assert dummy_test_class.func_1_last_value.args == []

        # Send single msg TC - 3. Tm_Meta
        client_tc('127.0.0.1', 8080, "tm_meta test\r\n")
        time.sleep(0.1)

        assert dummy_test_class.func_1_times_called == 3
        assert isinstance(dummy_test_class.func_1_last_value, ServiceRequest)
        assert dummy_test_class.func_1_last_value.id == 'test'
        assert dummy_test_class.func_1_last_value.type == ParameterType.get_meta
        assert dummy_test_class.func_1_last_value.args == []

        # Send single msg TC - 4. Tc
        client_tc('127.0.0.1', 8080, 'tc test "arg_1"\r\n')
        time.sleep(0.1)

        assert dummy_test_class.func_1_times_called == 4
        assert isinstance(dummy_test_class.func_1_last_value, ServiceRequest)
        assert dummy_test_class.func_1_last_value.id == 'test'
        assert dummy_test_class.func_1_last_value.type == ParameterType.set
        assert dummy_test_class.func_1_last_value.args == ['arg_1']

        client_tc('127.0.0.1', 8080, 'tc test "arg_1" "arg_2"\r\n')
        time.sleep(0.1)

        assert dummy_test_class.func_1_times_called == 5
        assert isinstance(dummy_test_class.func_1_last_value, ServiceRequest)
        assert dummy_test_class.func_1_last_value.id == 'test'
        assert dummy_test_class.func_1_last_value.type == ParameterType.set
        assert dummy_test_class.func_1_last_value.args == ['arg_1', 'arg_2']

        client_tc('127.0.0.1', 8080, 'tc test 2.3 arg_2\r\n')
        time.sleep(0.1)

        assert dummy_test_class.func_1_times_called == 6
        assert isinstance(dummy_test_class.func_1_last_value, ServiceRequest)
        assert dummy_test_class.func_1_last_value.id == 'test'
        assert dummy_test_class.func_1_last_value.type == ParameterType.set
        assert dummy_test_class.func_1_last_value.args == ['2.3', 'arg_2']

        # Send single msg TC - 5. Tm
        client_tc('127.0.0.1', 8080, 'tm test \r\n')
        time.sleep(0.1)

        assert dummy_test_class.func_1_times_called == 7
        assert isinstance(dummy_test_class.func_1_last_value, ServiceRequest)
        assert dummy_test_class.func_1_last_value.id == 'test'
        assert dummy_test_class.func_1_last_value.type == ParameterType.get
        assert dummy_test_class.func_1_last_value.args == []

        client_tc('127.0.0.1', 8080, 'tm test_2\r\n')
        time.sleep(0.1)

        assert dummy_test_class.func_1_times_called == 8
        assert isinstance(dummy_test_class.func_1_last_value, ServiceRequest)
        assert dummy_test_class.func_1_last_value.id == 'test_2'
        assert dummy_test_class.func_1_last_value.type == ParameterType.get
        assert dummy_test_class.func_1_last_value.args == []

        # Send multiple msg TC
        client_tc('127.0.0.1', 8080, 'helo test_2\r\nhelo test_3\r\n')
        time.sleep(0.1)

        assert dummy_test_class.func_1_times_called == 10
        assert isinstance(dummy_test_class.func_1_last_value, ServiceRequest)
        assert dummy_test_class.func_1_last_value.id == 'test_3'
        assert dummy_test_class.func_1_last_value.type == ParameterType.helo
        assert dummy_test_class.func_1_last_value.args == []

        # Close open threads
        server._close()
