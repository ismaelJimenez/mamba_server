import os

from rx import operators as op

from mamba_server.components.observable_types import Telecommand, Telemetry, IoServiceRequest
from mamba_server.components import ComponentBase
from mamba_server.exceptions import ComponentConfigException


class Driver(ComponentBase):
    def __init__(self, context, local_config=None):
        super(Driver, self).__init__(os.path.dirname(__file__), context,
                                     local_config)

        # Initialize observers
        self._register_observers()

        # Define custom variables
        self._io_services = {}

    def _register_observers(self):
        self._context.rx['tc'].pipe(
            op.filter(lambda value: isinstance(value, Telecommand))).subscribe(
                on_next=self._received_tc)

        self._context.rx['io_service_signature'].pipe(
            op.filter(lambda value: isinstance(value, dict))).subscribe(
                on_next=self._io_service_signature)

    def _received_tc(self, telecommand: Telecommand):
        """ Entry point for running the plugin

            Args:
                rx_value (RunAction): The value published by the subject.
        """
        self._log_dev('Received TC')
        self._log_dev(telecommand.type)
        if telecommand.type == 'helo':
            print('HELO')
            self._context.rx['tm'].on_next(
                Telemetry(tm_id=telecommand.id, tm_type=telecommand.type))

        else:
            if telecommand.id not in self._io_services:
                self._context.rx['tm'].on_next(
                    Telemetry(tm_id=telecommand.id,
                              tm_type='error',
                              value='Not recognized command'))
                return

            if telecommand.type == 'tc_meta':
                self._log_dev('Start processing tc_meta')
                print(self._io_services)
                io_service = self._io_services[telecommand.id]
                self._context.rx['tm'].on_next(
                    Telemetry(tm_id=telecommand.id,
                              tm_type=telecommand.type,
                              value={
                                  'signature': io_service["signature"],
                                  'description': io_service["description"]
                              }))

            elif telecommand.type == 'tm_meta':
                io_service = self._io_services[telecommand.id]
                return_type = io_service["signature"]

                self._context.rx['tm'].on_next(
                    Telemetry(tm_id=telecommand.id,
                              tm_type=telecommand.type,
                              value={
                                  'signature': io_service["signature"],
                                  'description': io_service["description"]
                              }))

            elif telecommand.type == 'tc':
                #self._context.rx['tm'].on_next(
                #    Telemetry(tm_id=telecommand.id, tm_type=telecommand.type))
                self._io_result_subs = self._context.rx['io_result'].pipe(
                    op.filter(lambda value: isinstance(value, Telemetry))
                ).subscribe(on_next=lambda _: self._io_result(telecommand, _))

                self._context.rx['io_service_request'].on_next(
                    IoServiceRequest(id=telecommand.id,
                                     type=telecommand.type,
                                     args=telecommand.args))

            elif telecommand.type == 'tm':
                self._io_result_subs = self._context.rx['io_result'].pipe(
                    op.filter(lambda value: isinstance(value, Telemetry))
                ).subscribe(on_next=lambda _: self._io_result(telecommand, _))

                self._context.rx['io_service_request'].on_next(
                    IoServiceRequest(id=telecommand.id,
                                     type=telecommand.type,
                                     args=telecommand.args))
            else:
                self._context.rx['tm'].on_next(
                    Telemetry(tm_id=telecommand.id,
                              tm_type='error',
                              value= 'Not recognized command type'))

    def _io_result(self, telecommand, rx_result):
        self._io_result_subs.dispose()
        print('IO_RESULT')
        self._context.rx['tm'].on_next(
            Telemetry(tm_id=telecommand.id,
                      tm_type=telecommand.type,
                      value=rx_result.value))

    def _io_service_signature(self, signatures):
        new_signatures = [key for key, value in signatures.items()]
        self._log_info(
            f"Received signatures: {new_signatures}"
        )

        for new_signature in new_signatures:
            if new_signature in self._io_services:
                raise ComponentConfigException(f"Received conflicting service key: {new_signature}")

        for key, value in signatures.items():
            if not isinstance(value.get('signature'), list) or len(
                    value.get('signature')) != 2 or not isinstance(
                        value.get('signature')[0], list):
                raise ComponentConfigException(
                    f'Signature of service "{key}" is invalid. Format shall'
                    f' be [[arg_1, arg_2, ...], return_type]')

        self._io_services.update(signatures)
