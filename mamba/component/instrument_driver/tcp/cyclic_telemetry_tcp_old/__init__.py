""" TCP controller base """
from typing import Optional, Dict, Union
import os
import threading
import socket

from rx import operators as op

from mamba.core.component_base import TcpInstrumentDriver
from mamba.core.context import Context
from mamba.component import ComponentBase
from mamba.core.exceptions import ComponentConfigException
from mamba.core.msg import ServiceRequest, \
    ServiceResponse, Empty


class ThreadedTmHandler:
    def __init__(self, HOST, PORT, eom, shared_memory, rx, log_info,
                 shared_memory_getter):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            # Connect to server and send data
            sock.connect((HOST, PORT))

            while True:
                # self.request is the TCP socket connected to the client
                data = str(sock.recv(1024), 'utf-8')
                if not data:
                    break

                print(data.split(eom))
                print(shared_memory)

                for cmd in data.split(eom)[:-1]:
                    cmd = cmd.split(" ")
                    print(cmd)
                    shared_memory[cmd[0]] = cmd[1]

                    result = ServiceResponse(id=shared_memory_getter[cmd[0]],
                                             type=ParameterType.get,
                                             value=cmd[1])

                    rx['io_result'].on_next(result)

            log_info('Remote socket connection has been closed')


def send_tcp_tc(HOST, PORT, message, eom):
    # Create a socket (SOCK_STREAM means a TCP socket)
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        # Connect to server and send data
        sock.connect((HOST, PORT))
        sock.sendall(bytes(message + eom, "utf-8"))


class TcpControllerBase(TcpInstrumentDriver):
    """ TCP controller base class """
    def __init__(self,
                 context: Context,
                 local_config: Optional[dict] = None) -> None:
        super().__init__(os.path.dirname(__file__), context, local_config)

        self._inst_tm_thread: Optional[threading.Thread] = None

    def _tcp_connect(self, result: ServiceResponse) -> None:

        self._inst_tm_thread = threading.Thread(
            target=ThreadedTmHandler,
            args=(self._configuration['address'],
                  self._configuration['tm_port'], self._eom_r,
                  self._shared_memory, self._context.rx, self._log_info,
                  self._shared_memory_getter))

        self._inst_tm_thread.start()

        #     if self._configuration.get('tcp-sim'):
        #         self._inst = pytcp.ResourceManager(
        #             f"{self._simulation_file}@sim").open_resource(
        #                 self._configuration['address'],
        #                 read_termination='\n')
        #     else:
        #         try:
        #             self._inst = pytcp.ResourceManager().open_resource(
        #                 self._configuration['address'],
        #                 read_termination='\n')
        #         except (OSError, pytcp.errors.TcpIOError):
        #             result.type = 'error'
        #             result.value = 'Instrument is unreachable'
        #
        #     if self._inst is not None:
        #         self._inst.timeout = 3000  # Default timeout

        if result.id in self._shared_memory_setter:
            self._shared_memory[self._shared_memory_setter[result.id]] = 1

        self._log_dev("Established connection to remote server")

    def _tcp_disconnect(self, result: ServiceResponse) -> None:
        self._inst_tm_thread = None
        if result.id in self._shared_memory_setter:
            self._shared_memory[self._shared_memory_setter[result.id]] = 0
        self._log_dev("Closed connection to remote server")

    def _service_preprocessing(self, service_request: ServiceRequest,
                               result: ServiceResponse) -> None:
        """Perform preprocessing of the services.

        Note: This step is useful in case a merge of multiple arguments into
        one unique argument is needed. If the 'command' argument is not
        defined for the service, then no further processing will be done.

        Args:
            service_request: The current service request.
            result: The result to be published.
        """

    def _run_command(self, service_request: ServiceRequest) -> None:
        self._log_dev(f"Received service request: {service_request.id}")

        result = ServiceResponse(id=service_request.id,
                                 type=service_request.type)

        self._service_preprocessing(service_request, result)

        if self._parameter_info[service_request.id].get('key') == '@connect':
            self._tcp_connect(result)
        elif self._parameter_info[service_request.id].get(
                'key') == '@disconnect':
            self._tcp_disconnect(result)
        elif service_request.id in self._shared_memory_getter:
            result.value = self._shared_memory[self._shared_memory_getter[
                service_request.id]]
        elif self._parameter_info[service_request.id].get('command') is None:
            pass
        else:
            send_tcp_tc(
                self._configuration['address'], self._configuration['tc_port'],
                self._parameter_info[service_request.id]['command'].format(
                    *service_request.args), self._eom_q)

        self._context.rx['io_result'].on_next(result)
