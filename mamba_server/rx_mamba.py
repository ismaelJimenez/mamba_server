""" The Mamba implementation of a Minimal Reactive Interface """


class Subject:
    """
    Represents an object that is both an observable sequence as well as an
    observer. Each notification is broadcasted to all subscribed observers.
    """
    def __init__(self):
        super(Subject, self).__init__()
        self._subscriptions = []

    def on_next(self, value=None):
        """
        Notifies all subscribed observers with the value.

        Args:
            value (any): The value to send to all subscribed observers.
        """
        for subscription in self._subscriptions:
            subscription['on_next'](value)

    def subscribe(self, on_next, op_filter=None):
        """
        Subscribe an observer to the observable sequence.

        Args:
            on_next (callable): Action to invoke.
            op_filter (callable): Filters the elements of an observable
                                  sequence based on a predicate.
        """
        if not callable(on_next):
            raise ValueError(
                f"Connection to non-callable '{on_next.__class__.__name__}' "
                f"object failed")

        if not any(subscription['on_next'] == on_next
                   for subscription in self._subscriptions):
            self._subscriptions.append({
                'on_next': on_next,
                'op_filter': op_filter
            })

    def disconnect(self, on_next):
        """
        Disconnects an action from the observable sequence.

        Args:
            on_next (callable): Action to disconnect from the
                                observable sequence.
        """
        if not callable(on_next):
            return

        try:
            for i, o in enumerate(self._subscriptions):
                if o['on_next'] == on_next:
                    del self._subscriptions[i]
                    break
        except ValueError:
            pass

    def dispose(self):
        """ Unsubscribe all observers and release resources """
        self._subscriptions = []


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

    def subscribe(self, observable_name, on_next, op_filter=None):
        """
        Adds a new observer to a given observable by name. If observable
        doesnt exists yet, it gets created.

        Args:
            observable_name (str): The subject name to connect to.
            on_next (callable): Action to invoke.
            op_filter (callable): Filters the elements of an observable
                                  sequence based on a predicate.
        """
        if observable_name not in self._factory:
            self.register(observable_name)

        self._factory[observable_name].subscribe(on_next, op_filter=op_filter)
