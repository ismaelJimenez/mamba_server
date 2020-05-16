""" The Mamba implementation of a RxPy Reactive Interface """

import weakref
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

    def block(self, signals=None, is_blocked=True):
        """
        Sets the block on any provided signals, or to all signals

        :param signals: defaults to all signals. Accepts either a single
        string or a list of strings
        :param is_blocked: the state to set the signal to
        """
        if signals and isinstance(signals, str):
            signals = [signals]

        signals = signals or self.keys()

        for signal in signals:
            if signal not in self:
                raise RuntimeError(
                    "Could not find signal matching {}".format(signal))
            self[signal].block(is_blocked)


class ClassSignalFactory:
    """
    The class signal allows a signal factory to be set on a class rather than
    an instance.
    """
    _map = {}
    _names = set()

    def __get__(self, instance, owner):
        tmp = self._map.setdefault(self, weakref.WeakKeyDictionary())

        signal = tmp.setdefault(instance, SignalFactory())
        for name in self._names:
            signal.register(name)

        return signal

    def __set__(self, instance, value):
        raise RuntimeError("Cannot assign to a Signal object")

    def register(self, name):
        """
        Registers a new signal with the given name
        :param name: The signal to register
        """
        self._names.add(name)
