#############################################################################
##
## Copyright (C) 2020 The Mamba Company.
## Contact: themambacompany@gmail.com
##
## This file is part of Mamba Server.
##
## $MAMBA_BEGIN_LICENSE:LGPL$
## Commercial License Usage
## Licensees holding valid commercial Mamba licenses may use this file in
## accordance with the commercial license agreement provided with the
## Software or, alternatively, in accordance with the terms contained in
## a written agreement between you and The Mamba Company. For licensing terms
## and conditions see LICENSE. For further information contact us at
## themambacompany@gmail.com.
##
## GNU Lesser General Public License Usage
## Alternatively, this file may be used under the terms of the GNU Lesser
## General Public License version 3 as published by the Free Software
## Foundation and appearing in the file LICENSE.LGPL3 included in the
## packaging of this file. Please review the following information to
## ensure the GNU Lesser General Public License version 3 requirements
## will be met: https://www.gnu.org/licenses/lgpl-3.0.html.
##
## GNU General Public License Usage
## Alternatively, this file may be used under the terms of the GNU
## General Public License version 2.0 or (at your option) the GNU General
## Public license version 3 or any later version approved by the KDE Free
## Qt Foundation. The licenses are as published by the Free Software
## Foundation and appearing in the file LICENSE.GPL2 and LICENSE.GPL3
## included in the packaging of this file. Please review the following
## information to ensure the GNU General Public License requirements will
## be met: https://www.gnu.org/licenses/gpl-2.0.html and
## https://www.gnu.org/licenses/gpl-3.0.html.
##
## $MAMBA_END_LICENSE$
##
#############################################################################

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