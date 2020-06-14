import pytest
import time
import socket
import os

from mamba.core.context import Context
from mamba.core.testing.utils import CallbackTestClass
from mamba.component.instrument_driver.signal_generator import SignalGeneratorSmb100b
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
        self.context.set(
            'mamba_dir',
            os.path.join(os.path.dirname(__file__), '..', '..',
                         'mamba'))

    def teardown_method(self):
        """ teardown_method called for every method """
        del self.context

    def test_integration_tmtc(self):
        """ Test component external interface """
        server = TcpSingleSocketServer(self.context)
        controller = HvsProtocolTranslator(self.context)
        protocol = MambaProtocolController(self.context)
        io_controller = SignalGeneratorSmb100b(self.context)
        server.initialize()
        controller.initialize()
        protocol.initialize()
        io_controller.initialize()

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
                      "tc_meta r&s_smb100b_rf_signal_generator_clear\r\n")
            time.sleep(0.1)
            assert str(
                sock.recv(1024), 'ascii'
            ) == '> OK r&s_smb100b_rf_signal_generator_clear;0;Clear status\r\n'

            client_tc('127.0.0.1', 8080,
                      "tc_meta r&s_smb100b_rf_signal_generator_idn\r\n")
            time.sleep(0.1)
            assert str(
                sock.recv(1024), 'ascii'
            ) == '> ERROR r&s_smb100b_rf_signal_generator_idn Not recognized command\r\n'

            client_tc('127.0.0.1', 8080,
                      "tm_meta r&s_smb100b_rf_signal_generator_idn\r\n")
            time.sleep(0.1)
            assert str(
                sock.recv(1024), 'ascii'
            ) == '> OK r&s_smb100b_rf_signal_generator_idn;str;str;Instrument identification;7;4\r\n'

            client_tc('127.0.0.1', 8080,
                      "tm_meta r&s_smb100b_rf_signal_generator_clear\r\n")
            time.sleep(0.1)
            assert str(
                sock.recv(1024), 'ascii'
            ) == '> ERROR r&s_smb100b_rf_signal_generator_clear Not recognized command\r\n'

            # Parameter Get/Set
            client_tc('127.0.0.1', 8080,
                      "tc r&s_smb100b_rf_signal_generator_clear\r\n")
            time.sleep(0.1)
            assert str(
                sock.recv(1024), 'ascii'
            ) == '> ERROR clear Not possible to perform command before connection is established\r\n'

            client_tc('127.0.0.1', 8080,
                      "tm r&s_smb100b_rf_signal_generator_connected\r\n")
            time.sleep(0.1)
            recv = str(sock.recv(1024), 'ascii')
            assert '> OK connected;' in recv
            assert ';0;0;0;1\r\n' in recv

            client_tc('127.0.0.1', 8080,
                      "tc r&s_smb100b_rf_signal_generator_connect 1\r\n")
            time.sleep(0.1)
            assert str(
                sock.recv(1024), 'ascii'
            ) == '> OK connect\r\n'

            client_tc('127.0.0.1', 8080,
                      "tm r&s_smb100b_rf_signal_generator_connected\r\n")
            time.sleep(0.1)
            recv = str(sock.recv(1024), 'ascii')
            assert '> OK connected;' in recv
            assert ';1;1;0;1\r\n' in recv

            # Send multiple TM
            client_tc('127.0.0.1', 8080, "helo test_3\r\n")
            time.sleep(0.1)
            client_tc('127.0.0.1', 8080, "helo test_4\r\n")
            time.sleep(0.1)

            assert str(sock.recv(1024),
                       'ascii') == '> OK helo test_3\r\n> OK helo test_4\r\n'

        # Close open threads
        server._close()
