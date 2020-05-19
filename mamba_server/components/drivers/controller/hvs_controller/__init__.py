import os

from rx import operators as op

from mamba_server.components import ComponentBase


class Driver(ComponentBase):
    def __init__(self, context, local_config=None):
        super(Driver, self).__init__(os.path.dirname(__file__), context,
                                     local_config)

        # Initialize observers
        self._register_observers()

    def _register_observers(self):
        self._context.rx['tc'].pipe(
            op.filter(lambda value: isinstance(value, list))).subscribe(
                on_next=self._received_tc)

    def _received_tc(self, rx_value):
        """ Entry point for running the plugin

            Args:
                rx_value (RunAction): The value published by the subject.
        """
        self._context.rx['tm'].on_next(['ACK', rx_value[0], rx_value[1]])
