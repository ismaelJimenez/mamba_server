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

""" Component for handling socket TMTC """

import os
import threading
import socketserver
from typing import Optional

from mamba.core.component_base import Component
from mamba.core.context import Context
from mamba.core.msg import Raw, Empty
from mamba.core.exceptions import ComponentConfigException


class TcpSingleSocketServer(Component):
    """ Plugin base class """
    def __init__(self,
                 context: Context,
                 local_config: Optional[dict] = None) -> None:
        super().__init__(os.path.dirname(__file__), context, local_config)

        # Define custom variables
        self._server: Optional[ThreadedTCPServer] = None
        self._server_thread: Optional[threading.Thread] = None

        # Initialize observers
        self._register_observers()

    def _register_observers(self) -> None:
        # Quit is sent to command App finalization
        self._context.rx['quit'].subscribe(on_next=self._close)

    def initialize(self) -> None:
        if not all(key in self._configuration for key in ['host', 'port']):
            raise ComponentConfigException(
                "Missing required elements in component configuration")

        # Create the socket server, binding to host and port
        socketserver.TCPServer.allow_reuse_address = True
        self._server = ThreadedTCPServer(
            (self._configuration['host'], self._configuration['port']),
            ThreadedTCPRequestHandler, self)

        # Start a thread with the server -- that thread will then start one
        # more thread for each request
        self._server_thread = threading.Thread(
            target=self._server.serve_forever)

        # Exit the server thread when the main thread terminates
        self._server_thread.daemon = True
        self._server_thread.start()
        print("Server loop running in thread:", self._server_thread.name)

    def _close(self, rx_value: Optional[Empty] = None) -> None:
        """ Entry point for closing application

            Args:
                rx_value (Empty): The value published by the subject.
        """
        if self._server is not None:
            self._server.shutdown()
            self._server = None


class ThreadedTCPRequestHandler(socketserver.BaseRequestHandler):
    """
    The request handler class for the socket server.

    It is instantiated once per connection to the server, and must
    override the handle() method to implement communication to the
    client.
    """
    def handle(self):
        # Register observer for raw_tm
        observer = self.server.raw_tm.subscribe(on_next=self.send_tm)

        # Send incoming data to raw_tc
        while True:
            # self.request is the TCP socket connected to the client
            try:
                data = str(self.request.recv(1024), 'utf-8')
                if not data:
                    break
                self.server.log_dev(fr' -> Received socket TC: {data}')
                self.server.raw_tc.on_next(Raw(data))
            except ConnectionResetError:
                break

        # Dispose observer when connection is closed
        observer.dispose()

        self.server.log_info('Remote socket connection has been closed')

    def send_tm(self, raw_tm: Raw):
        """ Send msg telemetry over the socket connection """
        self.server.log_dev(  # type: ignore
            fr' <- Published socket TM: {raw_tm.msg}')
        try:
            self.request.sendall(raw_tm.msg.encode('utf-8'))
        except BrokenPipeError:
            pass


class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    def __init__(self, server_address, request_handler_class,
                 parent: TcpSingleSocketServer) -> None:
        super().__init__(server_address, request_handler_class)

        self.raw_tc = parent._context.rx['raw_tc']
        self.raw_tm = parent._context.rx['raw_tm']
        self.log_dev = parent._log_dev
        self.log_info = parent._log_info
