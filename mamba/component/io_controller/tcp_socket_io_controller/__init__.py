""" TCP controller base """
from typing import Optional, Dict, Union
import os
import threading
import socket

from rx import operators as op

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
                                             type='tm',
                                             value=cmd[1])

                    rx['io_result'].on_next(result)

            log_info('Remote socket connection has been closed')


def send_tcp_tc(HOST, PORT, message, eom):
    # Create a socket (SOCK_STREAM means a TCP socket)
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        # Connect to server and send data
        sock.connect((HOST, PORT))
        sock.sendall(bytes(message + eom, "utf-8"))


class TcpControllerBase(ComponentBase):
    """ TCP controller base class """
    def __init__(self,
                 context: Context,
                 local_config: Optional[dict] = None) -> None:
        super(TcpControllerBase, self).__init__(os.path.dirname(__file__),
                                                context, local_config)

        # Initialize observers
        self._register_observers()

        # Defined custom variables
        self._shared_memory: Dict[str, Union[str, int, float]] = {}
        self._shared_memory_getter: Dict[str, str] = {}
        self._shared_memory_setter: Dict[str, str] = {}
        self._service_info: Dict[str, dict] = {}
        # self._inst_tm = None
        self._inst_tm_thread: Optional[threading.Thread] = None
        # self._inst_tc = None

        self._eom_q = self._configuration['eom']['TCPIP INSTR']['q']
        self._eom_r = self._configuration['eom']['TCPIP INSTR']['r']

    def _register_observers(self) -> None:
        """ Entry point for registering component observers """

        # Quit is sent to command App finalization
        self._context.rx['quit'].pipe(
            op.filter(lambda value: isinstance(value, Empty))).subscribe(
                on_next=self._close)

    def _close(self, rx_value: Empty) -> None:
        """ Entry point for closing application

            Args:
                rx_value: The value published by the subject.
        """

    #     if self._inst is not None:
    #         self._inst.close()
    #         self._inst = None
    #
    # def _tcp_sim_file_validation(self) -> None:
    #     if self._configuration.get('tcp-sim') is not None:
    #         if os.path.exists(self._configuration['tcp-sim']):
    #             self._simulation_file = self._configuration['tcp-sim']
    #         elif os.path.exists(
    #                 os.path.join(
    #                     self._context.get('mamba_dir'),
    #                     path_from_string(self._configuration['tcp-sim']))):
    #             self._simulation_file = os.path.join(
    #                 self._context.get('mamba_dir'),
    #                 path_from_string(self._configuration['tcp-sim']))
    #         else:
    #             raise ComponentConfigException(
    #                 'Tcp-sim file has not been found')
    #
    def _topics_format_validation(self) -> None:
        if not isinstance(self._configuration.get('topics'), dict):
            raise ComponentConfigException(
                'Topics configuration: wrong format')

    def initialize(self) -> None:
        """ Entry point for component initialization """

        self._topics_format_validation()
        #    self._tcp_sim_file_validation()
        #
        for key, service_data in self._configuration['topics'].items():
            # Create new service signature dictionary
            service_dict = {
                'description': service_data.get('description') or '',
                'signature': service_data.get('signature') or [[], None],
                'command': service_data.get('command'),
                'key': service_data.get('key'),
            }

            if not isinstance(service_dict['signature'], list) or len(
                    service_dict['signature']) != 2 or not isinstance(
                        service_dict['signature'][0], list):
                raise ComponentConfigException(
                    f'Signature of service "{key}" is invalid. Format shall'
                    f' be [[arg_1, arg_2, ...], return_type]')

            # Add new service to the component services dictionary
            self._service_info[key] = service_dict

        # Compose services signature to be published
        services_sig = {
            key: {
                'description': value['description'],
                'signature': value['signature']
            }
            for key, value in self._service_info.items()
        }

        io_signatures = {'provider': self._name, 'services': services_sig}

        # Compose shared memory data dictionaries
        if 'parameters' in self._configuration:
            for key, service_data in self._configuration['parameters'].items():
                # Initialize shared memory with given value, if any
                self._shared_memory[key] = service_data.get('default')

                # Compose dict assigning each getter with his memory slot
                if 'getter' in service_data:
                    for getter, value in service_data['getter'].items():
                        self._shared_memory_getter[key] = getter

                # Compose dict assigning each setter with his memory slot
                if 'setter' in service_data:
                    for setter, value in service_data['setter'].items():
                        self._shared_memory_setter[setter] = key

        # Publish services signature
        self._context.rx['io_service_signature'].on_next(io_signatures)

        # Subscribe to the services request
        self._context.rx['io_service_request'].pipe(
            op.filter(lambda value: isinstance(value, ServiceRequest) and
                      (value.id in self._service_info))).subscribe(
                          on_next=self._run_command)

    def _tcp_connect(self, result: ServiceResponse) -> None:

        self._inst_tm_thread = threading.Thread(
            target=ThreadedTmHandler,
            args=(self._configuration['resource-name'],
                  self._configuration['tm_port'], self._eom_r,
                  self._shared_memory, self._context.rx, self._log_info,
                  self._shared_memory_getter))

        self._inst_tm_thread.start()

        #     if self._configuration.get('tcp-sim'):
        #         self._inst = pytcp.ResourceManager(
        #             f"{self._simulation_file}@sim").open_resource(
        #                 self._configuration['resource-name'],
        #                 read_termination='\n')
        #     else:
        #         try:
        #             self._inst = pytcp.ResourceManager().open_resource(
        #                 self._configuration['resource-name'],
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

        if self._service_info[service_request.id].get('key') == '@connect':
            self._tcp_connect(result)
        elif self._service_info[service_request.id].get(
                'key') == '@disconnect':
            self._tcp_disconnect(result)
        elif service_request.id in self._shared_memory_getter:
            result.value = self._shared_memory[self._shared_memory_getter[
                service_request.id]]
        elif self._service_info[service_request.id].get('command') is None:
            pass
        else:
            send_tcp_tc(
                self._configuration['resource-name'],
                self._configuration['tc_port'],
                self._service_info[service_request.id]['command'].format(
                    *service_request.args), self._eom_q)

        self._context.rx['io_result'].on_next(result)
