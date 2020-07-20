############################################################################
#
# Copyright (c) Mamba Developers. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#
############################################################################

from typing import List, Any, Optional
from mamba.core.msg.parameter_info import ParameterType


class ServiceRequest:
    def __init__(self,
                 id: str,
                 type: ParameterType,
                 provider: Optional[str] = None,
                 args: List[Any] = []) -> None:
        self.id = id
        self.provider = provider
        self.type = type
        self.args = args
