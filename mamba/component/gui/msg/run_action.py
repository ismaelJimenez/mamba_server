################################################################################################
##
##  Copyright (c) Mamba Developers. All rights reserved.
##  Licensed under the MIT License. See License.txt in the project root for license information.
##
################################################################################################

from typing import Dict, Optional, Any


class RunAction:
    def __init__(self,
                 menu_title: str,
                 action_name: str,
                 perspective: Optional[Dict[str, Any]] = None) -> None:
        self.menu_title = menu_title
        self.action_name = action_name
        self.perspective = perspective
