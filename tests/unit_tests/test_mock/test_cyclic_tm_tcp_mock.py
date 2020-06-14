import socket
import time

from mamba.core.context import Context
from mamba.mock.tcp.cyclic_tm_tcp_mock import CyclicTmTcpMock


class TestClass:
    def test_simple_tmtc(self):
        self.mock = CyclicTmTcpMock(
            Context(),
            local_config={'instrument': {
                'port': {
                    'tc': 9200,
                    'tm': 9201
                }
            }})
        self.mock.initialize()

        # Create a socket (SOCK_STREAM means a TCP socket)
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            # Connect to server and send data
            sock.connect(("localhost", 9200))

            # Create a socket (SOCK_STREAM means a TCP socket)
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock_tm:
                # Connect to server and send data
                sock_tm.connect(("localhost", 9201))

                # Test cyclic telemetry reception
                time.sleep(.1)
                # Receive data from the server and shut down
                received = str(sock_tm.recv(1024), "utf-8")

                assert received == 'PARAMETER_1 1\nPARAMETER_2 2\nPARAMETER_3 3\n'

                sock.sendall(bytes('*IDN?\r\n', "utf-8"))

                time.sleep(.1)

                # Receive data from the server and shut down
                received = str(sock.recv(1024), "utf-8")
                assert received == 'Mamba Framework,Cyclic Telemetry TCP Mock,1.0\n'

                sock.sendall(bytes('*CLS\r\n', "utf-8"))

                sock.sendall(
                    bytes(
                        'PARAMETER_1 4\r\nPARAMETER_2 5\r\nPARAMETER_3 6\r\n',
                        "utf-8"))

                # Test cyclic telemetry reception
                time.sleep(5)
                # Receive data from the server and shut down
                received = str(sock_tm.recv(1024), "utf-8")

                assert received == 'PARAMETER_1 4\nPARAMETER_2 5\nPARAMETER_3 6\n'

                # Create a socket (SOCK_STREAM means a TCP socket)
                with socket.socket(socket.AF_INET,
                                   socket.SOCK_STREAM) as sock_2_tm:
                    # Connect to server and send data
                    sock_2_tm.connect(("localhost", 9201))

                    # Test cyclic telemetry reception
                    time.sleep(.1)
                    # Receive data from the server and shut down
                    received = str(sock_2_tm.recv(1024), "utf-8")

                    assert received == 'PARAMETER_1 4\nPARAMETER_2 5\nPARAMETER_3 6\n'

        self.mock._close()

    def test_error_handling(self):
        self.mock = CyclicTmTcpMock(
            Context(),
            local_config={'instrument': {
                'port': {
                    'tc': 9401,
                    'tm': 9402
                }
            }})

        self.mock.initialize()
        # Create a socket (SOCK_STREAM means a TCP socket)
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            # Connect to server and send data
            sock.connect(("localhost", 9401))

            # Create a socket (SOCK_STREAM means a TCP socket)
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock_tm:
                # Connect to server and send data
                sock_tm.connect(("localhost", 9402))

                sock.sendall(bytes('SYST:ERR?\r\n', "utf-8"))

                time.sleep(.1)

                # Receive data from the server and shut down
                received = str(sock.recv(1024), "utf-8")
                assert received == '0,_No_Error\n'

                # Test cyclic telemetry reception
                time.sleep(.1)
                # Receive data from the server and shut down
                received = str(sock_tm.recv(1024), "utf-8")

                assert received == 'PARAMETER_1 1\nPARAMETER_2 2\nPARAMETER_3 3\n'

                # Test wrong message ending
                sock.sendall(bytes('PARAMETER_1 4\n', "utf-8"))

                time.sleep(.1)

                # Test cyclic telemetry reception
                time.sleep(5)
                # Receive data from the server and shut down
                received = str(sock_tm.recv(1024), "utf-8")
                assert received == 'PARAMETER_1 1\nPARAMETER_2 2\nPARAMETER_3 3\n'

                # Test wrong number or parameters
                sock.sendall(bytes('PARAMETER_1\n', "utf-8"))

                # Test cyclic telemetry reception
                time.sleep(5)
                # Receive data from the server and shut down
                received = str(sock_tm.recv(1024), "utf-8")
                assert received == 'PARAMETER_1 1\nPARAMETER_2 2\nPARAMETER_3 3\n'

                # Test wrong number or parameters
                sock.sendall(bytes('PARAMETER_5 1234\r\n', "utf-8"))

                # Test cyclic telemetry reception
                time.sleep(5)
                # Receive data from the server and shut down
                received = str(sock_tm.recv(1024), "utf-8")
                assert received == 'PARAMETER_1 1\nPARAMETER_2 2\nPARAMETER_3 3\n'

                sock.sendall(bytes('SYST:ERR?\r\n', "utf-8"))

                time.sleep(.1)

                # Receive data from the server and shut down
                received = str(sock.recv(1024), "utf-8")
                assert received == '1,_Command_Error\n'

                sock.sendall(bytes('SYST:ERR?\r\n', "utf-8"))

                time.sleep(.1)

                # Receive data from the server and shut down
                received = str(sock.recv(1024), "utf-8")
                assert received == '0,_No_Error\n'

        self.mock._close()
