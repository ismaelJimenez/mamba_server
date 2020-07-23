############################################################################
#
# Copyright (c) Mamba Developers. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#
############################################################################
""" Script controller base """

from typing import Optional
import os
import sys
from subprocess import check_output, CalledProcessError

from tempfile import TemporaryFile

from mamba.core.context import Context
from mamba.core.exceptions import ComponentConfigException
from mamba.core.component_base import InstrumentDriver
from mamba.core.msg import ServiceRequest, \
    ServiceResponse, ParameterType


def _get_out(args):
    with TemporaryFile() as t:
        try:
            out = check_output(args, stderr=t)
            return 0, out
        except CalledProcessError as e:
            t.seek(0)
            return e.returncode, t.read()


class ScriptInstrumentDriver(InstrumentDriver):
    """ Script Instrument driver controller class """
    def __init__(self,
                 context: Context,
                 local_config: Optional[dict] = None) -> None:
        super().__init__(os.path.dirname(__file__), context, local_config)

    def initialize(self) -> None:
        super().initialize()
        self._inst = 0

    def _process_inst_command(self, cmd_type: str, cmd: str,
                              service_request: ServiceRequest,
                              result: ServiceResponse) -> None:

        self._log_dev(cmd.format(*service_request.args))

        if cmd_type == 'query':
            value = eval(cmd.format(*service_request.args))

            if service_request.type == ParameterType.set:
                self._shared_memory[self._shared_memory_setter[
                    service_request.id]] = value
            else:
                result.value = value

        elif cmd_type == 'write':
            eval(cmd.format(*service_request.args))

        elif cmd_type == 'python_script' or cmd_type == 'bash_script':
            script_cmd = None

            if cmd_type == 'bash_script':
                script_cmd = '/bin/bash'
            elif cmd_type == 'python_script':
                script_cmd = sys.executable
            else:
                result.type = ParameterType.error
                result.value = f'Unrecognized command type'

            if script_cmd is not None:
                (code, output) = _get_out([
                            script_cmd
                        ] + cmd.format(*service_request.args).split(' '))

                output = output.decode('utf-8')

                if service_request.type == ParameterType.set:
                    if code != 0:
                        result.type = ParameterType.error
                        result.value = f'Return code {code}'

                    self._shared_memory[self._shared_memory_setter[
                        service_request.id]] = output
                else:
                    result.value = output
