import os

from rx import operators as op

from mamba_server.components import ComponentBase


class Driver(ComponentBase):
    def __init__(self, context, local_config=None):
        super(Driver, self).__init__(os.path.dirname(__file__), context,
                                     local_config)

    def initialize(self):
        self._context.rx['io_service_signature'].on_next({
            'provider': self._name,
            'services':{
            'SHUTDOWN': {
                'signature': [[], None],
                'description': 'Shutdown Mamba Server'
            }
        }})
