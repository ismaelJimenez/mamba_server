""" Signal tests. Based on PySignal tests """

import pytest
from functools import partial

from mamba_server.signal import Signal, ClassSignal, ClassSignalFactory, SignalFactory


class DummySlotClass:
    """ A dummy class to check for slot handling """
    check_val = None
    func_call_count = 0
    check_val_2 = None
    func_call_count_2 = 0

    def set_val(self, val):
        """ A method to test slot calls with """
        self.check_val = val
        self.func_call_count += 1

    def set_val_2(self, val):
        """ A method to test slot calls with """
        self.check_val_2 = val
        self.func_call_count_2 += 1


def dummy_test_func(test, value):
    """A test standalone function for signals to attach onto"""
    test.check_val = value
    test.func_call_count += 1


class TestClassSignal:
    def setup_method(self):
        """ setup_method called for every method """
        self.check_val = None  # A state check for the tests
        self.func_call_count = 0  # A state check for test function

    def test_signal_function_connect(self):
        """ Test connecting signals to standalone functions """
        signal = Signal()
        signal.connect(dummy_test_func)
        # Expected single connected slot
        assert len(signal._slots) == 1

    def test_signal_function_connect_duplicate(self):
        """ Test connecting signals to duplicate standalone functions """
        signal = Signal()
        signal.connect(dummy_test_func)
        signal.connect(dummy_test_func)
        # Expected single connected slot
        assert len(signal._slots) == 1

    def test_signal_partial_connect(self):
        """ Tests connecting signals to partials """
        signal = Signal()
        signal.connect(partial(dummy_test_func, self, 'Partial'))
        # Expected single connected slot
        assert len(signal._slots) == 1

    def test_signal_partial_connect_duplicate(self):
        """ Tests connecting signals to duplicate partials """
        signal = Signal()
        func = partial(dummy_test_func, self, 'Partial')
        signal.connect(func)
        signal.connect(func)
        # Expected single connected slot
        assert len(signal._slots) == 1

    def test_signal_lambda_connect(self):
        """ Tests connecting signals to lambdas """
        signal = Signal()
        signal.connect(lambda value: dummy_test_func(self, value))
        # Expected single connected slot
        assert len(signal._slots) == 1

    def test_signal_lambda_connect_duplicate(self):
        """ Tests connecting signals to duplicate lambdas """
        signal = Signal()
        func = lambda value: dummy_test_func(self, value)
        signal.connect(func)
        signal.connect(func)
        # Expected single connected slot
        assert len(signal._slots) == 1

    def test_signal_method_connect(self):
        """ Test connecting signals to methods on class instances """
        signal = Signal()
        dummy_class = DummySlotClass()
        signal.connect(dummy_class.set_val)
        # Expected single connected slots
        assert len(signal._slots) == 1

    def test_signal_method_connect_duplicate(self):
        """ Test connecting signals to duplicate methods on class instances """
        signal = Signal()
        dummy_class = DummySlotClass()
        signal.connect(dummy_class.set_val)
        signal.connect(dummy_class.set_val)
        # Expected single connected slots
        assert len(signal._slots) == 1

    def test_signal_method_connect_different_instances(self):
        """ Test connecting the same method from different instances """
        signal = Signal()
        dummy_class_1 = DummySlotClass()
        dummy_class_2 = DummySlotClass()
        signal.connect(dummy_class_1.set_val)
        signal.connect(dummy_class_2.set_val)
        # Expected two connected slots
        assert len(signal._slots) == 2

    def test_signal_connect_non_callable(self):
        """ Test connecting non-callable object """
        signal = Signal()
        with pytest.raises(ValueError) as excinfo:
            signal.connect('string')

        assert "Connection to non-callable 'str' object failed" in str(
            excinfo.value)

        with pytest.raises(ValueError) as excinfo:
            signal.connect(None)

        assert "Connection to non-callable 'NoneType' object failed" in str(
            excinfo.value)

    def test_signal_emit_to_function(self):
        """ Test emitting signal to standalone function """
        signal = Signal()
        signal.connect(dummy_test_func)
        signal.emit(self, 'Method')
        assert self.check_val == 'Method'
        # Expected function to be called once
        assert self.func_call_count == 1

    def test_signal_emit_to_deleted_function(self):
        """ Test emitting signal to deleted method """
        def local_method(test, value):
            test.checkVal = value
            test.func_call_count += 1

        signal = Signal()
        signal.connect(local_method)
        del local_method
        signal.emit(self, 'Method')
        assert self.check_val is None
        # Expected function not to be called
        assert self.func_call_count == 0

    def test_signal_emit_to_partial(self):
        """ Test emitting signals to partial """
        signal = Signal()
        partial_func = partial(dummy_test_func, self, 'Partial')
        signal.connect(partial_func)
        signal.emit()
        assert self.check_val == 'Partial'
        # Expected function to be called once
        assert self.func_call_count == 1

    def test_signal_emit_to_lambda(self):
        """ Test emitting signal to lambda """
        signal = Signal()
        signal.connect(lambda value: dummy_test_func(self, value))
        signal.emit('Lambda')
        assert self.check_val == 'Lambda'
        # Expected function to be called once
        assert self.func_call_count == 1

    def test_signal_emit_to_instance_method(self):
        """ Test emitting signal to instance method """
        signal = Signal()
        dummy_class = DummySlotClass()
        signal.connect(dummy_class.set_val)
        signal.emit('ClassMethod')
        assert dummy_class.check_val == 'ClassMethod'
        # Expected function to be called once
        assert dummy_class.func_call_count == 1

    def test_signal_emit_to_method_on_deleted_instance(self):
        """ Test emitting signal to deleted instance method """
        signal = Signal()
        dummy_class = DummySlotClass()
        signal.connect(dummy_class.set_val)
        signal.connect(lambda value: dummy_test_func(self, value))
        del dummy_class
        signal.emit(1)
        assert self.check_val == 1
        # Expected function to be called once
        assert self.func_call_count == 1

    def test_signal_function_disconnect(self):
        """ Test disconnecting function """
        signal = Signal()
        signal.connect(dummy_test_func)
        signal.disconnect(dummy_test_func)
        assert len(signal._slots) == 0

    def test_signal_function_disconnect_unconnected(self):
        """ Test disconnecting unconnected function """
        signal = Signal()
        try:
            signal.disconnect(dummy_test_func)
        except:
            pytest.fail("Disconnecting unconnected function should not raise")

    def test_signal_partial_disconnect(self):
        """ Test disconnecting partial function """
        signal = Signal()
        part = partial(dummy_test_func, self, 'Partial')
        signal.connect(part)
        signal.disconnect(part)
        # Slot was not removed from signal
        assert self.check_val is None

    def test_signal_partial_disconnect_unconnected(self):
        """ Test disconnecting unconnected partial function """
        signal = Signal()
        part = partial(dummy_test_func, self, 'Partial')
        try:
            signal.disconnect(part)
        except:
            pytest.fail("Disonnecting unconnected partial should not raise")

    def test_signal_lambda_disconnect(self):
        """ Test disconnecting lambda function """
        signal = Signal()
        func = lambda value: dummy_test_func(self, value)
        signal.connect(func)
        signal.disconnect(func)
        assert len(signal._slots) == 0

    def test_signal_lambda_disconnect_unconnected(self):
        """ Test disconnecting unconnected lambda function """
        signal = Signal()
        func = lambda value: dummy_test_func(self, value)
        try:
            signal.disconnect(func)
        except:
            pytest.fail("Disconnecting unconnected lambda should not raise")

    def test_signal_method_disconnect(self):
        """Test disconnecting method"""
        def local_method(test, value):
            test.check_val = value
            test.func_call_count += 1

        signal = Signal()
        signal.connect(dummy_test_func)
        signal.connect(local_method)
        signal.disconnect(dummy_test_func)
        signal.emit(self, 1)
        # Expected 1 connected after disconnect
        assert len(signal._slots) == 1
        # Expected function to be called once
        assert self.check_val == 1
        # Expected function to not be called after disconnecting
        assert self.func_call_count == 1

    def test_signal_method_disconnect_unconnected(self):
        """ Test disconnecting unconnected method """
        signal = Signal()
        try:
            signal.disconnect(dummy_test_func)
        except:
            pytest.fail("Disconnecting unconnected method should not raise")

    def test_signal_disconnect_non_callable(self):
        """ Test disconnecting non-callable object """
        signal = Signal()
        try:
            signal.disconnect('string')
        except:
            pytest.fail("Disconnecting invalid object should not raise")

    def test_signal_clear_slots(self):
        """ Test clearing all slots """
        signal = Signal()
        func = lambda value: self.setVal(value)
        signal.connect(func)
        signal.connect(dummy_test_func)
        assert len(signal._slots) == 2
        signal.clear()
        assert len(signal._slots) == 0

    def test_class_signal_clear_slots(self):
        """ Test clearing all slots """


class DummySignalClass(object):
    """A dummy class to check for instance handling of signals"""
    cSignal = ClassSignal()
    cSignalFactory = ClassSignalFactory()

    def __init__(self):
        self.signal = Signal()
        self.signalFactory = SignalFactory()


class TestClassSignalClass:
    def test_class_signal_assign_to_property(self):
        """ Test assigning to a ClassSignal property """
        dummy_signal_class = DummySignalClass()
        with pytest.raises(RuntimeError) as excinfo:
            dummy_signal_class.cSignal = None
        assert 'Cannot assign to a Signal object' in str(excinfo.value)

    def test_class_signal_emit(self):
        """ Test emitting signals from class signal and that instances of the class are unique """
        dummy_signal_class_1 = DummySignalClass()
        dummy_slot_class = DummySlotClass()
        dummy_signal_class_1.cSignal.connect(dummy_slot_class.set_val)
        dummy_signal_class_2 = DummySignalClass()
        dummy_signal_class_2.cSignal.connect(dummy_slot_class.set_val_2)
        dummy_signal_class_1.cSignal.emit(1)
        assert dummy_slot_class.check_val == 1
        assert dummy_slot_class.func_call_count == 1
        dummy_signal_class_2.cSignal.emit(3)
        assert dummy_slot_class.check_val == 1
        assert dummy_slot_class.check_val_2 == 3
        assert dummy_slot_class.func_call_count == 1
        assert dummy_slot_class.func_call_count_2 == 1


class TestClassSignalFactory:
    def test_class_signal_factory_emit(self):
        """Test emitting signals from class signal factory and that class instances are unique"""
        dummy_signal_class_1 = DummySignalClass()
        dummy_slot_class = DummySlotClass()
        dummy_signal_class_1.cSignalFactory.register('Spam')
        dummy_signal_class_1.cSignalFactory['Spam'].connect(
            dummy_slot_class.set_val)
        dummy_signal_class_2 = DummySignalClass()
        dummy_signal_class_2.cSignalFactory.register('Spam')
        dummy_signal_class_2.cSignalFactory['Spam'].connect(
            dummy_slot_class.set_val_2)
        dummy_signal_class_1.cSignalFactory['Spam'].emit(1)
        assert dummy_slot_class.check_val == 1
        assert dummy_slot_class.func_call_count == 1
        dummy_signal_class_2.cSignalFactory['Spam'].emit(3)
        assert dummy_slot_class.check_val == 1
        assert dummy_slot_class.func_call_count == 1
        assert dummy_slot_class.check_val_2 == 3
        assert dummy_slot_class.func_call_count_2 == 1


class TestClassSignalFactoryClass:
    def test_class_signal_factory_class_assign_to_property(self):
        """ Test assigning to a ClassSignalFactory property """
        dummy_signal_class = DummySignalClass()
        with pytest.raises(RuntimeError) as excinfo:
            dummy_signal_class.cSignalFactory = None
        assert 'Cannot assign to a Signal object' in str(excinfo.value)

    def test_class_signal_factory_class_connect(self):
        """ Test SignalFactory indirect signal connection """
        dummy_signal_class = DummySignalClass()
        dummy_slot_class = DummySlotClass()
        dummy_signal_class.signalFactory.register('Spam')
        dummy_signal_class.signalFactory.connect('Spam',
                                                 dummy_slot_class.set_val)
        dummy_signal_class.signalFactory.emit('Spam', 1)
        assert dummy_slot_class.check_val == 1
        assert dummy_slot_class.func_call_count == 1

    def test_class_signal_factory_connect_invalid_channel(self):
        """ Test SignalFactory connecting to invalid channel """
        dummy_signal_class = DummySignalClass()
        dummy_slot_class = DummySlotClass()
        with pytest.raises(AssertionError) as excinfo:
            dummy_signal_class.signalFactory.connect('Spam',
                                                     dummy_slot_class.set_val)
        assert 'Spam is not a registered signal' in str(excinfo.value)

    def test_class_signal_factory_connect_emit(self):
        """ Test emitting signals from signal factory """
        dummy_signal_class = DummySignalClass()
        dummy_slot_class = DummySlotClass()
        dummy_signal_class.signalFactory.register('Spam')
        dummy_signal_class.signalFactory['Spam'].connect(
            dummy_slot_class.set_val)
        dummy_signal_class.signalFactory['Spam'].emit(1)
        assert dummy_slot_class.check_val == 1
        assert dummy_slot_class.func_call_count == 1

    def test_class_signal_factory_block_single(self):
        """ Test blocking single channel with signal factory """
        dummy_signal_class = DummySignalClass()
        dummy_slot_class = DummySlotClass()
        dummy_signal_class.signalFactory.register('Spam',
                                                  dummy_slot_class.set_val)
        dummy_signal_class.signalFactory.register('Eggs',
                                                  dummy_slot_class.set_val_2)
        dummy_signal_class.signalFactory.block('Spam')
        dummy_signal_class.signalFactory.emit('Spam', 1)
        dummy_signal_class.signalFactory.emit('Eggs', 2)
        assert dummy_slot_class.check_val is None
        assert dummy_slot_class.check_val_2 == 2
        assert dummy_slot_class.func_call_count == 0
        assert dummy_slot_class.func_call_count_2 == 1

    def test_class_signal_factory_unblock_single(self):
        """ Test unblocking a single channel with signal factory """
        dummy_signal_class = DummySignalClass()
        dummy_slot_class = DummySlotClass()
        dummy_signal_class.signalFactory.register('Spam',
                                                  dummy_slot_class.set_val)
        dummy_signal_class.signalFactory.register('Eggs',
                                                  dummy_slot_class.set_val_2)
        dummy_signal_class.signalFactory.block('Spam')
        dummy_signal_class.signalFactory.block('Spam', False)
        dummy_signal_class.signalFactory.emit('Spam', 1)
        dummy_signal_class.signalFactory.emit('Eggs', 2)
        assert dummy_slot_class.check_val == 1
        assert dummy_slot_class.check_val_2 == 2
        assert dummy_slot_class.func_call_count == 1
        assert dummy_slot_class.func_call_count_2 == 1

    def test_class_signal_factory_block_all(self):
        """ Test blocking all signals from signal factory """
        dummy_signal_class = DummySignalClass()
        dummy_slot_class = DummySlotClass()
        dummy_signal_class.signalFactory.register('Spam',
                                                  dummy_slot_class.set_val)
        dummy_signal_class.signalFactory.register('Eggs',
                                                  dummy_slot_class.set_val_2)
        dummy_signal_class.signalFactory.block()
        dummy_signal_class.signalFactory.emit('Spam', 1)
        dummy_signal_class.signalFactory.emit('Eggs', 2)
        assert dummy_slot_class.check_val is None
        assert dummy_slot_class.check_val_2 is None
        assert dummy_slot_class.func_call_count == 0
        assert dummy_slot_class.func_call_count_2 == 0

    def test_class_signal_factory_unblock_all(self):
        """ Test unblocking all signals from signal factory """
        dummy_signal_class = DummySignalClass()
        dummy_slot_class = DummySlotClass()
        dummy_signal_class.signalFactory.register('Spam',
                                                  dummy_slot_class.set_val)
        dummy_signal_class.signalFactory.register('Eggs',
                                                  dummy_slot_class.set_val_2)
        dummy_signal_class.signalFactory.block()
        dummy_signal_class.signalFactory.block(is_blocked=False)
        dummy_signal_class.signalFactory.emit('Spam', 1)
        dummy_signal_class.signalFactory.emit('Eggs', 2)
        assert dummy_slot_class.check_val == 1
        assert dummy_slot_class.check_val_2 == 2
        assert dummy_slot_class.func_call_count == 1
        assert dummy_slot_class.func_call_count_2 == 1

    def test_class_signal_factory_block_invalid_channel(self):
        """ Test blocking an invalid channel from signal factory """
        dummy_signal_class = DummySignalClass()

        with pytest.raises(RuntimeError) as excinfo:
            dummy_signal_class.signalFactory.block('Spam')
        assert 'Could not find signal matching Spam' in str(excinfo.value)

    def test_class_signal_factory_deregister(self):
        """ Test unregistering from SignalFactory """
        dummy_signal_class = DummySignalClass()
        dummy_signal_class.signalFactory.register('Spam')
        dummy_signal_class.signalFactory.deregister('Spam')
        assert 'Spam' not in dummy_signal_class.signalFactory

    def test_class_signal_factory_deregister_invalid_channel(self):
        """ Test unregistering invalid channel from SignalFactory """
        dummy_signal_class = DummySignalClass()
        try:
            dummy_signal_class.signalFactory.deregister('Spam')
        except KeyError:
            pytest.fail(
                "Deregistering invalid channel should not raise KeyError")
