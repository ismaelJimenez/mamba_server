#############################################################################
##
## Copyright (C) 2020 The Mamba Company.
## Contact: themambacompany@gmail.com
##
## This file is part of Mamba Server.
##
## $MAMBA_BEGIN_LICENSE:LGPL$
## Commercial License Usage
## Licensees holding valid commercial Mamba licenses may use this file in
## accordance with the commercial license agreement provided with the
## Software or, alternatively, in accordance with the terms contained in
## a written agreement between you and The Mamba Company. For licensing terms
## and conditions see LICENSE. For further information contact us at
## themambacompany@gmail.com.
##
## GNU Lesser General Public License Usage
## Alternatively, this file may be used under the terms of the GNU Lesser
## General Public License version 3 as published by the Free Software
## Foundation and appearing in the file LICENSE.LGPL3 included in the
## packaging of this file. Please review the following information to
## ensure the GNU Lesser General Public License version 3 requirements
## will be met: https://www.gnu.org/licenses/lgpl-3.0.html.
##
## GNU General Public License Usage
## Alternatively, this file may be used under the terms of the GNU
## General Public License version 2.0 or (at your option) the GNU General
## Public license version 3 or any later version approved by the KDE Free
## Qt Foundation. The licenses are as published by the Free Software
## Foundation and appearing in the file LICENSE.GPL2 and LICENSE.GPL3
## included in the packaging of this file. Please review the following
## information to ensure the GNU General Public License requirements will
## be met: https://www.gnu.org/licenses/gpl-2.0.html and
## https://www.gnu.org/licenses/gpl-3.0.html.
##
## $MAMBA_END_LICENSE$
##
#############################################################################

import struct

from mamba.core.exceptions import ComponentConfigException
from mamba.marketplace.components.spacewire_gateway.utils.crc_8 \
    import crc_8


def get_rmap_cmd_code(write: bool, verify: bool, reply: bool, inc: bool):
    _packet_type = 0x40  # command (0b01)
    _write = write * 0x20
    _verify = verify * 0x10
    _reply = reply * 0x8
    _inc = inc * 0x4

    return _packet_type | _write | _verify | _reply | _inc


class RMAP:
    def __init__(self, rmap_config: dict) -> None:
        self.target_logical_address = rmap_config.get('target_logical_address',
                                                      0xFE)
        self.protocol_identifier = 1  # RMAP protocol identifier

        key = rmap_config.get('key')

        if isinstance(key, int):
            self.key = rmap_config.get('key')
        else:
            raise ComponentConfigException(
                "Missing Key in component configuration")

        self.initiator_logical_address = rmap_config.get(
            'initiator_logical_address', 0xFE)
        self.transaction_id = 1

    def get_rmap_cmd(self, write: bool, verify: bool, reply: bool, inc: bool,
                     address: int, size: int, data_hex_str: str,
                     extended_addr: int) -> bytes:
        rmap_cmd_code = get_rmap_cmd_code(write, verify, reply, inc)

        if size == 0 and len(data_hex_str) > 0:
            size = int(len(data_hex_str) / 2)

        rmap_header = struct.pack(
            "BBBBBBBBBBBBBBB", self.target_logical_address,
            self.protocol_identifier, rmap_cmd_code, self.key,
            self.initiator_logical_address, self.transaction_id >> 8,
            self.transaction_id & 0xff, extended_addr, (address >> 24) & 0xff,
            (address >> 16) & 0xff, (address >> 8) & 0xff,
            (address >> 0) & 0xff, (size >> 16) & 0xff, (size >> 8) & 0xff,
            (size >> 0) & 0xff)

        msg = rmap_header + crc_8(rmap_header)

        if len(data_hex_str) > 0:
            msg = msg + bytes.fromhex(data_hex_str) + crc_8(
                bytes.fromhex(data_hex_str))

        self.transaction_id += 1

        if self.transaction_id > 65535:
            self.transaction_id = 1

        return msg


def rmap_bytes_to_dict(rmap_bytes_msg):
    if len(rmap_bytes_msg) < 8:
        return None

    instruction = rmap_bytes_msg[2]

    packet_type = instruction >> 6
    write = (instruction & 0x3F) >> 5

    if packet_type == 1:
        if write == 1:
            return {
                'target_logical_address':
                rmap_bytes_msg[0],
                'protocol_identifier':
                rmap_bytes_msg[1],
                'packet_type':
                packet_type,
                'cmd_write':
                write,
                'cmd_verify': (instruction & 0x1F) >> 4,
                'cmd_reply': (instruction & 0xF) >> 3,
                'cmd_incr': (instruction & 0x7) >> 2,
                'key':
                rmap_bytes_msg[3],
                'initiator_logical_address':
                rmap_bytes_msg[4],
                'transaction_id':
                int.from_bytes(rmap_bytes_msg[5:7], 'big'),
                'extended_addr':
                rmap_bytes_msg[7],
                'address':
                int.from_bytes(rmap_bytes_msg[8:12], 'big'),
                'data_length':
                int.from_bytes(rmap_bytes_msg[12:15], 'big'),
                'data_length_valid':
                int.from_bytes(rmap_bytes_msg[12:15],
                               'big') == len(rmap_bytes_msg) - 17,
                'header_crc':
                bytes([rmap_bytes_msg[15]]),
                'header_crc_valid':
                crc_8(rmap_bytes_msg[0:15]) == bytes([rmap_bytes_msg[15]]),
                'data':
                rmap_bytes_msg[16:-1],
                'data_crc':
                bytes([rmap_bytes_msg[-1]]),
                'data_crc_valid':
                crc_8(rmap_bytes_msg[16:-1]) == bytes([rmap_bytes_msg[-1]]),
            }
        else:
            return {
                'target_logical_address':
                rmap_bytes_msg[0],
                'protocol_identifier':
                rmap_bytes_msg[1],
                'packet_type':
                packet_type,
                'cmd_write':
                write,
                'cmd_verify': (instruction & 0x1F) >> 4,
                'cmd_reply': (instruction & 0xF) >> 3,
                'cmd_incr': (instruction & 0x7) >> 2,
                'key':
                rmap_bytes_msg[3],
                'initiator_logical_address':
                rmap_bytes_msg[4],
                'transaction_id':
                int.from_bytes(rmap_bytes_msg[5:7], 'big'),
                'extended_addr':
                rmap_bytes_msg[7],
                'address':
                int.from_bytes(rmap_bytes_msg[8:12], 'big'),
                'data_length':
                int.from_bytes(rmap_bytes_msg[12:15], 'big'),
                'header_crc':
                bytes([rmap_bytes_msg[15]]),
                'header_crc_valid':
                crc_8(rmap_bytes_msg[0:15]) == bytes([rmap_bytes_msg[15]]),
            }
    elif write == 1:
        return {
            'initiator_logical_address':
            rmap_bytes_msg[0],
            'protocol_identifier':
            rmap_bytes_msg[1],
            'packet_type':
            packet_type,
            'cmd_write': (instruction & 0x3F) >> 5,
            'cmd_verify': (instruction & 0x1F) >> 4,
            'cmd_reply': (instruction & 0xF) >> 3,
            'cmd_incr': (instruction & 0x7) >> 2,
            'status':
            rmap_bytes_msg[3],
            'target_logical_address':
            rmap_bytes_msg[4],
            'transaction_id':
            int.from_bytes(rmap_bytes_msg[5:7], 'big'),
            'header_crc':
            bytes([rmap_bytes_msg[7]]),
            'header_crc_valid':
            crc_8(rmap_bytes_msg[0:7]) == bytes([rmap_bytes_msg[7]]),
        }
    else:
        return {
            'initiator_logical_address':
            rmap_bytes_msg[0],
            'protocol_identifier':
            rmap_bytes_msg[1],
            'packet_type':
            packet_type,
            'cmd_write': (instruction & 0x3F) >> 5,
            'cmd_verify': (instruction & 0x1F) >> 4,
            'cmd_reply': (instruction & 0xF) >> 3,
            'cmd_incr': (instruction & 0x7) >> 2,
            'status':
            rmap_bytes_msg[3],
            'target_logical_address':
            rmap_bytes_msg[4],
            'transaction_id':
            int.from_bytes(rmap_bytes_msg[5:7], 'big'),
            'reserved':
            rmap_bytes_msg[7],
            'data_length':
            int.from_bytes(rmap_bytes_msg[8:11], 'big'),
            'header_crc':
            bytes([rmap_bytes_msg[11]]),
            'header_crc_valid':
            crc_8(rmap_bytes_msg[0:11]) == bytes([rmap_bytes_msg[11]]),
            'data':
            rmap_bytes_msg[12:-1],
            'data_crc':
            bytes([rmap_bytes_msg[-1]]),
            'data_crc_valid':
            crc_8(rmap_bytes_msg[12:-1]) == bytes([rmap_bytes_msg[-1]]),
        }
