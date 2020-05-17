""" Subject tests. Based on PySignal tests """

import pytest
from functools import partial

from mamba_server.rx_mamba import Subject, SubjectFactory


class DummySlotClass:
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
    """A test standalone function for signals to attach onto"""
    test.check_val = 12345
    test.func_call_count += 1


class TestClassSignal:
    def setup_method(self):
        """ setup_method called for every method """
        self.check_val = None  # A state check for the tests
        self.func_call_count = 0  # A state check for test function

    def test_signal_function_connect(self):
        """ Test connecting signals to standalone functions """
        signal = Subject()
        signal.subscribe(dummy_test_func)
        # Expected single connected on_next
        assert len(signal._subscriptions) == 1

    def test_signal_function_connect_duplicate(self):
        """ Test connecting signals to duplicate standalone functions """
        signal = Subject()
        signal.subscribe(dummy_test_func)
        signal.subscribe(dummy_test_func)
        # Expected single connected on_next
        assert len(signal._subscriptions) == 1

    def test_signal_partial_connect(self):
        """ Tests connecting signals to partials """
        signal = Subject()
        signal.subscribe(partial(dummy_test_func, self, 'Partial'))
        # Expected single connected on_next
        assert len(signal._subscriptions) == 1

    def test_signal_partial_connect_duplicate(self):
        """ Tests connecting signals to duplicate partials """
        signal = Subject()
        func = partial(dummy_test_func, self, 'Partial')
        signal.subscribe(func)
        signal.subscribe(func)
        # Expected single connected on_next
        assert len(signal._subscriptions) == 1

    def test_signal_lambda_connect(self):
        """ Tests connecting signals to lambdas """
        signal = Subject()
        signal.subscribe(lambda value: dummy_test_func(self, value))
        # Expected single connected on_next
        assert len(signal._subscriptions) == 1

    def test_signal_lambda_connect_duplicate(self):
        """ Tests connecting signals to duplicate lambdas """
        signal = Subject()
        func = lambda value: dummy_test_func(self, value)
        signal.subscribe(func)
        signal.subscribe(func)
        # Expected single connected on_next
        assert len(signal._subscriptions) == 1

    def test_signal_method_connect(self):
        """ Test connecting signals to methods on class instances """
        signal = Subject()
        dummy_class = DummySlotClass()
        signal.subscribe(dummy_class.set_val)
        # Expected single connected slots
        assert len(signal._subscriptions) == 1

    def test_signal_method_connect_duplicate(self):
        """ Test connecting signals to duplicate methods on class instances """
        signal = Subject()
        dummy_class = DummySlotClass()
        signal.subscribe(dummy_class.set_val)
        signal.subscribe(dummy_class.set_val)
        # Expected single connected slots
        assert len(signal._subscriptions) == 1

    def test_signal_method_connect_different_instances(self):
        """ Test connecting the same method from different instances """
        signal = Subject()
        dummy_class_1 = DummySlotClass()
        dummy_class_2 = DummySlotClass()
        signal.subscribe(dummy_class_1.set_val)
        signal.subscribe(dummy_class_2.set_val)
        # Expected two connected slots
        assert len(signal._subscriptions) == 2

    def test_signal_connect_non_callable(self):
        """ Test connecting non-callable object """
        signal = Subject()
        with pytest.raises(ValueError) as excinfo:
            signal.subscribe('string')

        assert "Connection to non-callable 'str' object failed" in str(
            excinfo.value)

        with pytest.raises(ValueError) as excinfo:
            signal.subscribe(None)

        assert "Connection to non-callable 'NoneType' object failed" in str(
            excinfo.value)

    def test_signal_emit_to_function(self):
        """ Test emitting signal to standalone function """
        signal = Subject()
        signal.subscribe(dummy_test_func)
        signal.on_next(self)
        assert self.check_val == 12345
        assert self.func_call_count == 1

    def test_signal_emit_to_lambda(self):
        """ Test emitting signal to lambda """
        signal = Subject()
        signal.subscribe(lambda _: dummy_test_func(self))
        signal.on_next()
        assert self.check_val == 12345
        assert self.func_call_count == 1

    def test_signal_emit_to_instance_method(self):
        """ Test emitting signal to instance method """
        signal = Subject()
        dummy_class = DummySlotClass()
        signal.subscribe(dummy_class.set_val)
        signal.on_next('ClassMethod')
        assert dummy_class.check_val == 'ClassMethod'
        # Expected function to be called once
        assert dummy_class.func_call_count == 1

    def test_signal_emit_to_method_on_deleted_instance(self):
        """ Test emitting signal to deleted instance method """
        signal = Subject()
        dummy_class = DummySlotClass()
        signal.subscribe(dummy_class.set_val)
        signal.subscribe(lambda _: dummy_test_func(self))
        del dummy_class
        signal.on_next()
        assert self.check_val == 12345
        # Expected function to be called once
        assert self.func_call_count == 1

    def test_signal_emit_to_method_filter(self):
        """ Test connecting signals to methods on class instances """
        signal = Subject()
        dummy_slot_class = DummySlotClass()
        signal.subscribe(dummy_slot_class.set_val,
                         op_filter=lambda value: value % 2 == 0)
        signal.subscribe(dummy_slot_class.set_val_2)
        signal.on_next(1)
        assert dummy_slot_class.check_val is None
        assert dummy_slot_class.func_call_count == 0
        assert dummy_slot_class.check_val_2 == 1
        assert dummy_slot_class.func_call_count_2 == 1

    def test_signal_function_disconnect(self):
        """ Test disconnecting function """
        signal = Subject()
        signal.subscribe(dummy_test_func)
        signal.disconnect(dummy_test_func)
        assert len(signal._subscriptions) == 0

    def test_signal_function_disconnect_unconnected(self):
        """ Test disconnecting unconnected function """
        signal = Subject()
        try:
            signal.disconnect(dummy_test_func)
        except:
            pytest.fail("Disconnecting unconnected function should not raise")

    def test_signal_partial_disconnect(self):
        """ Test disconnecting partial function """
        signal = Subject()
        part = partial(dummy_test_func, self, 'Partial')
        signal.subscribe(part)
        signal.disconnect(part)
        # Slot was not removed from signal
        assert self.check_val is None

    def test_signal_partial_disconnect_unconnected(self):
        """ Test disconnecting unconnected partial function """
        signal = Subject()
        part = partial(dummy_test_func, self, 'Partial')
        try:
            signal.disconnect(part)
        except:
            pytest.fail("Disonnecting unconnected partial should not raise")

    def test_signal_lambda_disconnect(self):
        """ Test disconnecting lambda function """
        signal = Subject()
        func = lambda value: dummy_test_func(self, value)
        signal.subscribe(func)
        signal.disconnect(func)
        assert len(signal._subscriptions) == 0

    def test_signal_lambda_disconnect_unconnected(self):
        """ Test disconnecting unconnected lambda function """
        signal = Subject()
        func = lambda value: dummy_test_func(self, value)
        try:
            signal.disconnect(func)
        except:
            pytest.fail("Disconnecting unconnected lambda should not raise")

    def test_signal_method_disconnect(self):
        """Test disconnecting method"""
        def local_method(test):
            test.check_val = 2345
            test.func_call_count += 1

        signal = Subject()
        signal.subscribe(dummy_test_func)
        signal.subscribe(local_method)
        signal.disconnect(dummy_test_func)
        signal.on_next(self)
        # Expected 1 connected after disconnect
        assert len(signal._subscriptions) == 1
        # Expected function to be called once
        assert self.check_val == 2345
        # Expected function to not be called after disconnecting
        assert self.func_call_count == 1

    def test_signal_method_disconnect_unconnected(self):
        """ Test disconnecting unconnected method """
        signal = Subject()
        try:
            signal.disconnect(dummy_test_func)
        except:
            pytest.fail("Disconnecting unconnected method should not raise")

    def test_signal_disconnect_non_callable(self):
        """ Test disconnecting non-callable object """
        signal = Subject()
        try:
            signal.disconnect('string')
        except:
            pytest.fail("Disconnecting invalid object should not raise")

    def test_signal_dispose(self):
        """ Test clearing all slots """
        signal = Subject()
        func = lambda value: self.setVal(value)
        signal.subscribe(func)
        signal.subscribe(dummy_test_func)
        assert len(signal._subscriptions) == 2
        signal.dispose()
        assert len(signal._subscriptions) == 0

    def test_class_signal_clear_slots(self):
        """ Test clearing all slots """


class DummySignalClass(object):
    """A dummy class to check for instance handling of signals"""
    def __init__(self):
        self.signal = Subject()
        self.signalFactory = SubjectFactory()


class TestClassSignalFactoryClass:
    def test_class_signal_factory_class_connect(self):
        """ Test SubjectFactory indirect signal connection """
        dummy_signal_class = DummySignalClass()
        dummy_slot_class = DummySlotClass()
        dummy_signal_class.signalFactory.register('Spam')
        dummy_signal_class.signalFactory.subscribe('Spam',
                                                   dummy_slot_class.set_val)
        dummy_signal_class.signalFactory.on_next('Spam', 1)
        assert dummy_slot_class.check_val == 1
        assert dummy_slot_class.func_call_count == 1

    def test_class_signal_factory_connect_invalid_channel(self):
        """ Test SubjectFactory connecting to invalid channel """
        dummy_signal_class = DummySignalClass()
        dummy_slot_class = DummySlotClass()
        dummy_signal_class.signalFactory.subscribe('Spam',
                                                   dummy_slot_class.set_val)
        dummy_signal_class.signalFactory.on_next('Spam', 1)
        assert dummy_slot_class.check_val == 1
        assert dummy_slot_class.func_call_count == 1

    def test_class_signal_factory_connect_emit(self):
        """ Test emitting signals from signal factory """
        dummy_signal_class = DummySignalClass()
        dummy_slot_class = DummySlotClass()
        dummy_signal_class.signalFactory.register('Spam')
        dummy_signal_class.signalFactory.subscribe('Spam',
                                                   dummy_slot_class.set_val)
        dummy_signal_class.signalFactory.on_next('Spam', 1)
        assert dummy_slot_class.check_val == 1
        assert dummy_slot_class.func_call_count == 1

    def test_class_signal_factory_deregister(self):
        """ Test unregistering from SubjectFactory """
        dummy_signal_class = DummySignalClass()
        dummy_signal_class.signalFactory.register('Spam')
        dummy_signal_class.signalFactory.unregister('Spam')
        assert 'Spam' not in dummy_signal_class.signalFactory._factory

    def test_class_signal_factory_deregister_invalid_channel(self):
        """ Test unregistering invalid channel from SubjectFactory """
        dummy_signal_class = DummySignalClass()
        try:
            dummy_signal_class.signalFactory.unregister('Spam')
        except KeyError:
            pytest.fail(
                "Deregistering invalid channel should not raise KeyError")
