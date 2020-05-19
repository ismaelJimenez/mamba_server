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
        self._context.rx['raw_tc'].pipe(
            op.filter(lambda value: isinstance(value, str))).subscribe(
                on_next=self._received_raw_tc)
        self._context.rx['tm'].pipe(
            op.filter(lambda value: isinstance(value, list))).subscribe(
                on_next=self._received_tm)

    def _received_raw_tc(self, rx_value):
        """ Entry point for running the plugin

            Args:
                rx_value (RunAction): The value published by the subject.
        """
        for telecommand in rx_value.split('\r\n')[:-1]:
            tc = telecommand.split(' ')
            self._context.rx['tc'].on_next(tc)

    def _received_tm(self, rx_value):
        """ Entry point for running the plugin

            Args:
                rx_value (RunAction): The value published by the subject.
        """
        tm = "> "

        if rx_value[0] == 'ACK':
            tm += f'OK {rx_value[1]} {rx_value[2]}'

        tm += "\r\n"

        self._context.rx['raw_tm'].on_next(tm)
