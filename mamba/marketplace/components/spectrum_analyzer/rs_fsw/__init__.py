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

""" R&S FSW Signal and Spectrum Analyzer Controller"""

from typing import Optional
import os
import threading
import pyvisa

from mamba.core.context import Context
from mamba.core.msg import ServiceRequest,\
    ServiceResponse, ParameterType
from mamba.core.component_base import VisaInstrumentDriver


class ThreadedTriggerInHandler:
    def __init__(self, tm_id, _inst, rx, _shared_memory, shared_memory_setter,
                 arg):
        _inst.write('TRIG:SOUR EXT')
        _inst.write('INIT')

        sleep_seconds = float(arg[0]) if len(arg) > 0 else 3

        _inst.timeout = sleep_seconds * 1000

        try:
            _inst.query('*OPC?')  # This waits for trigger
            _shared_memory[shared_memory_setter[tm_id]] = 1
        except pyvisa.errors.VisaIOError:
            pass


class SpectrumAnalyzerRsFsw(VisaInstrumentDriver):
    """ R&S FSW Signal and Spectrum Analyzer Controller class """
    def __init__(self,
                 context: Context,
                 local_config: Optional[dict] = None) -> None:
        super().__init__(os.path.dirname(__file__), context, local_config)

        self._trigger_in_thread: Optional[threading.Thread] = None

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
        if service_request.id == 'trigger_in' and \
                service_request.type == ParameterType.set:
            self._shared_memory[self._shared_memory_setter[
                service_request.id]] = 0

            self._trigger_in_thread = threading.Thread(
                target=ThreadedTriggerInHandler,
                args=(service_request.id, self._inst, self._context.rx,
                      self._shared_memory, self._shared_memory_setter,
                      service_request.args))

            if self._trigger_in_thread is not None:
                self._trigger_in_thread.start()
