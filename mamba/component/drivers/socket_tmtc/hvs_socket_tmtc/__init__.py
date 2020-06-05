""" Socket to TMTC translator """

import os
import time

from rx import operators as op

from mamba.core.msg import Raw, ServiceRequest, ServiceResponse
from mamba.component import ComponentBase


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
            op.filter(lambda value: isinstance(value, Raw))).subscribe(
                on_next=self._received_raw_tc)

        # Register to the telemetries provided by the central controller
        self._context.rx['tm'].pipe(
            op.filter(lambda value: isinstance(value, ServiceResponse))
        ).subscribe(on_next=self._received_tm)

    def _received_raw_tc(self, raw_tc: Raw):
        """ Entry point for processing a new msg telecommand coming from the
            socket server.

            Args:
                raw_tc (Raw): The msg telecommand coming from
                                         the socket.
        """
        self._log_dev('Received Raw TC')
        for telecommand in raw_tc.msg.replace('"', '').split('\r\n')[:-1]:
            tc_list = telecommand.rstrip().split(' ')
            self._log_dev('Published TC')
            self._context.rx['tc'].on_next(
                ServiceRequest(id=tc_list[1],
                               args=tc_list[2:],
                               type=tc_list[0].replace('tc', 'set').replace('tm', 'get')))

    def _received_tm(self, telemetry: ServiceResponse):
        """ Entry point for processing a new telemetry generated by the
            central controller.

            Args:
                tm: The telemetry coming from the central
                                controller.
        """
        self._log_dev('Received TM')
        if telemetry.type == 'set':
            raw_tm = f"> OK {telemetry.id}\r\n"
        elif telemetry.type == 'get':
            raw_tm = f"> OK {telemetry.id};{time.time()};{telemetry.value};" \
                     f"{telemetry.value};0;1\r\n"
        elif telemetry.type == 'set_meta':
            raw_tm = f"> OK {telemetry.id};" \
                     f"{len(telemetry.value['signature'][0])};" \
                     f"{telemetry.value['description']}\r\n"
        elif telemetry.type == 'get_meta':
            raw_tm = f"> OK {telemetry.id};" \
                     f"{telemetry.value['signature'][1]};" \
                     f"{telemetry.value['signature'][1]};" \
                     f"{telemetry.value['description']};7;4\r\n"
        elif telemetry.type == 'error':
            raw_tm = f"> ERROR {telemetry.id} {telemetry.value}\r\n"
        else:  # helo and Unrecognized type
            raw_tm = f"> OK {telemetry.type} {telemetry.id}\r\n"

        self._log_dev('Published Raw TM')
        self._context.rx['raw_tm'].on_next(Raw(raw_tm))
