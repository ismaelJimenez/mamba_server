""" The Mamba implementation of a RxPy Reactive Interface """

from rx.subject import Subject
from rx import operators as op


class SignalFactory:
    def __init__(self):
        super(SignalFactory, self).__init__()
        self._factory = {}

    """
    The Subject Factory object lets you handle signals by a string based name
    instead of by objects.
    """
    def register(self, name, *slots):
        """
        Registers a given signal
        :param name: the signal to register
        """
        # setdefault initializes the object even if it exists. This is
        # more efficient
        if name not in self._factory:
            self._factory[name] = Subject()

        for slot in slots:
            self._factory[name].subscribe(slot)

    def deregister(self, name):
        """
        Removes a given signal
        :param name: the signal to deregister
        """
        self._factory.pop(name, None)

    def on_next(self, observable_name, value=None):
        """
        Notifies all subscribed observers of the given observable
        with the value.

        Args:
            observable_name (str): The observable name.
            value (any): The callable on_next to register.
        """
        if observable_name in self._factory:
            self._factory[observable_name].on_next(value)

    def subscribe(self, observable_name, on_next, filter=None):
        """
        Adds a new observer to a given observable. If observable doesnt exists
        yet, it gets created.

        Args:
            observable_name (str): The signal name to connect to.
            on_next (callable): The callable on_next to register.
        """
        if observable_name not in self._factory:
            self.register(observable_name)

        sub = self._factory[observable_name]

        if filter is not None:
            sub = sub.pipe(op.filter(filter))

        sub.subscribe(on_next=on_next)
