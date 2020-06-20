import struct

from mamba.component.instrument_driver.spacewire_gateway.utils.crc_8 \
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
