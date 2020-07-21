import socket
import time

from mamba.core.context import Context
from mamba.marketplace.components.simulator.tcp.single_port_tcp_mock import SinglePortTcpMock


class TestClass:
    def test_simple_tmtc(self):
        self.mock = SinglePortTcpMock(
            Context(), local_config={'instrument': {
                'port': 34567
            }})
        self.mock.initialize()

        # Create a socket (SOCK_STREAM means a TCP socket)
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            # Connect to server and send data
            sock.connect(("localhost", 34567))

            sock.sendall(
                bytes('PARAMETER_1?\r\nPARAMETER_2?\r\nPARAMETER_3?\r\n',
                      "utf-8"))

            time.sleep(.1)

            # Receive data from the server and shut down
            received = str(sock.recv(1024), "utf-8")
            assert received == '1\n2\n3\n'

            sock.sendall(bytes('*IDN?\r\n', "utf-8"))

            time.sleep(.1)

            # Receive data from the server and shut down
            received = str(sock.recv(1024), "utf-8")
            assert received == 'Mamba Framework,Single Port TCP Mock,1.0\n'

            sock.sendall(bytes('*CLS\r\n', "utf-8"))

            sock.sendall(
                bytes('PARAMETER_1 4\r\nPARAMETER_2 5\r\nPARAMETER_3 6\r\n',
                      "utf-8"))
            sock.sendall(
                bytes('PARAMETER_1?\r\nPARAMETER_2?\r\nPARAMETER_3?\r\n',
                      "utf-8"))

            time.sleep(.1)

            # Receive data from the server and shut down
            received = str(sock.recv(1024), "utf-8")

            assert received == '4\n5\n6\n'

            # Create a socket (SOCK_STREAM means a TCP socket)
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock_2:
                # Connect to server and send data
                sock_2.connect(("localhost", 34567))

                sock_2.sendall(
                    bytes('PARAMETER_1?\r\nPARAMETER_2?\r\nPARAMETER_3?\r\n',
                          "utf-8"))

                time.sleep(.1)

                # Receive data from the server and shut down
                received = str(sock_2.recv(1024), "utf-8")

                assert received == '4\n5\n6\n'

        self.mock._close()

    def test_error_handling(self):
        self.mock = SinglePortTcpMock(
            Context(), local_config={'instrument': {
                'port': 8100
            }})

        self.mock.initialize()
        # Create a socket (SOCK_STREAM means a TCP socket)
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            # Connect to server and send data
            sock.connect(("localhost", 8100))

            sock.sendall(bytes('SYST:ERR?\r\n', "utf-8"))

            time.sleep(.1)

            # Receive data from the server and shut down
            received = str(sock.recv(1024), "utf-8")
            assert received == '0,_No_Error\n'

            sock.sendall(
                bytes('PARAMETER_1?\r\nPARAMETER_2?\r\nPARAMETER_3?\r\n',
                      "utf-8"))

            time.sleep(.1)

            # Receive data from the server and shut down
            received = str(sock.recv(1024), "utf-8")
            assert received == '1\n2\n3\n'

            # Test wrong message ending
            sock.sendall(bytes('PARAMETER_1 4\n', "utf-8"))

            time.sleep(.1)

            sock.sendall(bytes('PARAMETER_1?\r\n', "utf-8"))

            # Receive data from the server and shut down
            received = str(sock.recv(1024), "utf-8")
            assert received == '1\n'

            # Test wrong number or parameters
            sock.sendall(bytes('PARAMETER_1\n', "utf-8"))

            time.sleep(.1)

            sock.sendall(bytes('PARAMETER_1?\r\n', "utf-8"))

            # Receive data from the server and shut down
            received = str(sock.recv(1024), "utf-8")
            assert received == '1\n'

            # Test wrong number or parameters
            sock.sendall(bytes('PARAMETER_5 1234\r\n', "utf-8"))

            time.sleep(.1)

            sock.sendall(bytes('PARAMETER_5?\r\n', "utf-8"))

            # Receive data from the server and shut down
            received = str(sock.recv(1024), "utf-8")
            assert received == 'KeyError\n'

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
