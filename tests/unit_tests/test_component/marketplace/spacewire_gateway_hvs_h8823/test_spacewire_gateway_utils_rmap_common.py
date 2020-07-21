import pytest

from mamba.core.exceptions import ComponentConfigException
from mamba.core.rmap_utils.rmap_common import RMAP, rmap_bytes_to_dict
from mamba.core.rmap_utils.rmap_test import generate_write_reply, generate_read_reply


class TestClass:
    def test_rmap_init(self):
        rmap = RMAP({
            'target_logical_address': 0x32,
            'key': 0x20,
            'initiator_logical_address': 0x20
        })

        assert rmap.target_logical_address == 0x32
        assert rmap.protocol_identifier == 1
        assert rmap.key == 0x20
        assert rmap.initiator_logical_address == 0x20
        assert rmap.transaction_id == 1

        rmap = RMAP({'key': 0x20})

        assert rmap.target_logical_address == 0xFE
        assert rmap.protocol_identifier == 1
        assert rmap.key == 0x20
        assert rmap.initiator_logical_address == 0xFE
        assert rmap.transaction_id == 1

        with pytest.raises(ComponentConfigException) as excinfo:
            RMAP({})

        assert "Missing Key in component configuration" in str(excinfo.value)

        with pytest.raises(AttributeError) as excinfo:
            RMAP('wrong')

        assert "'str' object has no attribute 'get'" in str(excinfo.value)

        with pytest.raises(TypeError) as excinfo:
            RMAP()

        assert "missing 1 required positional argument: 'rmap_config'" in str(
            excinfo.value)

    def test_get_rmap_cmd(self):
        rmap = RMAP({
            'target_logical_address': 0x32,
            'key': 0x20,
            'initiator_logical_address': 0x20
        })

        cmd = rmap.get_rmap_cmd(write=1,
                                verify=1,
                                reply=1,
                                inc=1,
                                address=0,
                                size=0,
                                data_hex_str='AB',
                                extended_addr=0)

        assert rmap_bytes_to_dict(cmd) == {
            'target_logical_address': 0x32,
            'protocol_identifier': 1,
            'packet_type': 1,
            'cmd_write': 1,
            'cmd_verify': 1,
            'cmd_reply': 1,
            'cmd_incr': 1,
            'key': 0x20,
            'initiator_logical_address': 0x20,
            'transaction_id': 1,
            'extended_addr': 0,
            'address': 0,
            'data_length': 1,
            'data_length_valid': True,
            'header_crc': b'\xb3',
            'header_crc_valid': True,
            'data': b'\xab',
            'data_crc': b'\xa4',
            'data_crc_valid': True,
        }

        cmd = rmap.get_rmap_cmd(write=1,
                                verify=1,
                                reply=0,
                                inc=1,
                                address=2,
                                size=0,
                                data_hex_str='ABCDEF',
                                extended_addr=0)

        assert rmap_bytes_to_dict(cmd) == {
            'target_logical_address': 0x32,
            'protocol_identifier': 1,
            'packet_type': 1,
            'cmd_write': 1,
            'cmd_verify': 1,
            'cmd_reply': 0,
            'cmd_incr': 1,
            'key': 0x20,
            'initiator_logical_address': 0x20,
            'transaction_id': 2,
            'extended_addr': 0,
            'address': 2,
            'data_length': 3,
            'data_length_valid': True,
            'header_crc': b'\x03',
            'header_crc_valid': True,
            'data': b'\xab\xcd\xef',
            'data_crc': b'*',
            'data_crc_valid': True,
        }

        cmd = rmap.get_rmap_cmd(write=1,
                                verify=1,
                                reply=0,
                                inc=1,
                                address=2,
                                size=1,
                                data_hex_str='ABCDEF',
                                extended_addr=0)

        assert rmap_bytes_to_dict(cmd) == {
            'target_logical_address': 0x32,
            'protocol_identifier': 1,
            'packet_type': 1,
            'cmd_write': 1,
            'cmd_verify': 1,
            'cmd_reply': 0,
            'cmd_incr': 1,
            'key': 0x20,
            'initiator_logical_address': 0x20,
            'transaction_id': 3,
            'extended_addr': 0,
            'address': 2,
            'data_length': 1,
            'data_length_valid': False,
            'header_crc': b'\xcc',
            'header_crc_valid': True,
            'data': b'\xab\xcd\xef',
            'data_crc': b'*',
            'data_crc_valid': True,
        }

        cmd = rmap.get_rmap_cmd(write=0,
                                verify=0,
                                reply=1,
                                inc=1,
                                address=0,
                                size=4,
                                data_hex_str='',
                                extended_addr=0)

        assert rmap_bytes_to_dict(cmd) == {
            'target_logical_address': 0x32,
            'protocol_identifier': 1,
            'packet_type': 1,
            'cmd_write': 0,
            'cmd_verify': 0,
            'cmd_reply': 1,
            'cmd_incr': 1,
            'key': 0x20,
            'initiator_logical_address': 0x20,
            'transaction_id': 4,
            'extended_addr': 0,
            'address': 0,
            'data_length': 4,
            'header_crc': b'\xfe',
            'header_crc_valid': True,
        }

    def test_rmap_parser_write_reply(self):
        rmap = RMAP({
            'target_logical_address': 0x32,
            'key': 0x20,
            'initiator_logical_address': 0x20
        })

        cmd = rmap.get_rmap_cmd(write=1,
                                verify=1,
                                reply=1,
                                inc=1,
                                address=0,
                                size=0,
                                data_hex_str='AB',
                                extended_addr=0)

        write_reply = generate_write_reply(cmd, 0)

        assert rmap_bytes_to_dict(write_reply) == {
            'initiator_logical_address': 0x20,
            'protocol_identifier': 1,
            'packet_type': 0,
            'cmd_write': 1,
            'cmd_verify': 1,
            'cmd_reply': 1,
            'cmd_incr': 1,
            'status': 0,
            'target_logical_address': 0x32,
            'transaction_id': 1,
            'header_crc': b'5',
            'header_crc_valid': True
        }

        write_reply = generate_write_reply(cmd, 1)

        assert rmap_bytes_to_dict(write_reply) == {
            'initiator_logical_address': 0x20,
            'protocol_identifier': 1,
            'packet_type': 0,
            'cmd_write': 1,
            'cmd_verify': 1,
            'cmd_reply': 1,
            'cmd_incr': 1,
            'status': 1,
            'target_logical_address': 0x32,
            'transaction_id': 1,
            'header_crc': b'\xb9',
            'header_crc_valid': True
        }

    def test_rmap_parser_read_reply(self):
        rmap = RMAP({
            'target_logical_address': 0x32,
            'key': 0x20,
            'initiator_logical_address': 0x20
        })

        cmd = rmap.get_rmap_cmd(write=0,
                                verify=0,
                                reply=1,
                                inc=1,
                                address=0,
                                size=4,
                                data_hex_str='',
                                extended_addr=0)

        read_reply = generate_read_reply(cmd, 0, '00000004')

        assert rmap_bytes_to_dict(read_reply) == {
            'initiator_logical_address': 0x20,
            'protocol_identifier': 1,
            'packet_type': 0,
            'cmd_write': 0,
            'cmd_verify': 0,
            'cmd_reply': 1,
            'cmd_incr': 1,
            'status': 0,
            'target_logical_address': 0x32,
            'transaction_id': 1,
            'reserved': 0,
            'data_length': 4,
            'header_crc': b'\xab',
            'header_crc_valid': True,
            'data': b'\x00\x00\x00\x04',
            'data_crc': b'\x07',
            'data_crc_valid': True,
        }

        read_reply = generate_read_reply(cmd, 1, '12345678')

        assert rmap_bytes_to_dict(read_reply) == {
            'initiator_logical_address': 0x20,
            'protocol_identifier': 1,
            'packet_type': 0,
            'cmd_write': 0,
            'cmd_verify': 0,
            'cmd_reply': 1,
            'cmd_incr': 1,
            'status': 1,
            'target_logical_address': 0x32,
            'transaction_id': 1,
            'reserved': 0,
            'data_length': 4,
            'header_crc': b'V',
            'header_crc_valid': True,
            'data': b'\x124Vx',
            'data_crc': b'\xfd',
            'data_crc_valid': True,
        }
