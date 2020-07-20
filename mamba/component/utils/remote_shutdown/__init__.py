############################################################################
#
# Copyright (c) Mamba Developers. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#
############################################################################

import os
from typing import Optional

from rx import operators as op

from mamba.core.context import Context
from mamba.core.component_base import Component
from mamba.core.msg import ParameterInfo, ParameterType, ServiceRequest, Empty


class RemoteShutdown(Component):
    def __init__(self,
                 context: Context,
                 local_config: Optional[dict] = None) -> None:
        super().__init__(os.path.dirname(__file__), context, local_config)

    def initialize(self) -> None:
        self._context.rx['io_service_signature'].on_next([
            ParameterInfo(provider=self._name,
                          param_id='shutdown',
                          param_type=ParameterType.set,
                          signature=[[], None],
                          description='Shutdown Mamba Server')
        ])

        # Subscribe to the services request
        self._context.rx['io_service_request'].pipe(
            op.filter(lambda value: value.provider == self._name and value.id
                      == 'shutdown' and value.type == ParameterType.set)
        ).subscribe(on_next=self._run_command)

    def _run_command(self, service_request: ServiceRequest) -> None:
        self._log_dev(f"Received service request: {service_request.id}")
        self._context.rx['quit'].on_next(Empty())
