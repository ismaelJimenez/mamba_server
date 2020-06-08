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

        self.register_function(lambda tm: self._tm_dict.get(tm) or 'key-error',
                               'get_tm')


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
