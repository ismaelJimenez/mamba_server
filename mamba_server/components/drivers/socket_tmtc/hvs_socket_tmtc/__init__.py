""" Socket to TMTC translator """

import os
import time

from rx import operators as op

from mamba_server.components.observable_types import RawTelemetry, \
    RawTelecommand, Telecommand, Telemetry
from mamba_server.components import ComponentBase


class Driver(ComponentBase):
    """ Socket to TMTC translator class """
    def __init__(self, context, local_config=None):
        super(Driver, self).__init__(os.path.dirname(__file__), context,
                                     local_config)

        # Initialize observers
        self._register_observers()

    def _register_observers(self):
        # Register to the raw_tc provided by the socket server service
        self._context.rx['raw_tc'].pipe(
            op.filter(lambda value: isinstance(value, RawTelecommand))
        ).subscribe(on_next=self._received_raw_tc)

        # Register to the telemetries provided by the central controller
        self._context.rx['tm'].pipe(
            op.filter(lambda value: isinstance(value, Telemetry))).subscribe(
                on_next=self._received_tm)

    def _received_raw_tc(self, raw_tc: RawTelecommand):
        """ Entry point for processing a new raw telecommand coming from the
            socket server.

            Args:
                raw_tc (RawTelecommand): The raw telecommand coming from
                                         the socket.
        """
        self._log_dev('Received Raw TC')
        for telecommand in raw_tc.raw.replace('"', '').split('\r\n')[:-1]:
            tc_list = telecommand.rstrip().split(' ')
            self._log_dev('Published TC')
            self._context.rx['tc'].on_next(
                Telecommand(tc_id=tc_list[1],
                            args=tc_list[2:],
                            tc_type=tc_list[0]))

    def _received_tm(self, telemetry: Telemetry):
        """ Entry point for processing a new telemetry generated by the
            central controller.

            Args:
                tm (Telemetry): The telemetry coming from the central
                                controller.
        """
        self._log_dev('Received TM')
        if telemetry.type == 'tc':
            raw_tm = f"> OK {telemetry.id}\r\n"
        elif telemetry.type == 'tm':
            raw_tm = f"> OK {telemetry.id};{time.time()};{telemetry.value};" \
                     f"{telemetry.value};0;1\r\n"
        elif telemetry.type == 'tc_meta':
            raw_tm = f"> OK {telemetry.id};{telemetry.value['num_params']};" \
                     f"{telemetry.value['description']}\r\n"
        elif telemetry.type == 'tm_meta':
            raw_tm = f"> OK {telemetry.id};{telemetry.value['return_type']};" \
                     f"{telemetry.value['return_type']};" \
                     f"{telemetry.value['description']};7;4\r\n"
        elif telemetry.type == 'error':
            raw_tm = f"> ERROR {telemetry.type} {telemetry.id} {telemetry.value}\r\n"
        else:  # helo and Unrecognized type
            raw_tm = f"> OK {telemetry.type} {telemetry.id}\r\n"

        self._log_dev('Published Raw TM')
        self._context.rx['raw_tm'].on_next(RawTelemetry(raw_tm))

