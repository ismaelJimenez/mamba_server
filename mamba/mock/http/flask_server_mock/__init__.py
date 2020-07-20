################################################################################################
##
##  Copyright (c) Mamba Developers. All rights reserved.
##  Licensed under the MIT License. See License.txt in the project root for license information.
##
################################################################################################

""" Component for simulating a Flask server """

import os
import threading
import http.client
from typing import Optional, Dict, Union

from flask import Flask, request, make_response, jsonify, abort
from rx import operators as op

from mamba.core.component_base import InstrumentDriver
from mamba.core.msg import Empty
from mamba.core.exceptions import ComponentConfigException
from mamba.core.context import Context
from mamba.core.utils import get_properties_dict

params_dict: Dict[str, Union[str, int, float]] = {}

app = Flask(__name__)


@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)


@app.route('/query', methods=['GET'])
def query_parameter():
    parameter = request.args.get('param', default='', type=str)

    if len(parameter) == 0 or parameter not in params_dict:
        abort(404)

    return str(params_dict[parameter])


@app.route('/write', methods=['PUT'])
def write_parameter():
    parameter = request.args.get('param', default='', type=str)
    value = request.args.get('value', default='', type=str)

    if len(parameter) == 0 or parameter not in params_dict:
        abort(404)

    params_dict[parameter] = value

    return "OK"


def shutdown_server():
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        raise RuntimeError('Not running with the Werkzeug Server')
    func()


@app.route('/shutdown', methods=['POST'])
def shutdown():
    shutdown_server()
    return 'Server shutting down...'


class FlaskServerMock(InstrumentDriver):
    """ Flask Server Mock """
    def __init__(self,
                 context: Context,
                 local_config: Optional[dict] = None) -> None:
        super().__init__(os.path.dirname(__file__), context, local_config)

        self._flask_server_thread: Optional[threading.Thread] = None

    def initialize(self) -> None:
        global app
        global params_dict

        # Component configuration
        for key, parameter_info in self._configuration['parameters'].items():
            params_dict[key] = parameter_info.get('initial_value')

        # Start a thread with the server -- that thread will then start one
        # more thread for each request
        self._flask_server_thread = threading.Thread(
            target=lambda: app.run(port=self._instrument.port))

        # Exit the server thread when the main thread terminates
        self._flask_server_thread.daemon = True
        self._flask_server_thread.start()
        self._log_info(f'Flask Server running in thread: '
                       f'{self._flask_server_thread.name}')

    def _close(self, rx_value: Optional[Empty] = None) -> None:
        """ Entry point for closing the component """
        if self._flask_server_thread is not None:
            try:
                conn = http.client.HTTPConnection(self._instrument.address,
                                                  self._instrument.port)

                conn.request("POST", "/shutdown")
            except OSError:
                pass
