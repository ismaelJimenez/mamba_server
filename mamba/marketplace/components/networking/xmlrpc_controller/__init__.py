############################################################################
#
# Copyright (c) Mamba Developers. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#
############################################################################
""" Single Port TCP controller base """

from typing import Optional
import os

from mamba.core.component_base import XmlRpcInstrumentDriver
from mamba.core.context import Context


class XmlRpcController(XmlRpcInstrumentDriver):
    """ Simple TCP controller base class """
    def __init__(self,
                 context: Context,
                 local_config: Optional[dict] = None) -> None:
        super().__init__(os.path.dirname(__file__), context, local_config)
