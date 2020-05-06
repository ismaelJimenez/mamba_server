# -*- coding: utf-8 -*-
"""Minimal XMLRPC server for performance tests"""

from xmlrpc.server import SimpleXMLRPCServer

# Create server
with SimpleXMLRPCServer(('localhost', 8000)) as server:
    server.register_introspection_functions()

    # Register pow() function; this will use the value of
    # pow.__name__ as the name, which is just 'pow'.
    server.register_function(pow)

    # Run the server's main loop
    server.serve_forever()
