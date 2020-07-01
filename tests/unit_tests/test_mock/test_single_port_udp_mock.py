import socket
import time

from mamba.core.context import Context
from mamba.mock.udp.single_port_udp_mock import SinglePortUdpMock


def udp_client(ip: str, port: int, message: bytes) -> bytes:
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        sock.sendto(message, (ip, port))
        return sock.recv(1024)


def send_server_msg(ip: str, port: int, cmd_id: int, param_number: int,
                    pathname: str):
    msg = bytes('SOME', 'ascii') + cmd_id.to_bytes(4, 'big') + \
          param_number.to_bytes(4, 'big') + bytes(pathname, 'ascii') + \
          (0).to_bytes(1, 'big') + bytes('EOME', 'ascii')
    return udp_client(ip, port, message=msg)


class TestClass:
    def test_simple_tmtc(self):
        mock = SinglePortUdpMock(Context(),
                                 local_config={'instrument': {
                                     'port': 34571
                                 }})
        mock.initialize()

        reply = send_server_msg(ip='127.0.0.1',
                                port=34571,
                                cmd_id=1,
                                param_number=1,
                                pathname='test.txt')
        assert reply == b'SOME\x00\x00\x01\x01\x00\x00\x00\x00EOME'

        reply = send_server_msg(ip='127.0.0.1',
                                port=34571,
                                cmd_id=4,
                                param_number=10,
                                pathname='test.txt')
        assert reply == b'SOME\x00\x00\x01\x01\x00\x00\x00\x00EOME'

        reply = send_server_msg(ip='127.0.0.1',
                                port=34571,
                                cmd_id=2,
                                param_number=10,
                                pathname='test.txt')
        assert reply == b'SOME\x00\x00\x01\x01\x00\x00\x00\x01EOME'

        mock._close()
