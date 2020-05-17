""" Subject tests. Based on PySignal tests """

import pytest

from mamba_server.rx_py import SignalFactory


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


def dummy_test_func(test, value):
    """A test standalone function for signals to attach onto"""
    test.check_val = value
    test.func_call_count += 1


class DummySignalClass(object):
    """A dummy class to check for instance handling of signals"""
    def __init__(self):
        self.signalFactory = SignalFactory()


class TestClassSignalFactoryClass:
    def test_class_signal_factory_class_connect(self):
        """ Test SignalFactory indirect signal connection """
        dummy_signal_class = DummySignalClass()
        dummy_slot_class = DummySlotClass()
        dummy_signal_class.signalFactory.register('Spam')
        dummy_signal_class.signalFactory.subscribe('Spam',
                                                   dummy_slot_class.set_val)
        dummy_signal_class.signalFactory.on_next('Spam', 1)
        assert dummy_slot_class.check_val == 1
        assert dummy_slot_class.func_call_count == 1

    def test_class_signal_factory_connect_invalid_channel(self):
        """ Test SignalFactory connecting to invalid channel """
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

    def test_class_signal_factory_connect_emit_filter(self):
        """ Test emitting signals from signal factory """
        dummy_signal_class = DummySignalClass()
        dummy_slot_class = DummySlotClass()
        dummy_signal_class.signalFactory.subscribe(
            observable_name='Spam',
            on_next=dummy_slot_class.set_val,
            filter=lambda value: value%2 == 0)
        dummy_signal_class.signalFactory.subscribe(
            observable_name='Spam',
            on_next=dummy_slot_class.set_val_2)

        dummy_signal_class.signalFactory.on_next('Spam', 1)
        assert dummy_slot_class.check_val is None
        assert dummy_slot_class.func_call_count == 0
        assert dummy_slot_class.check_val_2 == 1
        assert dummy_slot_class.func_call_count_2 == 1

        dummy_signal_class.signalFactory.on_next('Spam', 4)

        assert dummy_slot_class.check_val == 4
        assert dummy_slot_class.func_call_count == 1
        assert dummy_slot_class.check_val_2 == 4
        assert dummy_slot_class.func_call_count_2 == 2

    def test_class_signal_factory_deregister(self):
        """ Test unregistering from SignalFactory """
        dummy_signal_class = DummySignalClass()
        dummy_signal_class.signalFactory.register('Spam')
        dummy_signal_class.signalFactory.deregister('Spam')
        assert 'Spam' not in dummy_signal_class.signalFactory._factory

    def test_class_signal_factory_deregister_invalid_channel(self):
        """ Test unregistering invalid channel from SignalFactory """
        dummy_signal_class = DummySignalClass()
        try:
            dummy_signal_class.signalFactory.deregister('Spam')
        except KeyError:
            pytest.fail(
                "Deregistering invalid channel should not raise KeyError")
