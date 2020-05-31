""" Digitizer IO Controller"""

import os
import threading
import pyvisa

from mamba.core.msg import ServiceRequest,\
    ServiceResponse
from mamba.component.io_controller import VisaControllerBase


class ThreadedTriggerInHandler:
    def __init__(self, tm_id, _inst, rx, _shared_memory, shared_memory_setter,
                 arg):
        _inst.write('TRIG:SOUR EXT')
        _inst.write('INIT')

        sleep_seconds = float(arg[0]) if len(arg) > 0 else 3

        _inst.timeout = sleep_seconds * 1000

        # print(f"init wait for {sleep_seconds}")
        # import time
        # time.sleep(sleep_seconds)
        # print("end wait")

        try:
            _inst.query('*OPC?')  # This waits for trigger
            _shared_memory[shared_memory_setter[tm_id]] = 1
        except pyvisa.errors.VisaIOError:
            _shared_memory[shared_memory_setter[tm_id]] = 'timedout'


class SpectrumAnalyzer(VisaControllerBase):
    """ Digitizer IO Controller class """
    def __init__(self, context, local_config=None):
        super(SpectrumAnalyzer, self).__init__(os.path.dirname(__file__),
                                               context, local_config)

        self._trigger_in_thread = None

    def _service_preprocessing(self, service_request: ServiceRequest,
                               result: ServiceResponse) -> None:
        """Perform preprocessing of the services listed in _custom_process.
        Note: This step is useful in case a merge of multiple arguments into
        one unique argument is needed. If the 'command' argument is not
        defined for the service, then no further processing will be done.
        Args:
            service_request: The current service request.
            result: The result to be published.
        """
        if service_request.id == 'SA_TC_QUERY_TRIGGER_IN':
            self._shared_memory[self._shared_memory_setter[
                service_request.id]] = 0

            self._trigger_in_thread = threading.Thread(
                target=ThreadedTriggerInHandler,
                args=(service_request.id, self._inst, self._context.rx,
                      self._shared_memory, self._shared_memory_setter,
                      service_request.args))

            self._trigger_in_thread.start()

        if service_request.id == 'SA_TM_QUERY_TRIGGER_IN':
            if self._shared_memory[self._shared_memory_getter[
                    service_request.id]] == 'timedout':
                result.type = 'error'
