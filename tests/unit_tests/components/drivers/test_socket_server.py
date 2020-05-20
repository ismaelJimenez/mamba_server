import pytest
import os
import socket
import time

from mamba_server.context import Context
from mamba_server.components.drivers.socket_server import Driver
from mamba_server.components.observable_types import Empty, RawTelemetry, RawTelecommand


class DummyTestClass:
    def __init__(self):
        super(DummyTestClass, self).__init__()
        self.times_called = 0
        self.last_value = None

    def test_function(self, rx_on_set=None):
        self.times_called += 1
        self.last_value = rx_on_set


def client_tc(ip, port, message):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.connect((ip, port))
        sock.sendall(bytes(message, 'ascii'))


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
        component = Driver(self.context)
        component.initialize()

        # Test status before close
        assert component._server is not None
        assert component._server_thread is not None

        self.context.rx['quit'].on_next(Empty())

        # Test load screen has been closed
        assert component._server is None

    def test_component_socket_receive(self):
        """ Test component external interface """
        dummy_test_class = DummyTestClass()
        component = Driver(self.context)
        component.initialize()

        # Subscribe to the 'raw_tc' that shall be published
        self.context.rx['raw_tc'].subscribe(dummy_test_class.test_function)

        client_tc('127.0.0.1', 8080, "Hello World 1\r\n")
        time.sleep(.1)

        assert dummy_test_class.times_called == 1
        assert isinstance(dummy_test_class.last_value, RawTelecommand)
        assert dummy_test_class.last_value.raw == "Hello World 1\r\n"

        client_tc('127.0.0.1', 8080, "Hello World 2\r\n")
        time.sleep(.1)

        assert dummy_test_class.times_called == 2
        assert isinstance(dummy_test_class.last_value, RawTelecommand)
        assert dummy_test_class.last_value.raw == "Hello World 2\r\n"

        client_tc('127.0.0.1', 8080, "Hello World 3\r\nHello World 4\r\n")
        time.sleep(.1)

        assert dummy_test_class.times_called == 3
        assert isinstance(dummy_test_class.last_value, RawTelecommand)
        assert dummy_test_class.last_value.raw == "Hello World 3\r\nHello World 4\r\n"

        # Close open threads
        component._close()

    def test_component_socket_send(self):
        """ Test component external interface """
        dummy_test_class = DummyTestClass()
        component = Driver(self.context)
        component.initialize()

        # Establish socket connection
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect(('127.0.0.1', 8080))

        time.sleep(.1)

        # Send TM
        self.context.rx['raw_tm'].on_next(RawTelemetry("Hello World 1\r\n"))
        assert str(sock.recv(1024), 'ascii') == 'Hello World 1\r\n'

        # Send TM
        self.context.rx['raw_tm'].on_next(
            RawTelemetry("Hello World 2\r\nHello World 3\r\n"))
        assert str(sock.recv(1024),
                   'ascii') == 'Hello World 2\r\nHello World 3\r\n'

        # Close open threads
        component._close()
