############################################################################
#
# Copyright (c) Mamba Developers. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#
############################################################################
""" Single Port TCP controller base """

from typing import Optional, Dict, Any
import os
import struct
import socket

from mamba.core.component_base import TcpInstrumentDriver
from mamba.core.context import Context
from mamba.core.rmap_utils.rmap_common \
    import RMAP, rmap_bytes_to_dict
from mamba.core.msg import ServiceRequest, \
    ServiceResponse, ParameterType


def rmap_raw_write(sock: socket.socket, rmap_cmd: bytes) -> None:
    num_bytes = struct.pack("I", len(rmap_cmd))
    sock.sendall(num_bytes)
    sock.sendall(rmap_cmd)


def rmap_raw_reply(sock: socket.socket) -> bytes:
    recv_header = sock.recv(12)
    flags = recv_header[-4]

    recv_reply = b''

    if (flags == 0) or (flags == 8):  # 0: EOP, 8: EEP
        recv_size = int.from_bytes(recv_header[-3:], 'big')

        while len(recv_reply) < recv_size:
            recv = sock.recv(recv_size - len(recv_reply))
            if not recv:
                break
            recv_reply = recv_reply + recv

    return recv_reply


class H8823SpwRmapController(TcpInstrumentDriver):
    """ Simple TCP controller base class """
    def __init__(self,
                 context: Context,
                 local_config: Optional[dict] = None) -> None:
        super().__init__(os.path.dirname(__file__), context, local_config)

        # Initialize instrument configuration
        self._rmap = RMAP(self._configuration.get('rmap'))

    def _process_inst_command(self, cmd_type: str, cmd: Dict[str, Any],
                              service_request: ServiceRequest,
                              result: ServiceResponse) -> None:

        connection_attempts = 0
        success = False

        while connection_attempts < self._instrument.max_connection_attempts:
            connection_attempts += 1

            if self._inst is not None:
                try:
                    if cmd_type == 'query':
                        try:
                            raw_cmd = bytes.fromhex(
                                cmd.format(*service_request.args))
                            rmap_raw_write(self._inst, raw_cmd)
                            self._shared_memory['last_raw_cmd'] = raw_cmd.hex(
                            ).upper()
                        except ValueError:
                            result.type = ParameterType.error
                            result.value = 'Invalid Hexadecimal Parameter'
                            self._log_error(result.value)
                            return

                        raw_reply = rmap_raw_reply(self._inst).hex().upper()

                        if service_request.type == ParameterType.set:
                            self._shared_memory[self._shared_memory_setter[
                                service_request.id]] = raw_reply
                        else:
                            result.value = raw_reply

                        self._shared_memory['last_raw_reply'] = raw_reply

                    elif cmd_type == 'write':
                        try:
                            raw_cmd = bytes.fromhex(
                                cmd.format(*service_request.args))
                            rmap_raw_write(self._inst, raw_cmd)
                            self._shared_memory['last_raw_cmd'] = raw_cmd.hex()
                        except ValueError:
                            result.type = ParameterType.error
                            result.value = 'Invalid Hexadecimal Parameter'
                            self._log_error(result.value)
                            return

                    elif cmd_type == 'rmap':
                        try:
                            rmap_cmd = self._rmap.get_rmap_cmd(
                                write=cmd['command_code'].get('write', 0),
                                verify=cmd['command_code'].get('verify', 0),
                                reply=cmd['command_code'].get('reply', 0),
                                inc=cmd['command_code'].get(
                                    'increment_address', 0),
                                address=int(
                                    cmd['address'].format(
                                        *service_request.args), 16),
                                size=cmd.get('size')
                                if isinstance(cmd.get('size'), int) else int(
                                    cmd.get(
                                        'size',
                                        '0').format(*service_request.args)),
                                data_hex_str=cmd.get(
                                    'body', '').format(*service_request.args),
                                extended_addr=int(
                                    cmd.get(
                                        'extended_addr',
                                        '0').format(*service_request.args)),
                            )
                        except ValueError:
                            result.type = ParameterType.error
                            result.value = 'Parameter error'
                            self._log_error(result.value)
                            return

                        rmap_raw_write(self._inst, rmap_cmd)
                        self._shared_memory['last_raw_cmd'] = rmap_cmd.hex(
                        ).upper()

                        if cmd['command_code'].get('reply', 0) == 1:
                            raw_reply = rmap_raw_reply(self._inst)
                            self._shared_memory[
                                'last_raw_reply'] = raw_reply.hex().upper()

                            reply = rmap_bytes_to_dict(raw_reply)

                            if len(reply) == 0 or reply['status'] != 0:
                                result.type = ParameterType.error
                                result.value = 'RMAP Reply error'

                            if cmd['command_code'].get('write', 0) == 0:
                                res = reply['data'].hex().upper()

                                if service_request.type == ParameterType.set:
                                    self._shared_memory[
                                        self._shared_memory_setter[
                                            service_request.id]] = res
                                else:
                                    result.value = res

                except (ConnectionRefusedError, OSError):
                    self._instrument_disconnect()
                    self._instrument_connect()
                    continue
            else:
                result.type = ParameterType.error
                result.value = 'Not possible to perform command before ' \
                               'connection is established'
                self._log_error(result.value)

            success = True
            break

        if not success:
            result.type = ParameterType.error
            result.value = 'Not possible to communicate to the' \
                           ' instrument'
            self._log_error(result.value)
