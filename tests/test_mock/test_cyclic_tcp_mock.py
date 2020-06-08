import socket
import time

from mamba.core.context import Context
from mamba.mock.tcp.cyclic_tcp_mock import CyclicTcpMock


class TestClass:
    def test_cyclic_tmtc(self):
        self.mock = CyclicTcpMock(Context())
        self.mock.initialize()

        # Create a socket (SOCK_STREAM means a TCP socket)
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            # Connect to server and send data
            sock.connect(("localhost", 8082))

            time.sleep(1)

            # Receive data from the server and shut down
            received = str(sock.recv(1024), "utf-8")

            assert received == 'telemetry_1 1\ntelemetry_2 2\ntelemetry_3 3\n'

            time.sleep(2)

            # Receive data from the server and shut down
            received = str(sock.recv(1024), "utf-8")

            assert received == 'telemetry_1 1\ntelemetry_2 2\ntelemetry_3 3\n'

            time.sleep(4)

            # Receive data from the server and shut down
            received = str(sock.recv(1024), "utf-8")

            assert received == 'telemetry_1 1\ntelemetry_2 2\ntelemetry_3 3\ntelemetry_1 1\ntelemetry_2 2\n' \
                               'telemetry_3 3\n'

            # Create a socket (SOCK_STREAM means a TCP socket)
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock_tc:
                # Connect to server and send data
                sock_tc.connect(("localhost", 8081))

                sock_tc.sendall(bytes('telemetry_1 5\r\n', "utf-8"))

                time.sleep(2)

                # Receive data from the server and shut down
                received = str(sock.recv(1024), "utf-8")

                assert received == 'telemetry_1 5\ntelemetry_2 2\ntelemetry_3 3\n'

                sock_tc.sendall(
                    bytes('telemetry_2 6\r\ntelemetry_3 7\r\n', "utf-8"))

                time.sleep(2)

                # Receive data from the server and shut down
                received = str(sock.recv(1024), "utf-8")

                assert received == 'telemetry_1 5\ntelemetry_2 6\ntelemetry_3 7\n'

        self.mock._close()

    def test_error_handling(self):
        self.mock = CyclicTcpMock(
            Context(),
            local_config={'instrument': {
                'port': {
                    'tc': 8084,
                    'tm': 8083
                }
            }})

        self.mock.initialize()
        # Create a socket (SOCK_STREAM means a TCP socket)
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            # Connect to server and send data
            sock.connect(("localhost", 8083))

            time.sleep(1)

            # Receive data from the server and shut down
            received = str(sock.recv(1024), "utf-8")

            assert received == 'telemetry_1 1\ntelemetry_2 2\ntelemetry_3 3\n'

            # Create a socket (SOCK_STREAM means a TCP socket)
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock_tc:
                # Connect to server and send data
                sock_tc.connect(("localhost", 8084))

                sock_tc.sendall(bytes('telemetry_1 5\n',
                                      "utf-8"))  # Command with wrong ending

                time.sleep(2)

                assert received == 'telemetry_1 1\ntelemetry_2 2\ntelemetry_3 3\n'

                sock_tc.sendall(bytes('telemetry_1\r\n',
                                      "utf-8"))  # Command wo param

                time.sleep(2)

                assert received == 'telemetry_1 1\ntelemetry_2 2\ntelemetry_3 3\n'

                sock_tc.sendall(bytes('telemetry_4 4\r\n',
                                      "utf-8"))  # Not existing TM

                time.sleep(2)

                assert received == 'telemetry_1 1\ntelemetry_2 2\ntelemetry_3 3\n'

        self.mock._close()
