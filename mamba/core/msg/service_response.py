############################################################################
#
# Copyright (c) Mamba Developers. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#
############################################################################

from typing import Optional, Any


class ServiceResponse:
    def __init__(self,
                 id: str,
                 provider: Optional[str] = None,
                 value: Optional[Any] = None,
                 type: Optional[Any] = None):
        self.id = id
        self.provider = provider
        self.value = value
        self.type = type
