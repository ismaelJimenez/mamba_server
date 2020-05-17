""" Rx_Mamba Subject Factory tests """

import pytest
from functools import partial

from mamba_server.rx_mamba import Subject, SubjectFactory


class DummyObservableClass:
    """ A dummy class to check for on_next handling """
    check_val = None
    func_call_count = 0
    check_val_2 = None
    func_call_count_2 = 0

    def set_val(self, val):
        """ A method to test on_next calls with """
        self.check_val = val
        self.func_call_count += 1

    def set_val_2(self, val):
        """ A method to test on_next calls with """
        self.check_val_2 = val
        self.func_call_count_2 += 1


def dummy_test_func(test):
    """A test standalone function for subjects to attach onto"""
    test.check_val = 12345
    test.func_call_count += 1


class TestClassSignal:
    def setup_method(self):
        """ setup_method called for every method """
        self.check_val = None  # A state check for the tests
        self.func_call_count = 0  # A state check for test function

    def test_subject_function_connect(self):
        """ Test subscribing standalone functions to subjects """
        subject = Subject()
        subject.subscribe(dummy_test_func)
        assert len(subject._subscriptions) == 1

    def test_subject_function_subscribe_duplicate(self):
        """ Test subscribing duplicate standalone functions to subjects """
        subject = Subject()
        subject.subscribe(dummy_test_func)
        subject.subscribe(dummy_test_func)
        assert len(subject._subscriptions) == 1

    def test_subject_partial_subscribe(self):
        """ Test subscribing partial functions to subjects """
        subject = Subject()
        subject.subscribe(partial(dummy_test_func, self, 'Partial'))
        assert len(subject._subscriptions) == 1

    def test_subject_partial_subscribe_duplicate(self):
        """ Test subscribing duplicate partial functions to subjects """
        subject = Subject()
        func = partial(dummy_test_func, self, 'Partial')
        subject.subscribe(func)
        subject.subscribe(func)
        assert len(subject._subscriptions) == 1

    def test_subject_lambda_subscribe(self):
        """ Test subscribing lambda functions to subjects """
        subject = Subject()
        subject.subscribe(lambda value: dummy_test_func(self, value))
        assert len(subject._subscriptions) == 1

    def test_subject_lambda_subscribe_duplicate(self):
        """ Test subscribing duplicate lambda functions to subjects """
        subject = Subject()
        func = lambda value: dummy_test_func(self, value)
        subject.subscribe(func)
        subject.subscribe(func)
        assert len(subject._subscriptions) == 1

    def test_subject_method_subscribe(self):
        """ Test subscribing class instance methods to subjects """
        subject = Subject()
        dummy_class = DummyObservableClass()
        subject.subscribe(dummy_class.set_val)
        assert len(subject._subscriptions) == 1

    def test_subject_method_subscribe_duplicate(self):
        """ Test subscribing duplicate class instance methods to subjects """
        subject = Subject()
        dummy_class = DummyObservableClass()
        subject.subscribe(dummy_class.set_val)
        subject.subscribe(dummy_class.set_val)
        assert len(subject._subscriptions) == 1

    def test_subject_method_subscribe_different_instances(self):
        """ Test subscribing class methods from different instances
         to subjects """
        subject = Subject()
        dummy_class_1 = DummyObservableClass()
        dummy_class_2 = DummyObservableClass()
        subject.subscribe(dummy_class_1.set_val)
        subject.subscribe(dummy_class_2.set_val)
        assert len(subject._subscriptions) == 2

    def test_subject_subscribe_non_callable(self):
        """ Test subscribing non-callable object to subjects """
        subject = Subject()
        with pytest.raises(ValueError) as excinfo:
            subject.subscribe('string')

        assert "Subscription of non-callable 'str' is not possible" in str(
            excinfo.value)

        with pytest.raises(ValueError) as excinfo:
            subject.subscribe(None)

        assert "Subscription of non-callable 'NoneType' is not possible" in str(
            excinfo.value)

    def test_subject_on_next_to_function(self):
        """ Test notification to standalone function observables """
        subject = Subject()
        subject.subscribe(dummy_test_func)
        subject.on_next(self)
        assert self.check_val == 12345
        assert self.func_call_count == 1

    def test_subject_on_next_to_lambda(self):
        """ Test notification to lambda function observables """
        subject = Subject()
        subject.subscribe(lambda _: dummy_test_func(self))
        subject.on_next()
        assert self.check_val == 12345
        assert self.func_call_count == 1

    def test_subject_on_next_to_instance_method(self):
        """ Test notification to class instance method observables """
        subject = Subject()
        dummy_class = DummyObservableClass()
        subject.subscribe(dummy_class.set_val)
        subject.on_next('ClassMethod')
        assert dummy_class.check_val == 'ClassMethod'
        assert dummy_class.func_call_count == 1

    def test_subject_on_next_to_method_on_deleted_instance(self):
        """ Test notification to deleted instance method """
        subject = Subject()
        dummy_class = DummyObservableClass()
        subject.subscribe(dummy_class.set_val)
        subject.subscribe(lambda _: dummy_test_func(self))
        del dummy_class
        subject.on_next()
        assert self.check_val == 12345
        assert self.func_call_count == 1

    def test_subject_on_next_to_method_filter(self):
        """ Test notification with applied filter to observables """
        subject = Subject()
        dummy_observable_class = DummyObservableClass()
        subject.subscribe(dummy_observable_class.set_val,
                          op_filter=lambda value: value % 2 == 0)
        subject.subscribe(dummy_observable_class.set_val_2)
        subject.on_next(1)
        assert dummy_observable_class.check_val is None
        assert dummy_observable_class.func_call_count == 0
        assert dummy_observable_class.check_val_2 == 1
        assert dummy_observable_class.func_call_count_2 == 1

    def test_subject_function_unsubscribe(self):
        """ Test unsubscribe a function from observables """
        def local_func(test):
            test.check_val = 2345
            test.func_call_count += 1

        subject = Subject()
        subject.subscribe(dummy_test_func)
        subject.subscribe(local_func)
        subject.unsubscribe(dummy_test_func)
        subject.on_next(self)
        assert len(subject._subscriptions) == 1
        assert self.check_val == 2345
        assert self.func_call_count == 1

    def test_subject_function_unsubscribe_unconnected(self):
        """ Test unsubscribe an unconnected function from observables """
        subject = Subject()
        try:
            subject.unsubscribe(dummy_test_func)
        except:
            pytest.fail("Unsubscribe non-existing function should not raise")

    def test_subject_partial_unsubscribe(self):
        """ Test unsubscribe a partial function from observables """
        subject = Subject()
        part = partial(dummy_test_func, self, 'Partial')
        subject.subscribe(part)
        subject.unsubscribe(part)
        assert self.check_val is None

    def test_subject_partial_unsubscribe_unconnected(self):
        """ Test unsubscribe an unconnected partial function from observables
        """
        subject = Subject()
        part = partial(dummy_test_func, self, 'Partial')
        try:
            subject.unsubscribe(part)
        except:
            pytest.fail(
                "Unsubscribe non-existing partial function should not raise")

    def test_subject_lambda_unsubscribe(self):
        """ Test unsubscribe a lambda function from observables """
        subject = Subject()
        func = lambda value: dummy_test_func(self, value)
        subject.subscribe(func)
        subject.unsubscribe(func)
        assert len(subject._subscriptions) == 0

    def test_subject_lambda_unsubscribe_unconnected(self):
        """ Test unsubscribe an unconnected lambda function from observables
        """
        subject = Subject()
        func = lambda value: dummy_test_func(self, value)
        try:
            subject.unsubscribe(func)
        except:
            pytest.fail(
                "Unsubscribe non-existing lambda function should not raise")

    def test_subject_unsubscribe_non_callable(self):
        """ Test unsubscribe a non-callable from observables """
        subject = Subject()
        try:
            subject.unsubscribe('string')
        except:
            pytest.fail("Unsubscribe non-callable should not raise")

    def test_subject_dispose(self):
        """ Test unsubscribe all observers and release resources """
        subject = Subject()
        subject.subscribe(lambda value: self.setVal(value))
        subject.subscribe(dummy_test_func)
        assert len(subject._subscriptions) == 2
        subject.dispose()
        assert len(subject._subscriptions) == 0


class TestClassSignalFactory:
    def test_subject_factory_register(self):
        """ Test new subject registration """
        dummy_subject_factory = SubjectFactory()
        dummy_observable_class = DummyObservableClass()
        dummy_subject_factory.register('TestSubject')
        dummy_subject_factory.subscribe('TestSubject',
                                        dummy_observable_class.set_val)
        dummy_subject_factory.on_next('TestSubject', 1)
        assert dummy_observable_class.check_val == 1
        assert dummy_observable_class.func_call_count == 1

    def test_subject_factory_subscribe_to_non_existing_subject(self):
        """ Test SubjectFactory subscribing to non existing subject """
        dummy_subject_factory = SubjectFactory()
        dummy_observable_class = DummyObservableClass()
        dummy_subject_factory.subscribe('TestSubject',
                                        dummy_observable_class.set_val)
        dummy_subject_factory.on_next('TestSubject', 1)
        assert dummy_observable_class.check_val == 1
        assert dummy_observable_class.func_call_count == 1

    def test_subject_factory_subscribe_non_callable(self):
        """ Test subscribing non-callable object to subjects """
        dummy_subject_factory = SubjectFactory()
        with pytest.raises(ValueError) as excinfo:
            dummy_subject_factory.subscribe('TestSubject', 'string')

        assert "Subscription of non-callable 'str' is not possible" in str(
            excinfo.value)

    def test_subject_factory_subscribe_on_next(self):
        """ Test notification to all subscribed observers """
        dummy_subject_factory = SubjectFactory()
        dummy_observable_class = DummyObservableClass()
        dummy_subject_factory.register('TestSubject')
        dummy_subject_factory.subscribe('TestSubject',
                                        dummy_observable_class.set_val)
        dummy_subject_factory.on_next('TestSubject', 1)
        assert dummy_observable_class.check_val == 1
        assert dummy_observable_class.func_call_count == 1

    def test_subject_factory_subscribe_filter(self):
        """ Test notification to all subscribed observers using filters """
        dummy_subject_factory = SubjectFactory()
        dummy_observable_class = DummyObservableClass()
        dummy_subject_factory.subscribe(subject_name='TestSubject',
                                        on_next=dummy_observable_class.set_val,
                                        op_filter=lambda value: value % 2 == 0)
        dummy_subject_factory.subscribe(
            subject_name='TestSubject',
            on_next=dummy_observable_class.set_val_2)

        dummy_subject_factory.on_next('TestSubject', 1)
        assert dummy_observable_class.check_val is None
        assert dummy_observable_class.func_call_count == 0
        assert dummy_observable_class.check_val_2 == 1
        assert dummy_observable_class.func_call_count_2 == 1

        dummy_subject_factory.on_next('TestSubject', 4)

        assert dummy_observable_class.check_val == 4
        assert dummy_observable_class.func_call_count == 1
        assert dummy_observable_class.check_val_2 == 4
        assert dummy_observable_class.func_call_count_2 == 2

    def test_subject_factory_unregister(self):
        """ Test unregistering from SubjectFactory """
        dummy_subject_factory = SubjectFactory()
        dummy_subject_factory.register('TestSubject')
        dummy_subject_factory.unregister('TestSubject')
        assert 'TestSubject' not in dummy_subject_factory._factory

    def test_subject_factory_unregister_non_existing_subject(self):
        """ Test unregistering non existing subject from SubjectFactory """
        dummy_subject_factory = SubjectFactory()
        try:
            dummy_subject_factory.unregister('TestSubject')
        except KeyError:
            pytest.fail(
                "Unregistering non existing subject should not raise KeyError")
