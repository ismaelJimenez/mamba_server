""" Single Port TCP controller base """
from typing import Optional
import os

from stringparser import Parser

from mamba.core.component_base import TcpTmTcCyclic
from mamba.core.context import Context
from mamba.core.msg import ServiceResponse, ParameterType


class ThreadedCyclicTmHandler:
    def __init__(self, sock, eom, shared_memory, rx, log_info,
                 cyclic_tm_mapping, provider):
        half_tm = ''
        while True:
            try:
                # self.request is the TCP socket connected to the client
                data = str(sock.recv(1024), 'utf-8')
                if not data:
                    break

                if half_tm != '':
                    data = half_tm + data

                data_split = data.split(eom)

                if data[-1] != eom:
                    if len(data_split) > 0:
                        half_tm = data_split[-1]
                    else:
                        half_tm = data
                else:
                    half_tm = ''

                data_split = data_split[:-1]

                for raw_cmd in data_split:
                    if '_TC_' in raw_cmd:  # Filter TC echos
                        continue
                    cmd = raw_cmd.split(' ', 1)[1]
                    for key, val in cyclic_tm_mapping.items():
                        try:
                            shared_memory[key] = Parser(val)(cmd)

                            result = ServiceResponse(provider=provider,
                                                     id=key,
                                                     type=ParameterType.get,
                                                     value=shared_memory[key])

                            rx['io_result'].on_next(result)

                        except ValueError:
                            continue

            except OSError:
                break

        log_info('Remote Cyclic TM socket connection has been closed')


class H8823TmTcController(TcpTmTcCyclic):
    """ Simple TCP controller base class """
    def __init__(self,
                 context: Context,
                 local_config: Optional[dict] = None) -> None:
        super().__init__(os.path.dirname(__file__), context, local_config,
                         ThreadedCyclicTmHandler)
