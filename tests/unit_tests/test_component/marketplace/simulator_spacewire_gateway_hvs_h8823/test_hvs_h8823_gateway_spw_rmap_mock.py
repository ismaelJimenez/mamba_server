import socket
import time
import struct

from mamba.core.context import Context
from mamba.marketplace.components.simulator.spacewire_gateway_hvs_h8823_rmap_sim import H8823GatewaySpwRmapMock
from mamba.core.rmap_utils.rmap_common import RMAP, rmap_bytes_to_dict


class TestClass:
    def test_simple_tmtc(self):
        self.mock = H8823GatewaySpwRmapMock(
            Context(), local_config={'instrument': {
                'port': 34576
            }})
        self.mock.initialize()

        rmap = RMAP({
            'target_logical_address': 0x32,
            'key': 0x20,
            'initiator_logical_address': 0x20
        })

        # Create a socket (SOCK_STREAM means a TCP socket)
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            # Connect to server and send data
            sock.connect(("localhost", 34576))

            # 1 - RMAP read before memory initialization
            cmd = rmap.get_rmap_cmd(write=0,
                                    verify=0,
                                    reply=1,
                                    inc=1,
                                    address=0,
                                    size=4,
                                    data_hex_str='',
                                    extended_addr=0)

            sock.sendall(struct.pack("I", len(cmd)))
            sock.sendall(cmd)
            time.sleep(.1)

            assert self.mock._rmap_memory[
                'last_msg_bytes'] == b'2\x01L  \x00\x01\x00\x00\x00\x00\x00\x00\x00\x04b'
            assert self.mock._rmap_memory['last_msg'] == {
                'address': 0,
                'cmd_incr': 1,
                'cmd_reply': 1,
                'cmd_verify': 0,
                'cmd_write': 0,
                'data_length': 4,
                'extended_addr': 0,
                'header_crc': b'b',
                'header_crc_valid': True,
                'initiator_logical_address': 32,
                'key': 32,
                'packet_type': 1,
                'protocol_identifier': 1,
                'target_logical_address': 50,
                'transaction_id': 1
            }

            assert self.mock._rmap_memory['memory_table'] == {}

            # Receive data from the server
            recv_header = sock.recv(12)
            recv_size = int.from_bytes(recv_header[-3:], 'big')
            received = sock.recv(recv_size)

            assert rmap_bytes_to_dict(received) == {
                'cmd_incr': 1,
                'cmd_reply': 1,
                'cmd_verify': 0,
                'cmd_write': 0,
                'data': b'\x00\x00\x00\x00',
                'data_crc': b'\x00',
                'data_crc_valid': True,
                'data_length': 4,
                'header_crc': b'\xab',
                'header_crc_valid': True,
                'initiator_logical_address': 32,
                'packet_type': 0,
                'protocol_identifier': 1,
                'reserved': 0,
                'status': 0,
                'target_logical_address': 50,
                'transaction_id': 1
            }

            # 2 - RMAP write without reply
            cmd = rmap.get_rmap_cmd(write=1,
                                    verify=1,
                                    reply=0,
                                    inc=1,
                                    address=0,
                                    size=0,
                                    data_hex_str='AB',
                                    extended_addr=0)

            sock.sendall(struct.pack("I", len(cmd)))
            sock.sendall(cmd)
            time.sleep(.1)

            assert self.mock._rmap_memory[
                'last_msg_bytes'] == b'2\x01t  \x00\x02\x00\x00\x00\x00\x00\x00\x00\x019\xab\xa4'
            assert self.mock._rmap_memory['last_msg'] == {
                'address': 0,
                'cmd_incr': 1,
                'cmd_reply': 0,
                'cmd_verify': 1,
                'cmd_write': 1,
                'data': b'\xab',
                'data_crc': b'\xa4',
                'data_crc_valid': True,
                'data_length': 1,
                'data_length_valid': True,
                'extended_addr': 0,
                'header_crc': b'9',
                'header_crc_valid': True,
                'initiator_logical_address': 32,
                'key': 32,
                'packet_type': 1,
                'protocol_identifier': 1,
                'target_logical_address': 50,
                'transaction_id': 2
            }

            assert self.mock._rmap_memory['memory_table'] == {0: b'\xab'}

            # 3 - RMAP read single address after modification
            cmd = rmap.get_rmap_cmd(write=0,
                                    verify=0,
                                    reply=1,
                                    inc=0,
                                    address=0,
                                    size=4,
                                    data_hex_str='',
                                    extended_addr=0)

            sock.sendall(struct.pack("I", len(cmd)))
            sock.sendall(cmd)
            time.sleep(.1)

            assert self.mock._rmap_memory[
                'last_msg_bytes'] == b'2\x01H  \x00\x03\x00\x00\x00\x00\x00\x00\x00\x04E'
            assert self.mock._rmap_memory['last_msg'] == {
                'address': 0,
                'cmd_incr': 0,
                'cmd_reply': 1,
                'cmd_verify': 0,
                'cmd_write': 0,
                'data_length': 4,
                'extended_addr': 0,
                'header_crc': b'E',
                'header_crc_valid': True,
                'initiator_logical_address': 32,
                'key': 32,
                'packet_type': 1,
                'protocol_identifier': 1,
                'target_logical_address': 50,
                'transaction_id': 3
            }

            assert self.mock._rmap_memory['memory_table'] == {0: b'\xab'}

            # Receive reply from the server
            recv_header = sock.recv(12)
            recv_size = int.from_bytes(recv_header[-3:], 'big')
            received = sock.recv(recv_size)

            assert rmap_bytes_to_dict(received) == {
                'cmd_incr': 0,
                'cmd_reply': 1,
                'cmd_verify': 0,
                'cmd_write': 0,
                'data': b'\x00\x00\x00\xab',
                'data_crc': b'\xa4',
                'data_crc_valid': True,
                'data_length': 4,
                'header_crc': b'\x08',
                'header_crc_valid': True,
                'initiator_logical_address': 32,
                'packet_type': 0,
                'protocol_identifier': 1,
                'reserved': 0,
                'status': 0,
                'target_logical_address': 50,
                'transaction_id': 3
            }

            # 4 - RMAP write with reply
            cmd = rmap.get_rmap_cmd(write=1,
                                    verify=1,
                                    reply=1,
                                    inc=1,
                                    address=20,
                                    size=0,
                                    data_hex_str='89ABCDEF',
                                    extended_addr=0)

            sock.sendall(struct.pack("I", len(cmd)))
            sock.sendall(cmd)
            time.sleep(.1)

            assert self.mock._rmap_memory[
                'last_msg_bytes'] == b'2\x01|  \x00\x04\x00\x00\x00\x00\x14\x00\x00\x04\xc7\x89\xab\xcd\xef('
            assert self.mock._rmap_memory['last_msg'] == {
                'address': 20,
                'cmd_incr': 1,
                'cmd_reply': 1,
                'cmd_verify': 1,
                'cmd_write': 1,
                'data': b'\x89\xab\xcd\xef',
                'data_crc': b'(',
                'data_crc_valid': True,
                'data_length': 4,
                'data_length_valid': True,
                'extended_addr': 0,
                'header_crc': b'\xc7',
                'header_crc_valid': True,
                'initiator_logical_address': 32,
                'key': 32,
                'packet_type': 1,
                'protocol_identifier': 1,
                'target_logical_address': 50,
                'transaction_id': 4
            }

            assert self.mock._rmap_memory['memory_table'] == {
                0: b'\xab',
                20: b'\x89\xab\xcd\xef'
            }

            # Receive reply from the server
            recv_header = sock.recv(12)
            recv_size = int.from_bytes(recv_header[-3:], 'big')
            received = sock.recv(recv_size)

            assert rmap_bytes_to_dict(received) == {
                'cmd_incr': 1,
                'cmd_reply': 1,
                'cmd_verify': 1,
                'cmd_write': 1,
                'header_crc': b'\xa3',
                'header_crc_valid': True,
                'initiator_logical_address': 32,
                'packet_type': 0,
                'protocol_identifier': 1,
                'status': 0,
                'target_logical_address': 50,
                'transaction_id': 4
            }

            # 5 - RMAP read incr address
            cmd = rmap.get_rmap_cmd(write=0,
                                    verify=0,
                                    reply=1,
                                    inc=1,
                                    address=20,
                                    size=8,
                                    data_hex_str='',
                                    extended_addr=0)

            sock.sendall(struct.pack("I", len(cmd)))
            sock.sendall(cmd)
            time.sleep(.1)

            assert self.mock._rmap_memory[
                'last_msg_bytes'] == b'2\x01L  \x00\x05\x00\x00\x00\x00\x14\x00\x00\x08\xa5'
            assert self.mock._rmap_memory['last_msg'] == {
                'address': 20,
                'cmd_incr': 1,
                'cmd_reply': 1,
                'cmd_verify': 0,
                'cmd_write': 0,
                'data_length': 8,
                'extended_addr': 0,
                'header_crc': b'\xa5',
                'header_crc_valid': True,
                'initiator_logical_address': 32,
                'key': 32,
                'packet_type': 1,
                'protocol_identifier': 1,
                'target_logical_address': 50,
                'transaction_id': 5
            }

            assert self.mock._rmap_memory['memory_table'] == {
                0: b'\xab',
                20: b'\x89\xab\xcd\xef'
            }

            # Receive reply from the server
            recv_header = sock.recv(12)
            recv_size = int.from_bytes(recv_header[-3:], 'big')
            received = sock.recv(recv_size)

            assert rmap_bytes_to_dict(received) == {
                'cmd_incr': 1,
                'cmd_reply': 1,
                'cmd_verify': 0,
                'cmd_write': 0,
                'data': b'\x00\x00\x00\x00\x89\xab\xcd\xef',
                'data_crc': b'(',
                'data_crc_valid': True,
                'data_length': 8,
                'header_crc': b'\x84',
                'header_crc_valid': True,
                'initiator_logical_address': 32,
                'packet_type': 0,
                'protocol_identifier': 1,
                'reserved': 0,
                'status': 0,
                'target_logical_address': 50,
                'transaction_id': 5
            }

            # 6 - RMAP read incr address with delay
            cmd = rmap.get_rmap_cmd(write=0,
                                    verify=0,
                                    reply=1,
                                    inc=1,
                                    address=13,
                                    size=8,
                                    data_hex_str='',
                                    extended_addr=0)

            sock.sendall(struct.pack("I", len(cmd)))
            sock.sendall(cmd)
            time.sleep(.1)

            assert self.mock._rmap_memory[
                'last_msg_bytes'] == b'2\x01L  \x00\x06\x00\x00\x00\x00\r\x00\x00\x08\xb6'
            assert self.mock._rmap_memory['last_msg'] == {
                'address': 13,
                'cmd_incr': 1,
                'cmd_reply': 1,
                'cmd_verify': 0,
                'cmd_write': 0,
                'data_length': 8,
                'extended_addr': 0,
                'header_crc': b'\xb6',
                'header_crc_valid': True,
                'initiator_logical_address': 32,
                'key': 32,
                'packet_type': 1,
                'protocol_identifier': 1,
                'target_logical_address': 50,
                'transaction_id': 6
            }

            assert self.mock._rmap_memory['memory_table'] == {
                0: b'\xab',
                20: b'\x89\xab\xcd\xef'
            }

            # Receive reply from the server
            recv_header = sock.recv(12)
            recv_size = int.from_bytes(recv_header[-3:], 'big')
            received_1 = sock.recv(recv_size)

            assert received_1 == b' \x01\x0c\x002'

            received_2 = sock.recv(recv_size - len(received_1))

            assert received_2 == b'\x00\x06\x00\x00\x00\x08~\x00\x00\x00\x00\x00\x00\x00\x00\x00'

            received = received_1 + received_2

            assert rmap_bytes_to_dict(received) == {
                'cmd_incr': 1,
                'cmd_reply': 1,
                'cmd_verify': 0,
                'cmd_write': 0,
                'data': b'\x00\x00\x00\x00\x00\x00\x00\x00',
                'data_crc': b'\x00',
                'data_crc_valid': True,
                'data_length': 8,
                'header_crc': b'~',
                'header_crc_valid': True,
                'initiator_logical_address': 32,
                'packet_type': 0,
                'protocol_identifier': 1,
                'reserved': 0,
                'status': 0,
                'target_logical_address': 50,
                'transaction_id': 6
            }

        self.mock._close()

    def test_error_handling(self):
        self.mock = H8823GatewaySpwRmapMock(
            Context(), local_config={'instrument': {
                'port': 34577
            }})
        self.mock.initialize()

        rmap = RMAP({
            'target_logical_address': 0x32,
            'key': 0x20,
            'initiator_logical_address': 0x20
        })

        # Create a socket (SOCK_STREAM means a TCP socket)
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            # Connect to server and send data
            sock.connect(("localhost", 34577))

            # 1- Force read failed status
            cmd = rmap.get_rmap_cmd(write=0,
                                    verify=0,
                                    reply=1,
                                    inc=1,
                                    address=11,
                                    size=4,
                                    data_hex_str='',
                                    extended_addr=0)

            sock.sendall(struct.pack("I", len(cmd)))
            sock.sendall(cmd)
            time.sleep(.1)

            # Receive reply from the server
            recv_header = sock.recv(12)
            recv_size = int.from_bytes(recv_header[-3:], 'big')
            received = sock.recv(recv_size)

            assert rmap_bytes_to_dict(received) == {
                'cmd_incr': 1,
                'cmd_reply': 1,
                'cmd_verify': 0,
                'cmd_write': 0,
                'data': b'\x00\x00\x00\x00',
                'data_crc': b'\x00',
                'data_crc_valid': True,
                'data_length': 4,
                'header_crc': b'V',
                'header_crc_valid': True,
                'initiator_logical_address': 32,
                'packet_type': 0,
                'protocol_identifier': 1,
                'reserved': 0,
                'status': 1,
                'target_logical_address': 50,
                'transaction_id': 1
            }

            # 2- Force write failed status
            cmd = rmap.get_rmap_cmd(write=1,
                                    verify=1,
                                    reply=1,
                                    inc=1,
                                    address=11,
                                    size=0,
                                    data_hex_str='89ABCDEF',
                                    extended_addr=0)

            sock.sendall(struct.pack("I", len(cmd)))
            sock.sendall(cmd)
            time.sleep(.1)

            # Receive reply from the server
            recv_header = sock.recv(12)
            recv_size = int.from_bytes(recv_header[-3:], 'big')
            received = sock.recv(recv_size)

            assert rmap_bytes_to_dict(received) == {
                'cmd_incr': 1,
                'cmd_reply': 1,
                'cmd_verify': 1,
                'cmd_write': 1,
                'header_crc': b'\xcb',
                'header_crc_valid': True,
                'initiator_logical_address': 32,
                'packet_type': 0,
                'protocol_identifier': 1,
                'status': 1,
                'target_logical_address': 50,
                'transaction_id': 2
            }

            # 4- Wrong RMAP command format
            cmd = b'\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x01p\xab'
            sock.sendall(struct.pack("I", len(cmd)))
            sock.sendall(cmd)
            time.sleep(1)

            cmd = b'\x00'
            sock.sendall(struct.pack("I", len(cmd)))
            sock.sendall(cmd)
            time.sleep(.1)
