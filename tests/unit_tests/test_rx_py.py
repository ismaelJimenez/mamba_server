""" Rx_Py Subject Factory tests """

import pytest

from mamba_server.rx_py import SubjectFactoryRxPy as SubjectFactory


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


class TestClassSubjectFactoryClass:
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
