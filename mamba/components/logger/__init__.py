import os

from rx import operators as op

from mamba.components.observable_types import Log
from mamba.components import ComponentBase


class Logger(ComponentBase):
    def __init__(self, context, local_config=None):
        super(Logger, self).__init__(os.path.dirname(__file__), context,
                                     local_config)

        # Initialize observers
        self._register_observers()

    def _register_observers(self):
        # Register to the raw_tc provided by the socket server service
        self._context.rx['log'].pipe(
            op.filter(lambda value: isinstance(value, Log))).subscribe(
                on_next=self._received_log)

    def _received_log(self, log: Log):
        """ Entry point for processing a new raw telecommand coming from the
            socket server.

            Args:
                raw_tc (Log): The raw telecommand coming from
                                         the socket.
        """
        print(f'[{log.level}] [{log.source}] {log.message}')
