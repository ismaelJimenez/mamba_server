import socket
import time

from mamba.core.context import Context
from mamba.mock.udp.single_port_udp_mock import SinglePortUdpMock


class TestClass:
    def test_simple_tmtc(self):
        self.mock = SinglePortUdpMock(
            Context(), local_config={'instrument': {
                'port': 34591
            }})
        self.mock.initialize()

        # Create a socket (SOCK_STREAM means a UDP socket)
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            # Connect to server and send data
            sock.sendto(
                bytes('PARAMETER_1?\r\nPARAMETER_2?\r\nPARAMETER_3?\r\n',
                      "utf-8"), ("localhost", 34591))

            time.sleep(.1)

            # Receive data from the server and shut down
            received = str(sock.recv(1024), "utf-8")
            assert received == '1\n'

            received = str(sock.recv(1024), "utf-8")
            assert received == '2\n'

            received = str(sock.recv(1024), "utf-8")
            assert received == '3\n'

            sock.sendto(bytes('*IDN?\r\n', "utf-8"), ("localhost", 34591))

            time.sleep(.1)

            # Receive data from the server and shut down
            received = str(sock.recv(1024), "utf-8")
            assert received == 'Mamba Framework,Single Port UDP Mock,1.0\n'

        self.mock._close()
