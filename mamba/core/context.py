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

"""Application context that is shared between component"""

from typing import Dict, Any

from mamba.core.subject_factory import SubjectFactory


class Context:
    """Application context class"""
    def __init__(self) -> None:
        self._memory: Dict[str, Any] = {}
        self.rx = SubjectFactory()

    def get(self, parameter: str) -> Any:
        """Returns the value of a context parameter, or None if it
        doesn´t exists.

        Args:
            parameter: Identifier of the parameter.

        Returns:
           The parameter value. None if parameter does not exists in context.
        """
        return self._memory.get(parameter)

    def set(self, parameter: str, value: Any) -> None:
        """Set the value of a context parameter. If already exists, value is
        overwritten.

        Args:
            parameter: Identifier of the parameter.
            value: New parameter value.
        """
        self._memory[parameter] = value
