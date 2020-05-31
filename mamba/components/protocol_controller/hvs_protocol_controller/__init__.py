import os

from rx import operators as op

from mamba.core.msg import Telecommand, Telemetry,\
    IoServiceRequest
from mamba.components import ComponentBase
from mamba.core.exceptions import ComponentConfigException


class Driver(ComponentBase):
    def __init__(self, context, local_config=None):
        super(Driver, self).__init__(os.path.dirname(__file__), context,
                                     local_config)

        # Initialize observers
        self._register_observers()

        # Define custom variables
        self._io_services = {}
        self._io_result_subs = None

    def _register_observers(self):
        """ Entry point for registering component observers """

        # Register to the tc provided by the socket protocol translator service
        self._context.rx['tc'].pipe(
            op.filter(lambda value: isinstance(value, Telecommand))).subscribe(
                on_next=self._received_tc)

        # Register to the topic provided by the io_controller services
        self._context.rx['io_service_signature'].pipe(
            op.filter(lambda value: isinstance(value, dict))).subscribe(
                on_next=self._io_service_signature)

    def _generate_tm(self, telecommand: Telecommand):
        """ Entry point for generating response telemetry

            Args:
                telecommand: The service request received.
        """

        result = Telemetry(tm_id=telecommand.id, tm_type=telecommand.type)

        if 'meta' in telecommand.type:
            io_service = self._io_services[telecommand.id]

            result.value = {
                'signature': io_service["signature"],
                'description': io_service["description"]
            }

        self._context.rx['tm'].on_next(result)

    def _generate_error_tm(self, telecommand: Telecommand, message: str):
        """ Entry point for generating error response telemetry

            Args:
                telecommand: The service request received.
                message: The error feedback message.
        """

        self._context.rx['tm'].on_next(
            Telemetry(tm_id=telecommand.id, tm_type='error', value=message))

    def _generate_io_service_request(self, telecommand: Telecommand):
        """ Entry point for generating a IO Service request to fulfill
            a request

            Args:
                telecommand: The service request received.
        """

        self._io_result_subs = self._context.rx['io_result'].pipe(
            op.filter(lambda value: isinstance(value, Telemetry))).subscribe(
                on_next=self._process_io_result)

        self._context.rx['io_service_request'].on_next(
            IoServiceRequest(id=telecommand.id,
                             type=telecommand.type,
                             args=telecommand.args))

    def _received_tc(self, telecommand: Telecommand):
        """ Entry point for processing a new telecommand coming from the
            socket translator.

            Args:
                telecommand: The telecommand coming from the socket translator.
        """
        self._log_dev(f'Received TC: {telecommand.id}')
        if (telecommand.id
                not in self._io_services) and (telecommand.type != 'helo'):
            self._generate_error_tm(telecommand, 'Not recognized command')
            return

        if telecommand.type in ['helo', 'tc_meta', 'tm_meta']:
            self._generate_tm(telecommand)
        elif telecommand.type in ['tc', 'tm']:
            self._generate_io_service_request(telecommand)
        else:
            self._generate_error_tm(telecommand, 'Not recognized command type')

    def _process_io_result(self, rx_result: Telemetry):
        """ Entry point for processing the IO Service results.

            Args:
                rx_result: The io service response.
        """
        self._io_result_subs.dispose()
        self._context.rx['tm'].on_next(rx_result)

    def _io_service_signature(self, signatures: dict):
        """ Entry point for processing the service signatures.

            Args:
                signatures: The io service signatures dictionary.
        """
        new_signatures = [key for key, value in signatures['services'].items()]
        self._log_info(f"Received signatures: {new_signatures}")

        for new_signature in new_signatures:
            if new_signature in self._io_services:
                raise ComponentConfigException(
                    f"Received conflicting service key: {new_signature}")

        for key, value in signatures['services'].items():
            if not isinstance(value.get('signature'), list) or len(
                    value.get('signature')) != 2 or not isinstance(
                        value.get('signature')[0], list):
                raise ComponentConfigException(
                    f'Signature of service "{key}" is invalid. Format shall'
                    f' be [[arg_1, arg_2, ...], return_type]')

        self._io_services.update(signatures['services'])
