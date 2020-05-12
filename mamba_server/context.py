"""Application context that is shared between components"""


class Context:
    """Application context class"""
    def __init__(self):
        self._memory = {}

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
