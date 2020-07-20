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

from mamba.marketplace.components.spacewire_gateway.utils.crc_8 \
    import crc_8


def generate_write_reply(write_cmd_bytes, status) -> bytes:
    write_reply = struct.pack("BBBBBBB", write_cmd_bytes[4],
                              write_cmd_bytes[1], write_cmd_bytes[2] & 0x3F,
                              status, write_cmd_bytes[0], write_cmd_bytes[5],
                              write_cmd_bytes[6])

    return write_reply + crc_8(write_reply)


def generate_read_reply(read_cmd_bytes, status, data) -> bytes:
    size = int(len(data) / 2)

    write_reply = struct.pack("BBBBBBBBBBB", read_cmd_bytes[4],
                              read_cmd_bytes[1], read_cmd_bytes[2] & 0xF,
                              status, read_cmd_bytes[0], read_cmd_bytes[5],
                              read_cmd_bytes[6], 0, (size >> 16) & 0xff,
                              (size >> 8) & 0xff, (size >> 0) & 0xff)

    return write_reply + crc_8(write_reply) + bytes.fromhex(data) + crc_8(
        bytes.fromhex(data))
