""" The Mamba implementation of a RxPy Reactive Interface """

from rx.subject import Subject


class SubjectFactory:
    """ The Subject Factory object lets you handle subjects by a string name
    """
    def __init__(self):
        super(SubjectFactory, self).__init__()
        self._factory = {}

    def __getitem__(self, key):
        """ Registers a given subject by name
            Note: It creates an empty one if it does not exists
        Args:
            key (str): Subject key to register.
        """
        if key not in self._factory:
            self._factory[key] = Subject()

        return self._factory[key]
