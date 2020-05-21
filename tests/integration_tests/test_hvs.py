import pytest
import os
import socket
import time

from mamba_server.context import Context
from mamba_server.components.drivers.socket_tmtc.hvs_socket_tmtc import Driver as HvsSocketTmtc
from mamba_server.components.drivers.socket_server import Driver as SocketServer
from mamba_server.components.observable_types import Telemetry, Telecommand


def client_tc(ip, port, message):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.connect((ip, port))
        sock.sendall(bytes(message, 'ascii'))


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
                         'mamba_server'))

    def teardown_method(self):
        """ teardown_method called for every method """
        del self.context

    def test_component_tc_socket_hvs_tmtc(self):
        """ Test component external interface """
        dummy_test_class = DummyTestClass()
        server = SocketServer(self.context)
        controller = HvsSocketTmtc(self.context)
        server.initialize()
        controller.initialize()

        # Subscribe to the 'tc' that shall be published
        self.context.rx['tc'].subscribe(dummy_test_class.test_function)

        # Send single raw TC - 1. Helo
        client_tc('127.0.0.1', 8080, "helo test\r\n")
        time.sleep(0.1)

        assert dummy_test_class.times_called == 1
        assert isinstance(dummy_test_class.last_value, Telecommand)
        assert dummy_test_class.last_value.id == 'test'
        assert dummy_test_class.last_value.type == 'helo'
        assert dummy_test_class.last_value.args == []

        # Send single raw TC - 2. Tc_Meta
        client_tc('127.0.0.1', 8080, "tc_meta test\r\n")
        time.sleep(0.1)

        assert dummy_test_class.times_called == 2
        assert isinstance(dummy_test_class.last_value, Telecommand)
        assert dummy_test_class.last_value.id == 'test'
        assert dummy_test_class.last_value.type == 'tc_meta'
        assert dummy_test_class.last_value.args == []

        # Send single raw TC - 3. Tm_Meta
        client_tc('127.0.0.1', 8080, "tm_meta test\r\n")
        time.sleep(0.1)

        assert dummy_test_class.times_called == 3
        assert isinstance(dummy_test_class.last_value, Telecommand)
        assert dummy_test_class.last_value.id == 'test'
        assert dummy_test_class.last_value.type == 'tm_meta'
        assert dummy_test_class.last_value.args == []

        # Send single raw TC - 4. Tc
        client_tc('127.0.0.1', 8080, 'tc test "arg_1"\r\n')
        time.sleep(0.1)

        assert dummy_test_class.times_called == 4
        assert isinstance(dummy_test_class.last_value, Telecommand)
        assert dummy_test_class.last_value.id == 'test'
        assert dummy_test_class.last_value.type == 'tc'
        assert dummy_test_class.last_value.args == ['arg_1']

        client_tc('127.0.0.1', 8080, 'tc test "arg_1" "arg_2"\r\n')
        time.sleep(0.1)

        assert dummy_test_class.times_called == 5
        assert isinstance(dummy_test_class.last_value, Telecommand)
        assert dummy_test_class.last_value.id == 'test'
        assert dummy_test_class.last_value.type == 'tc'
        assert dummy_test_class.last_value.args == ['arg_1', 'arg_2']

        client_tc('127.0.0.1', 8080, 'tc test 2.3 arg_2\r\n')
        time.sleep(0.1)

        assert dummy_test_class.times_called == 6
        assert isinstance(dummy_test_class.last_value, Telecommand)
        assert dummy_test_class.last_value.id == 'test'
        assert dummy_test_class.last_value.type == 'tc'
        assert dummy_test_class.last_value.args == ['2.3', 'arg_2']

        # Send single raw TC - 5. Tm
        client_tc('127.0.0.1', 8080, 'tm test \r\n')
        time.sleep(0.1)

        assert dummy_test_class.times_called == 7
        assert isinstance(dummy_test_class.last_value, Telecommand)
        assert dummy_test_class.last_value.id == 'test'
        assert dummy_test_class.last_value.type == 'tm'
        assert dummy_test_class.last_value.args == []

        client_tc('127.0.0.1', 8080, 'tm test_2\r\n')
        time.sleep(0.1)

        assert dummy_test_class.times_called == 8
        assert isinstance(dummy_test_class.last_value, Telecommand)
        assert dummy_test_class.last_value.id == 'test_2'
        assert dummy_test_class.last_value.type == 'tm'
        assert dummy_test_class.last_value.args == []

        # Send multiple raw TC
        client_tc('127.0.0.1', 8080, 'helo test_2\r\nhelo test_3\r\n')
        time.sleep(0.1)

        assert dummy_test_class.times_called == 10
        assert isinstance(dummy_test_class.last_value, Telecommand)
        assert dummy_test_class.last_value.id == 'test_3'
        assert dummy_test_class.last_value.type == 'helo'
        assert dummy_test_class.last_value.args == []

        # Send unexisting TC type
        client_tc('127.0.0.1', 8080, 'wrong test\r\n')
        time.sleep(0.1)

        assert dummy_test_class.times_called == 11
        assert isinstance(dummy_test_class.last_value, Telecommand)
        assert dummy_test_class.last_value.id == 'test'
        assert dummy_test_class.last_value.type == 'wrong'
        assert dummy_test_class.last_value.args == []

        # Close open threads
        server._close()

    def test_component_observer_tm(self):
        """ Test component external interface """
        server = SocketServer(self.context)
        controller = HvsSocketTmtc(self.context)
        server.initialize()
        controller.initialize()

        # Establish socket connection
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect(('127.0.0.1', 8080))
        time.sleep(.1)

        # Send single TM - 1. Helo
        self.context.rx['tm'].on_next(Telemetry(tm_id='test', tm_type='helo'))
        assert str(sock.recv(1024), 'ascii') == '> OK helo test\r\n'

        # Send single TM - 2. Tc_Meta
        self.context.rx['tm'].on_next(
            Telemetry(tm_id='test',
                      tm_type='tc_meta',
                      value={
                          'num_params': 1,
                          'description': 'description test 1'
                      }))

        assert str(sock.recv(1024),
                   'ascii') == '> OK test;1;description test 1\r\n'

        # Send single TM - 3. Tm_Meta
        self.context.rx['tm'].on_next(
            Telemetry(tm_id='test',
                      tm_type='tm_meta',
                      value={
                          'return_type': 'String',
                          'description': 'description test 1'
                      }))

        assert str(
            sock.recv(1024),
            'ascii') == '> OK test;String;String;description test 1;7;4\r\n'

        # Send single TM - 4. Tc
        self.context.rx['tm'].on_next(Telemetry(tm_id='test', tm_type='tc'))

        assert str(sock.recv(1024), 'ascii') == '> OK test\r\n'

        # Send single TM - 5. Tm
        self.context.rx['tm'].on_next(
            Telemetry(tm_id='test', tm_type='tm', value=1))

        data = str(sock.recv(1024), 'ascii')
        assert '> OK ' in data
        assert ';1;1;0;1\r\n' in data

        # Send single TM - 6. Error
        self.context.rx['tm'].on_next(
            Telemetry(tm_id='test', tm_type='error', value='error msg'))

        assert str(sock.recv(1024), 'ascii') == '> ERROR test error msg\r\n'

        # Send multiple TM
        self.context.rx['tm'].on_next(Telemetry(tm_id='test_3',
                                                tm_type='helo'))
        self.context.rx['tm'].on_next(Telemetry(tm_id='test_4',
                                                tm_type='helo'))

        assert str(sock.recv(1024),
                   'ascii') == '> OK helo test_3\r\n> OK helo test_4\r\n'

        # Close open threads
        server._close()
