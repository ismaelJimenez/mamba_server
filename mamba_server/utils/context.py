class Context:
    _memory = {}

    def get(self, parameter):
        if parameter in self._memory:
            return self._memory[parameter]
        else:
            return None

    def set(self, parameter, value):
        self._memory[parameter] = value

