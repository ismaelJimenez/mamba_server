import socket
import time

from mamba.core.context import Context
from mamba.mock.tcp.two_ports_tcp_mock import TwoPortsTcpMock


class TestClass:
    def test_tmtc(self):
        self.mock = TwoPortsTcpMock(Context())
        self.mock.initialize()

        # Create a socket (SOCK_STREAM means a TCP socket)
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock_tc:
            # Connect to server and send data
            sock_tc.connect(("localhost", 8086))

            # Create a socket (SOCK_STREAM means a TCP socket)
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock_tm:
                # Connect to server and send data
                sock_tm.connect(("localhost", 8087))

                sock_tc.sendall(
                    bytes('PARAMETER_1?\r\nPARAMETER_2?\r\nPARAMETER_3?\r\n',
                          "utf-8"))

                time.sleep(.1)

                # Receive data from the server and shut down
                received = str(sock_tm.recv(1024), "utf-8")
                assert received == '1\n2\n3\n'

                sock_tc.sendall(bytes('*IDN?\r\n', "utf-8"))

                time.sleep(.1)

                # Receive data from the server and shut down
                received = str(sock_tm.recv(1024), "utf-8")
                assert received == 'Mamba Framework,Two Port TCP Mock,1.0\n'

                sock_tc.sendall(bytes('*CLS\r\n', "utf-8"))

                sock_tc.sendall(
                    bytes(
                        'PARAMETER_1 4\r\nPARAMETER_2 5\r\nPARAMETER_3 6\r\n',
                        "utf-8"))
                sock_tc.sendall(
                    bytes('PARAMETER_1?\r\nPARAMETER_2?\r\nPARAMETER_3?\r\n',
                          "utf-8"))

                time.sleep(.1)

                # Receive data from the server and shut down
                received = str(sock_tm.recv(1024), "utf-8")

                assert received == '4\n5\n6\n'

                # Create a socket (SOCK_STREAM means a TCP socket)
                with socket.socket(socket.AF_INET,
                                   socket.SOCK_STREAM) as sock_2_tc:
                    # Connect to server and send data
                    sock_2_tc.connect(("localhost", 8086))

                    sock_2_tc.sendall(
                        bytes(
                            'PARAMETER_1?\r\nPARAMETER_2?\r\nPARAMETER_3?\r\n',
                            "utf-8"))

                    time.sleep(.1)

                    # Receive data from the server and shut down
                    received = str(sock_tm.recv(1024), "utf-8")
                    assert received == '4\n5\n6\n'

        self.mock._close()

    def test_error_handling(self):
        self.mock = TwoPortsTcpMock(
            Context(),
            local_config={'instrument': {
                'port': {
                    'tc': 8088,
                    'tm': 8089
                }
            }})

        self.mock.initialize()

        # Create a socket (SOCK_STREAM means a TCP socket)
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock_tc:
            # Connect to server and send data
            sock_tc.connect(("localhost", 8088))

            # Create a socket (SOCK_STREAM means a TCP socket)
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock_tm:
                # Connect to server and send data
                sock_tm.connect(("localhost", 8089))

                sock_tc.sendall(bytes('SYST:ERR?\r\n', "utf-8"))

                time.sleep(.1)

                # Receive data from the server and shut down
                received = str(sock_tm.recv(1024), "utf-8")
                assert received == '0,_No_Error\n'

                sock_tc.sendall(
                    bytes('PARAMETER_1?\r\nPARAMETER_2?\r\nPARAMETER_3?\r\n',
                          "utf-8"))

                time.sleep(1)

                # Receive data from the server and shut down
                received = str(sock_tm.recv(1024), "utf-8")
                assert received == '1\n2\n3\n'

                # Test wrong message ending
                sock_tc.sendall(bytes('PARAMETER_1 4\n', "utf-8"))

                time.sleep(.1)

                sock_tc.sendall(bytes('PARAMETER_1?\r\n', "utf-8"))

                # Receive data from the server and shut down
                received = str(sock_tm.recv(1024), "utf-8")
                assert received == '1\n'

                # Test wrong number or parameters
                sock_tc.sendall(bytes('PARAMETER_1\n', "utf-8"))

                time.sleep(.1)

                sock_tc.sendall(bytes('PARAMETER_1?\r\n', "utf-8"))

                # Receive data from the server and shut down
                received = str(sock_tm.recv(1024), "utf-8")
                assert received == '1\n'

                # Test wrong number or parameters
                sock_tc.sendall(bytes('PARAMETER_5 1234\r\n', "utf-8"))

                time.sleep(.1)

                sock_tc.sendall(bytes('PARAMETER_5?\r\n', "utf-8"))

                # Receive data from the server and shut down
                received = str(sock_tm.recv(1024), "utf-8")
                assert received == 'KeyError\n'

                sock_tc.sendall(bytes('SYST:ERR?\r\n', "utf-8"))

                time.sleep(.1)

                # Receive data from the server and shut down
                received = str(sock_tm.recv(1024), "utf-8")
                assert received == '1,_Command_Error\n'

                sock_tc.sendall(bytes('SYST:ERR?\r\n', "utf-8"))

                time.sleep(.1)

                # Receive data from the server and shut down
                received = str(sock_tm.recv(1024), "utf-8")
                assert received == '0,_No_Error\n'

        self.mock._close()
