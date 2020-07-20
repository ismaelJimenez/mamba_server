################################################################################################
##
##  Copyright (c) Mamba Developers. All rights reserved.
##  Licensed under the MIT License. See License.txt in the project root for license information.
##
################################################################################################

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
