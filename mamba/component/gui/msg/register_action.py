############################################################################
#
# Copyright (c) Mamba Developers. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#
############################################################################

from typing import Optional


class RegisterAction:
    def __init__(self,
                 menu_title: str,
                 action_name: str,
                 shortcut: Optional[str] = None,
                 status_tip: str = '') -> None:
        self.menu_title = menu_title
        self.action_name = action_name
        self.shortcut = shortcut
        self.status_tip = status_tip
