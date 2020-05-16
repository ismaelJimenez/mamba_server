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

    def on_next(self, *args, **kwargs):
        """
        Notifies all subscribed observers with the value.

        Args:
            value (any): The callable on_next to register.
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

        self[observable_name].subscribe(on_next)
