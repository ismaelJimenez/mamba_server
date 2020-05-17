""" The Mamba implementation of a Reactive Interface """


class Subject:
    """
    Represents an object that is both an observable sequence as well as an
    observer. Each notification is broadcasted to all subscribed observers.
    """
    def __init__(self):
        super(Subject, self).__init__()
        self._slots = []

    def on_next(self, value=None):
        """
        Notifies all subscribed observers with the value.

        Args:
            value (any): The callable on_next to register.
        """
        for slot in self._slots:
            slot(value)

    def subscribe(self, on_next, filter=None):
        """
        Adds a new observer to the observable.

        Args:
            on_next (callable): The callable on_next to register.
        """
        if not callable(on_next):
            raise ValueError(
                f"Connection to non-callable '{on_next.__class__.__name__}' "
                f"object failed"
            )

        if on_next not in self._slots:
            self._slots.append(on_next)

    def disconnect(self, slot):
        """
        Disconnects the on_next from the signal
        """
        if not callable(slot):
            return

        try:
            self._slots.remove(slot)
        except ValueError:
            pass

    def clear(self):
        """Clears the signal of all connected slots"""
        self._slots = []


class SignalFactory(dict):
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

    def subscribe(self, observable_name, on_next, filter=None):
        """
        Adds a new observer to a given observable. If observable doesnt exists
        yet, it gets created.

        Args:
            observable_name (str): The signal name to connect to.
            on_next (callable): The callable on_next to register.
        """
        if observable_name not in self:
            self.register(observable_name)

        self[observable_name].subscribe(on_next, filter=filter)
