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

""" The Generic component interface """

import os
import yaml

from typing import Optional

from mamba.core.context import Context
from mamba.core.utils import merge_dicts
from mamba.core.msg import Log, LogLevel

COMPONENT_CONFIG_FILE = "config.yml"


class Component:
    """ The Generic component interface """
    def __init__(self,
                 config_folder: str,
                 context: Context,
                 local_config: Optional[dict] = None) -> None:
        # Retrieve component configuration
        self._context = context

        try:
            with open(os.path.join(config_folder,
                                   COMPONENT_CONFIG_FILE)) as file:
                file_config = yaml.load(file, Loader=yaml.FullLoader)
        except FileNotFoundError:
            file_config = {}

        local_config = local_config or {}

        self._configuration = merge_dicts(local_config, file_config)

        self._name = (self._configuration['name'] if 'name'
                      in self._configuration else '').replace(' ',
                                                              '_').lower()
        self._log_dev = lambda message: self._context.rx['log'].on_next(
            Log(LogLevel.Dev, message, self._name))
        self._log_info = lambda message: self._context.rx['log'].on_next(
            Log(LogLevel.Info, message, self._name))
        self._log_warning = lambda message: self._context.rx['log'].on_next(
            Log(LogLevel.Warning, message, self._name))
        self._log_error = lambda message: self._context.rx['log'].on_next(
            Log(LogLevel.Error, message, self._name))

    def initialize(self) -> None:
        """ Entry point for component initialization """
        pass
