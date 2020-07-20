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

""" Plugin base """

from rx import operators as op

from typing import Optional

from mamba.core.context import Context
from mamba.core.component_base import Component
from mamba.core.exceptions import ComponentConfigException
from mamba.component.gui.msg import RegisterAction, RunAction


class GuiPlugin(Component):
    """ Plugin base class """
    def __init__(self,
                 config_folder: str,
                 context: Context,
                 local_config: Optional[dict] = None) -> None:
        super().__init__(config_folder, context, local_config)

        # Initialize observers
        self._register_observers()

    def _register_observers(self) -> None:
        self._context.rx['run_plugin'].pipe(
            op.filter(lambda value: value.menu_title == self._configuration[
                'menu'] and value.action_name == self._configuration['name'])
        ).subscribe(on_next=self.run)

    def initialize(self) -> None:
        if not all(key in self._configuration for key in ['menu', 'name']):
            raise ComponentConfigException(
                "Missing required elements in component configuration")

        self._context.rx['register_action'].on_next(
            RegisterAction(menu_title=self._configuration['menu'],
                           action_name=self._configuration['name'],
                           shortcut=self._configuration['shortcut']
                           if 'shortcut' in self._configuration else None,
                           status_tip=self._configuration['status_tip']
                           if 'status_tip' in self._configuration else None))

    def run(self, rx_value: RunAction) -> None:
        """ Entry point for running the plugin

            Args:
                rx_value (RunAction): The value published by the subject.
        """
        raise NotImplementedError
