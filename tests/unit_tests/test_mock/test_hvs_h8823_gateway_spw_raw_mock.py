import socket
import time

from mamba.core.context import Context
from mamba.mock.tcp.spacewire_gateway.hvs_h8823_gateway_spw_raw_mock import H8823GatewaySpwRawMock


class TestClass:
    def test_simple_tmtc(self):
        self.mock = H8823GatewaySpwRawMock(
            Context(), local_config={'instrument': {
                'port': 34571
            }})
        self.mock.initialize()

        # Create a socket (SOCK_STREAM means a TCP socket)
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            # Connect to server and send data
            sock.connect(("localhost", 34571))

            sock.sendall(bytes('0123456789ABCDEF\n', "utf-8"))
            time.sleep(.1)

            sock.sendall(bytes('1023456789ABCDEF\n', "utf-8"))
            time.sleep(.1)

            # Receive data from the server and shut down
            received = str(sock.recv(1024), "utf-8")
            assert received == '1023456789ABCDEF\n'

        self.mock._close()
