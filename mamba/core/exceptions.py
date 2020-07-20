################################################################################################
##
##  Copyright (c) Mamba Developers. All rights reserved.
##  Licensed under the MIT License. See License.txt in the project root for license information.
##
################################################################################################

# Mamba exceptions

from typing import Optional


class ComponentConfigException(Exception):
    def __init__(self, msg: Optional[str] = None) -> None:
        super(ComponentConfigException,
              self).__init__(msg or "Component configuration error")


class ComposeFileException(Exception):
    def __init__(self, msg: Optional[str] = None) -> None:
        super(ComposeFileException,
              self).__init__(msg or "Launch file configuration error")
