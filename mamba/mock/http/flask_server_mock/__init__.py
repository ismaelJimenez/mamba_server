""" Component for simulating a Flask server """

import os
import threading
import http.client
from typing import Optional

from flask import Flask, request, make_response, jsonify, abort
from rx import operators as op

from mamba.components import ComponentBase
from mamba.components.observable_types import Empty
from mamba.internal.exceptions import ComponentConfigException
from mamba.core.context import Context

params_dict = {}

app = Flask(__name__)


@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)


@app.route('/get', methods=['GET'])
def get_parameter():
    parameter = request.args.get('param', default='', type=str)

    if len(parameter) == 0 or parameter not in params_dict:
        abort(404)

    return str(params_dict[parameter])


@app.route('/set', methods=['PUT'])
def set_parameter():
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


class FlaskServerMock(ComponentBase):
    """ Flask Server Mock """
    def __init__(self,
                 context: Context,
                 local_config: Optional[dict] = None) -> None:
        global params_dict
        super(FlaskServerMock, self).__init__(os.path.dirname(__file__),
                                              context, local_config)

        # Component configuration
        params_dict = {}  # Value of the parameters

        if 'device' in self._configuration and 'properties' in \
                self._configuration['device']:
            for key, value in self._configuration['device'][
                    'properties'].items():
                params_dict[key] = value.get('default')

        self._flask_server_thread: Optional[threading.Thread] = None

        # Initialize observers
        self._register_observers()

    def _register_observers(self) -> None:
        # Quit topic is published to command App finalization
        self._context.rx['quit'].pipe(
            op.filter(lambda value: isinstance(value, Empty))).subscribe(
                on_next=self._close)

    def initialize(self) -> None:
        global app
        if not all(key in self._configuration for key in ['port']):
            raise ComponentConfigException(
                "Missing required elements in component configuration")

        # Start a thread with the server -- that thread will then start one
        # more thread for each request
        self._flask_server_thread = threading.Thread(
            target=lambda: app.run(port=self._configuration['port']))

        # Exit the server thread when the main thread terminates
        self._flask_server_thread.daemon = True
        self._flask_server_thread.start()
        self._log_info(f'Flask Server running in thread: '
                       f'{self._flask_server_thread.name}')

    def _close(self, rx_value: Optional[Empty] = None) -> None:
        """ Entry point for closing the component """
        if self._flask_server_thread is not None:
            conn = http.client.HTTPConnection('localhost', self._configuration['port'])
            conn.request("POST", "/shutdown")
