""" Component for simulating XMLRPC server equipment """

import os
import threading
from typing import Optional

from rx import operators as op

from mamba.components import ComponentBase
from mamba.components.observable_types import Empty
from mamba.internal.exceptions import ComponentConfigException
from mamba.core.context import Context

from xmlrpc.server import SimpleXMLRPCServer
from xmlrpc.server import SimpleXMLRPCRequestHandler


# Restrict to a particular path.
class RequestHandler(SimpleXMLRPCRequestHandler):
    rpc_paths = ('/RPC2', )


class MockXMLRPCServer(SimpleXMLRPCServer):
    def __init__(self, address, tm_dict, request_handler=RequestHandler):
        super(MockXMLRPCServer, self).__init__(address, request_handler)

        self.register_introspection_functions()
        self._tm_dict = tm_dict

        self.register_function(lambda tm: self._tm_dict.get(tm) or 'key-error',
                               'get_tm')


class XmlRpcMock(ComponentBase):
    """ XMLRPC Server Mock """
    def __init__(self,
                 context: Context,
                 local_config: Optional[dict] = None) -> None:
        super(XmlRpcMock, self).__init__(os.path.dirname(__file__), context,
                                         local_config)

        # Component configuration
        self._tm_dict = {}

        if 'device' in self._configuration and 'properties' in \
                self._configuration['device']:
            for key, value in self._configuration['device'][
                    'properties'].items():
                self._tm_dict[key] = value.get('default')

        self._server: Optional[MockXMLRPCServer] = None
        self._server_thread: Optional[threading.Thread] = None

        # Initialize observers
        self._register_observers()

    def _register_observers(self) -> None:
        # Quit topic is published to command App finalization
        self._context.rx['quit'].pipe(
            op.filter(lambda value: isinstance(value, Empty))).subscribe(
                on_next=self._close)

    def initialize(self) -> None:
        if not all(key in self._configuration for key in ['host', 'port']):
            raise ComponentConfigException(
                "Missing required elements in component configuration")

        # Create the XMLRPC server, binding to host and port
        self._server = MockXMLRPCServer(address=(self._configuration['host'],
                                                 self._configuration['port']),
                                        tm_dict=self._tm_dict,
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

    def _close(self, rx_value: Optional[Empty] = None) -> None:
        """ Entry point for closing the component """
        if self._server is not None:
            self._server.shutdown()

        if self._server_thread is not None:
            self._server_thread.join()
