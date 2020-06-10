""" TCP Instrument driver controller base """
from typing import Optional
import socket

from mamba.core.context import Context
from mamba.core.exceptions import ComponentConfigException
from mamba.core.component_base import InstrumentDriver
from mamba.core.msg import ServiceRequest, \
    ServiceResponse, ParameterType, Empty


def tcp_raw_write(sock, message, eom_w, encoding) -> None:
    sock.sendall(bytes(f'{message}{eom_w}', encoding))


def tcp_raw_query(sock, message, eom_w, eom_r, encoding) -> str:
    sock.sendall(bytes(f'{message}{eom_w}', encoding))
    return str(sock.recv(1024), encoding)[:-len(eom_r)]


def tcp_raw_read(sock, eom_r, encoding) -> str:
    return str(sock.recv(1024), encoding)[:-len(eom_r)]


class TcpInstrumentDriver(InstrumentDriver):
    """ VISA Instrument driver controller class """
    def __init__(self,
                 config_folder: str,
                 context: Context,
                 local_config: Optional[dict] = None) -> None:
        super().__init__(config_folder, context, local_config)

        if (self._instrument.port is None and self._instrument.tc_port is None
                and self._instrument.tm_port is None):
            raise ComponentConfigException(
                'Missing port in Instrument Configuration')

    def _instrument_connect(self,
                            result: Optional[ServiceResponse] = None) -> None:
        try:
            self._inst = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self._inst.connect(
                (self._instrument.address, self._instrument.port))
        except ConnectionRefusedError:
            error = 'Instrument is unreachable'
            if result is not None:
                result.type = ParameterType.error
                result.value = error
            self._log_error(error)

    def _instrument_disconnect(self,
                               result: Optional[ServiceResponse] = None
                               ) -> None:
        if self._inst is not None:
            self._inst.close()
            self._inst = None

    def _process_inst_command(self, cmd_type: str, cmd: str,
                              service_request: ServiceRequest,
                              result: ServiceResponse) -> None:
        try:
            if cmd_type == 'query':
                value = tcp_raw_query(self._inst,
                                      cmd.format(*service_request.args),
                                      self._instrument.terminator_write,
                                      self._instrument.terminator_read,
                                      self._instrument.encoding)

                if service_request.type == ParameterType.set:
                    self._shared_memory[self._shared_memory_setter[
                        service_request.id]] = value
                else:
                    result.value = value

            elif cmd_type == 'write':
                tcp_raw_write(self._inst, cmd.format(*service_request.args),
                              self._instrument.terminator_write,
                              self._instrument.encoding)

        except ConnectionRefusedError:
            result.type = ParameterType.error
            result.value = 'Not possible to communicate to the' \
                           ' instrument'
            self._log_error(result.value)
