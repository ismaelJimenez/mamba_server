################################################################################################
##
##  Copyright (c) Mamba Developers. All rights reserved.
##  Licensed under the MIT License. See License.txt in the project root for license information.
##
################################################################################################

""" Component for simulating HVS H8823 RMAP Spw protocol """

import os
import threading
import socketserver
from typing import Optional, Dict, Any
import struct
import time

from mamba.core.msg import Empty
from mamba.core.context import Context
from mamba.core.component_base import InstrumentDriver

from mamba.marketplace.components.spacewire_gateway.utils.rmap_common \
    import rmap_bytes_to_dict
from mamba.marketplace.components.spacewire_gateway.utils.rmap_test \
    import generate_write_reply, generate_read_reply


class H8823GatewaySpwRmapMock(InstrumentDriver):
    """ HVS H8823 RMAP Spw protocol Mock """
    def __init__(self,
                 context: Context,
                 local_config: Optional[dict] = None) -> None:
        super().__init__(os.path.dirname(__file__), context, local_config)

        self._server: Optional[ThreadedTcpServer] = None
        self._server_thread: Optional[threading.Thread] = None

        self._rmap_memory: Dict[str, Any] = {
            'last_msg': None,
            'last_msg_bytes': b'',
            'memory_table': {}
        }

    def _close(self, rx_value: Optional[Empty] = None) -> None:
        """ Entry point for closing the component """
        if self._server is not None:
            self._server.shutdown()

        if self._server_thread is not None:
            self._server_thread.join()

    def initialize(self) -> None:
        """ Entry point for component initialization """
        # Create the TM socket server, binding to host and port
        socketserver.TCPServer.allow_reuse_address = True
        self._server = ThreadedTcpServer(
            (self._instrument.address, self._instrument.port),
            ThreadedTcpHandler, self)

        # Start a thread with the server -- that thread will then start one
        # more thread for each request
        self._server_thread = threading.Thread(
            target=self._server.serve_forever)

        # Exit the server thread when the main thread terminates
        self._server_thread.daemon = True
        self._server_thread.start()
        self._log_info(f'RMAP Server running in thread: '
                       f'{self._server_thread.name}')


def send_reply(socket, reply_msg, split_reply):
    response_size = len(reply_msg)

    curr_time = time.time()

    time_sec = int(curr_time)
    time_ns = int((curr_time - int(curr_time)) * 1000000)

    res_header = struct.pack("iiBBBB", time_sec, time_ns, 0,
                             (response_size >> 16) & 0xff,
                             (response_size >> 8) & 0xff,
                             (response_size >> 0) & 0xff)

    socket.sendall(res_header)

    if split_reply:
        socket.sendall(reply_msg[:5])
        time.sleep(1)
        socket.sendall(reply_msg[5:])
    else:
        socket.sendall(reply_msg)


class ThreadedTcpHandler(socketserver.BaseRequestHandler):
    """
    The request handler class for the socket server.

    It is instantiated once per connection to the server, and must
    override the handle() method to implement communication to the
    client.
    """
    def handle(self):
        # Server to receive remote commands
        while True:
            # self.request is the TCP socket connected to the client
            try:
                size = self.request.recv(4)
                data = self.request.recv(int.from_bytes(size, 'little'))
                if not data:
                    break
            except ConnectionResetError:
                break

            self.server.log_dev(f'Received: {data}')
            self.server.rmap_memory['last_msg_bytes'] = data
            recv_msg = rmap_bytes_to_dict(data)
            self.server.rmap_memory['last_msg'] = recv_msg

            if recv_msg is not None and recv_msg['header_crc_valid']:
                if recv_msg['cmd_write'] == 1:
                    # Store new register value in memory
                    self.server.rmap_memory['memory_table'][recv_msg[
                        'address']] = b'\x00' * (recv_msg['data_length'] - len(
                            recv_msg['data'])) + recv_msg['data']

                    if recv_msg['cmd_reply'] == 1:
                        status = 1 if recv_msg['address'] == 11 else 0
                        reply_msg = generate_write_reply(data, status)
                        send_reply(self.request, reply_msg,
                                   recv_msg['address'] == 13)
                else:
                    partial_res = b''
                    if recv_msg['address'] in self.server.rmap_memory[
                            'memory_table']:
                        partial_res = self.server.rmap_memory['memory_table'][
                            recv_msg['address']]

                    res = b'\x00' * (recv_msg['data_length'] -
                                     len(partial_res)) + partial_res
                    status = 1 if recv_msg['address'] == 11 else 0

                    reply_msg = generate_read_reply(data, status, res.hex())
                    send_reply(self.request, reply_msg,
                               recv_msg['address'] == 13)

        self.server.log_info('Remote socket connection has been closed')


class ThreadedTcpServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    """ RMAP server """
    def __init__(self, server_address, request_handler_class,
                 parent: H8823GatewaySpwRmapMock) -> None:
        super().__init__(server_address, request_handler_class)
        self.log_dev = parent._log_dev
        self.log_info = parent._log_info
        self.rmap_memory = parent._rmap_memory
