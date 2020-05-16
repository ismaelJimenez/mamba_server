""" The Mamba implementation of a Reactive Interface """

import inspect
import weakref
from functools import partial


class Signal:
    """
    The Signal is the core object that handles connection and emission .
    """
    def __init__(self):
        super(Signal, self).__init__()
        self._block = False
        self._slots = []

    def emit(self, *args, **kwargs):
        """
        Calls all the connected slots with the provided args and kwargs
        unless block is activated
        """

        if self._block:
            return

        for slot in self._slots:
            if not slot:
                continue

            if isinstance(slot, partial):
                slot()
            elif isinstance(slot, weakref.WeakKeyDictionary):
                # For class methods, get the class object and call the
                # method accordingly.
                for obj, method in slot.items():
                    method(obj, *args, **kwargs)
            elif isinstance(slot, weakref.ref):
                # If it's a weakref, call the ref to get the instance and
                # then call the func
                # Don't wrap in try/except so we don't risk masking exceptions
                # from the actual func call
                if slot() is not None:
                    slot()(*args, **kwargs)
            else:
                # Else call it in a standard way. Should be just lambdas
                # at this point
                slot(*args, **kwargs)

    def subscribe(self, on_next):
        """
        Adds a new observer to the observable.

        Args:
            on_next (callable): The callable on_next to register.
        """
        if not callable(on_next):
            raise ValueError(
                "Connection to non-callable '{}' object failed".format(
                    on_next.__class__.__name__))

        if isinstance(on_next, partial) or '<' in on_next.__name__:
            # If it's a partial or a lambda. The '<' check is the only py2
            # and py3 compatible way I could find
            if on_next not in self._slots:
                self._slots.append(on_next)
        elif inspect.ismethod(on_next):
            # Check if it's an instance method and store it with the instance
            # as the key
            slot_self = on_next.__self__
            slot_dict = weakref.WeakKeyDictionary()
            slot_dict[slot_self] = on_next.__func__
            if slot_dict not in self._slots:
                self._slots.append(slot_dict)
        else:
            # If it's just a function then just store it as a weakref.
            new_slot_ref = weakref.ref(on_next)
            if new_slot_ref not in self._slots:
                self._slots.append(new_slot_ref)

    def disconnect(self, slot):
        """
        Disconnects the on_next from the signal
        """
        if not callable(slot):
            return

        if inspect.ismethod(slot):
            # If it's a method, then find it by its instance
            slot_self = slot.__self__
            for current_slot in self._slots:
                if isinstance(current_slot, weakref.WeakKeyDictionary) and (
                        slot_self in current_slot) and (current_slot[slot_self]
                                                        is slot.__func__):
                    self._slots.remove(current_slot)
                    break
        elif isinstance(slot, partial) or '<' in slot.__name__:
            # If it's a partial or lambda, try to remove directly
            try:
                self._slots.remove(slot)
            except ValueError:
                pass
        else:
            # It's probably a function, so try to remove by weakref
            try:
                self._slots.remove(weakref.ref(slot))
            except ValueError:
                pass

    def clear(self):
        """Clears the signal of all connected slots"""
        self._slots = []

    def block(self, is_blocked):
        """Sets blocking of the signal"""
        self._block = bool(is_blocked)


class ClassSignal:
    """
    The class signal allows a signal to be set on a class rather than
    an instance. This emulates the behavior of a PyQt signal
    """
    _map = {}

    def __get__(self, instance, owner):
        tmp = self._map.setdefault(self, weakref.WeakKeyDictionary())
        return tmp.setdefault(instance, Signal())

    def __set__(self, instance, value):
        raise RuntimeError("Cannot assign to a Signal object")


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
            self[name] = Signal()

        for slot in slots:
            self[name].subscribe(slot)

    def deregister(self, name):
        """
        Removes a given signal
        :param name: the signal to deregister
        """
        self.pop(name, None)

    def emit(self, signal_name, *args, **kwargs):
        """
        Emits a signal by name if it exists. Any additional args or kwargs are
        passed to the signal
        :param signal_name: the signal name to emit
        """
        assert signal_name in self, "{} is not a registered signal".format(
            signal_name)
        self[signal_name].emit(*args, **kwargs)

    def subscribe(self, observable_name, on_next):
        """
        Adds a new observer to a given observable. If observable doesnt exists
        yet, it gets created.

        Args:
            observable_name (str): The signal name to connect to.
            on_next (callable): The callable on_next to register.
        """
        if observable_name not in self:
            self.register(observable_name, on_next)

        self[observable_name].subscribe(on_next)

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
