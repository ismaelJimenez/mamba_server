""" The Mamba implementation of a RxPy Reactive Interface """

from rx.subject import Subject
from rx import operators as op


class SubjectFactory:
    """ The Subject Factory object lets you handle subjects by a string name
    """
    def __init__(self):
        super(SubjectFactory, self).__init__()
        self._factory = {}

    def register(self, name):
        """ Registers a given subject by name

        Args:
            name (str): Subject name to register.
        """
        if name not in self._factory:
            self._factory[name] = Subject()

    def unregister(self, name):
        """ Unregister a given a given subject by name

        Args:
            name (str): Subject name to remove from the register.
        """
        self._factory.pop(name, None)

    def on_next(self, subject_name, value=None):
        """
        Notifies all subscribed observers of the given observable
        with the value.

        Args:
            subject_name (str): The subject name.
            value (any): The value to send to all subscribed observers.
        """
        if subject_name in self._factory:
            self._factory[subject_name].on_next(value)

    def subscribe(self, subject_name, on_next, op_filter=None):
        """
        Adds a new observer to a given observable by name. If observable
        doesnt exists yet, it gets created.

        Args:
            subject_name (str): The subject name to connect to.
            on_next (callable): Action to invoke.
            op_filter (callable): Filters the elements of an observable
                                  sequence based on a predicate.
        """
        if not callable(on_next):
            raise ValueError(
                f"Subscription of non-callable '{on_next.__class__.__name__}' "
                f"is not possible")

        if subject_name not in self._factory:
            self.register(subject_name)

        sub = self._factory[subject_name]

        if op_filter is not None:
            sub = sub.pipe(op.filter(op_filter))

        sub.subscribe(on_next=on_next)
