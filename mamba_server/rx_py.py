""" The Mamba implementation of a RxPy Reactive Interface """

from rx.subject import Subject


class SignalFactory(dict):
    """
    The Signal Factory object lets you handle signals by a string based name
    instead of by objects.
    """
    def register(self, name, *slots):
        """
        Registers a given signal
        :param name: the signal to register
        """
        # setdefault initializes the object even if it exists. This is
        # more efficient
        if name not in self:
            self[name] = Subject()

        for slot in slots:
            self[name].subscribe(slot)

    def deregister(self, name):
        """
        Removes a given signal
        :param name: the signal to deregister
        """
        self.pop(name, None)

    def on_next(self, observable_name, value=None):
        """
        Notifies all subscribed observers of the given observable
        with the value.

        Args:
            observable_name (str): The observable name.
            value (any): The callable on_next to register.
        """
        if observable_name in self:
            self[observable_name].on_next(value)

    def subscribe(self, observable_name, on_next):
        """
        Adds a new observer to a given observable. If observable doesnt exists
        yet, it gets created.

        Args:
            observable_name (str): The signal name to connect to.
            on_next (callable): The callable on_next to register.
        """
        if observable_name not in self:
            self.register(observable_name)

        self[observable_name].subscribe(on_next=on_next)
