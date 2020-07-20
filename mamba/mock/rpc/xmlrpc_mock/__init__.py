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

""" Component for simulating XMLRPC server equipment """

import os
import threading
from typing import Optional

from mamba.core.component_base import InstrumentDriver
from mamba.core.msg import Empty
from mamba.core.context import Context

from xmlrpc.server import SimpleXMLRPCServer
from xmlrpc.server import SimpleXMLRPCRequestHandler


# Restrict to a particular path.
class RequestHandler(SimpleXMLRPCRequestHandler):
    rpc_paths = ('/RPC2', )


class MockXMLRPCServer(SimpleXMLRPCServer):
    def __init__(self, address, tm_dict, request_handler=RequestHandler):
        super().__init__(address, request_handler)

        self.register_introspection_functions()
        self._tm_dict = tm_dict

        def raw_write(tm):
            cmd = tm.split(' ')
            if len(cmd) > 1:
                self._tm_dict[cmd[0]] = cmd[1]
            return 0

        self.register_function(raw_write, 'write')

        self.register_function(lambda tm: self._tm_dict.get(tm) or 'key-error',
                               'query')


class XmlRpcMock(InstrumentDriver):
    """ XMLRPC Server Mock """
    def __init__(self,
                 context: Context,
                 local_config: Optional[dict] = None) -> None:
        super().__init__(os.path.dirname(__file__), context, local_config)

        self._server: Optional[MockXMLRPCServer] = None
        self._server_thread: Optional[threading.Thread] = None

    def _close(self, rx_value: Optional[Empty] = None) -> None:
        """ Entry point for closing the component """
        if self._server is not None:
            self._server.shutdown()

        if self._server_thread is not None:
            self._server_thread.join()

    def initialize(self) -> None:
        for key, parameter_info in self._configuration['parameters'].items():
            self._shared_memory[key] = parameter_info.get('initial_value')

        # Create the XMLRPC server, binding to host and port
        self._server = MockXMLRPCServer(address=(self._instrument.address,
                                                 self._instrument.port),
                                        tm_dict=self._shared_memory,
                                        request_handler=RequestHandler)

        # Start a thread with the server -- that thread will then start one
        # more thread for each request
        self._server_thread = threading.Thread(
            target=self._server.serve_forever)

        # Exit the server thread when the main thread terminates
        self._server_thread.daemon = True
        self._server_thread.start()
        self._log_info(f'XMLRPC Mock Server running in thread: '
                       f'{self._server_thread.name}')
