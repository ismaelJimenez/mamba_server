import pytest
import os
import socket
import time

from mamba.core.context import Context
from mamba.core.testing.utils import CallbackTestClass
from mamba.component.mamba_tmtc import TcpSingleSocketServer
from mamba.core.msg import Empty, Raw


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

    def test_component_wo_context(self):
        with pytest.raises(TypeError) as excinfo:
            TcpSingleSocketServer()

        assert "missing 1 required positional argument" in str(excinfo.value)

    def test_component_w_empty_context(self):
        component = TcpSingleSocketServer(Context())
        component.initialize()

        # Test default configuration
        assert component._configuration == {
            'host': '0.0.0.0',
            'name': 'socket_server',
            'port': 8080
        }

        assert component._server is not None
        assert component._server_thread is not None

        # Close open threads
        component._close()

    def test_component_quit_observer(self):
        """ Test component quit observer """
        component = TcpSingleSocketServer(self.context, local_config={'port': 8102})
        component.initialize()

        # Test status before close
        assert component._server is not None
        assert component._server_thread is not None

        self.context.rx['quit'].on_next(Empty())

        # Test load screen has been closed
        assert component._server is None

    def test_component_socket_receive(self):
        """ Test component external interface """
        dummy_test_class = CallbackTestClass()
        component = TcpSingleSocketServer(self.context, local_config={'port': 8101})
        component.initialize()

        # Subscribe to the 'raw_tc' that shall be published
        self.context.rx['raw_tc'].subscribe(dummy_test_class.test_func_1)

        client_tc('127.0.0.1', 8101, "Hello World 1\r\n")
        time.sleep(.1)

        assert dummy_test_class.func_1_times_called == 1
        assert isinstance(dummy_test_class.func_1_last_value, Raw)
        assert dummy_test_class.func_1_last_value.msg == "Hello World 1\r\n"

        client_tc('127.0.0.1', 8101, "Hello World 2\r\n")
        time.sleep(.1)

        assert dummy_test_class.func_1_times_called == 2
        assert isinstance(dummy_test_class.func_1_last_value, Raw)
        assert dummy_test_class.func_1_last_value.msg == "Hello World 2\r\n"

        client_tc('127.0.0.1', 8101, "Hello World 3\r\nHello World 4\r\n")
        time.sleep(.1)

        assert dummy_test_class.func_1_times_called == 3
        assert isinstance(dummy_test_class.func_1_last_value, Raw)
        assert dummy_test_class.func_1_last_value.msg == "Hello World 3\r\nHello World 4\r\n"

        # Close open threads
        component._close()

    def test_component_socket_send(self):
        """ Test component external interface """
        component = TcpSingleSocketServer(self.context, local_config={'port': 8100})
        component.initialize()

        # Establish socket connection
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.connect(('127.0.0.1', 8100))

            time.sleep(.1)

            # Send TM
            self.context.rx['raw_tm'].on_next(Raw("Hello World 1\r\n"))
            assert str(sock.recv(1024), 'ascii') == 'Hello World 1\r\n'

            # Send TM
            self.context.rx['raw_tm'].on_next(
                Raw("Hello World 2\r\nHello World 3\r\n"))
            assert str(sock.recv(1024),
                       'ascii') == 'Hello World 2\r\nHello World 3\r\n'

        # Close open threads
        component._close()
