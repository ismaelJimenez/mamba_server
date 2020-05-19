"""Application context that is shared between components"""

from mamba_server.rx_mamba import SubjectFactory
from mamba_server.rx_py import SubjectFactoryRxPy
from mamba_server.exceptions import ComponentConfigException


class Context:
    """Application context class"""
    def __init__(self, implementation='mamba'):
        self._memory = {}
        if implementation == 'mamba':
            self.rx = SubjectFactory()
        elif implementation == 'rxpy':
            self.rx = SubjectFactoryRxPy()
        else:
            raise ComponentConfigException(f"Rx implementation "
                                           f"'{implementation}' "
                                           f"not valid")

    def get(self, parameter):
        """Returns the value of a context parameter, or None if it
        doesn´t exists.

        Args:
            parameter (str): String identifier of the parameter.

        Returns:
           The parameter value. None if parameter does not exists in context.
        """
        if parameter in self._memory:
            return self._memory[parameter]

        return None

    def set(self, parameter, value):
        """Set the value of a context parameter. If already exists, value is
        overwritten.

        Args:
            parameter (str): String identifier of the parameter.
            value: New parameter value.
        """
        self._memory[parameter] = value
