################################################################################################
##
##  Copyright (c) Mamba Developers. All rights reserved.
##  Licensed under the MIT License. See License.txt in the project root for license information.
##
################################################################################################

""" Script controller base """

from typing import Optional
import os
import sys
import subprocess
import tempfile

from mamba.core.context import Context
from mamba.core.exceptions import ComponentConfigException
from mamba.core.component_base import InstrumentDriver
from mamba.core.msg import ServiceRequest, \
    ServiceResponse, ParameterType


class ScriptInstrumentDriver(InstrumentDriver):
    """ Script Instrument driver controller class """
    def __init__(self,
                 context: Context,
                 local_config: Optional[dict] = None) -> None:
        super().__init__(os.path.dirname(__file__), context, local_config)

        if self._configuration.get('source_folder') is None:
            raise ComponentConfigException(
                'Missing Source Folder in Script Controller Configuration')

        self._scripts_folder = None
        if self._configuration.get('source_folder',
                                   {}).get('global') is not None:
            self._scripts_folder = self._configuration.get(
                'source_folder', {}).get('global')
        elif self._configuration.get('source_folder',
                                     {}).get('local') is not None:
            self._scripts_folder = os.path.join(
                os.path.dirname(__file__),
                self._configuration.get('source_folder', {}).get('local'))

    def initialize(self) -> None:
        super().initialize()
        self._inst = 0

    def _process_inst_command(self, cmd_type: str, cmd: str,
                              service_request: ServiceRequest,
                              result: ServiceResponse) -> None:
        script_state = 1

        if cmd_type == 'script':
            arguments = service_request.args[0].split(' ')
            if cmd.get('type') == 'python':
                if cmd.get('command') is None:
                    with tempfile.TemporaryFile() as out:
                        script_state = subprocess.call([
                            sys.executable,
                            os.path.join(self._scripts_folder, arguments[0])
                        ] + arguments[1:],
                                                       stdout=out,
                                                       stderr=out)
                else:
                    with tempfile.TemporaryFile() as out:
                        script_state = subprocess.call([
                            sys.executable,
                            os.path.join(self._scripts_folder,
                                         cmd.get('command'))
                        ] + arguments,
                                                       stdout=out,
                                                       stderr=out)
            elif cmd.get('type') == 'bash':
                if cmd.get('command') is None:
                    with tempfile.TemporaryFile() as out:
                        script_state = subprocess.call([
                            '/bin/bash',
                            os.path.join(self._scripts_folder, arguments[0])
                        ] + arguments[1:],
                                                       stdout=out,
                                                       stderr=out)
                else:
                    with tempfile.TemporaryFile() as out:
                        script_state = subprocess.call([
                            '/bin/bash',
                            os.path.join(self._scripts_folder,
                                         cmd.get('command'))
                        ] + arguments,
                                                       stdout=out,
                                                       stderr=out)
            else:
                raise ComponentConfigException('Unrecognized script type')

        if script_state != 0:
            result.type = ParameterType.error
            result.value = 'Script execution error.'
            self._log_error(result.value)
