""" Rx_Py Subject Factory tests """

import pytest

from rx import operators as op

from mamba_server.subject_factory import SubjectFactory as SubjectFactory


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
    def test_subject_factory_subscribe_to_non_existing_subject(self):
        """ Test SubjectFactory subscribing to non existing subject """
        dummy_subject_factory = SubjectFactory()
        dummy_observable_class = DummyObservableClass()
        dummy_subject_factory['TestSubject'].subscribe(
            dummy_observable_class.set_val)
        dummy_subject_factory['TestSubject'].on_next(1)
        assert dummy_observable_class.check_val == 1
        assert dummy_observable_class.func_call_count == 1

    def test_subject_factory_subscribe_non_callable(self):
        """ Test subscribing non-callable object to subjects """
        dummy_subject_factory = SubjectFactory()
        dummy_subject_factory['TestSubject'].subscribe('string')

        with pytest.raises(TypeError) as excinfo:
            dummy_subject_factory['TestSubject'].on_next(1)

        assert "'str' object is not callable" in str(excinfo.value)

    def test_subject_factory_subscribe_filter(self):
        """ Test notification to all subscribed observers using filters """
        dummy_subject_factory = SubjectFactory()
        dummy_observable_class = DummyObservableClass()
        dummy_subject_factory['TestSubject'].pipe(
            op.filter(lambda value: value % 2 == 0)).subscribe(
                dummy_observable_class.set_val)

        dummy_subject_factory['TestSubject'].subscribe(
            dummy_observable_class.set_val_2)

        dummy_subject_factory['TestSubject'].on_next(1)
        assert dummy_observable_class.check_val is None
        assert dummy_observable_class.func_call_count == 0
        assert dummy_observable_class.check_val_2 == 1
        assert dummy_observable_class.func_call_count_2 == 1

        dummy_subject_factory['TestSubject'].on_next(4)

        assert dummy_observable_class.check_val == 4
        assert dummy_observable_class.func_call_count == 1
        assert dummy_observable_class.check_val_2 == 4
        assert dummy_observable_class.func_call_count_2 == 2

    def test_subject_factory_dispose(self):
        """ Test unregistering from a subject """
        dummy_subject_factory = SubjectFactory()
        dummy_observable_class = DummyObservableClass()
        subj_1 = dummy_subject_factory['TestSubject'].subscribe(
                dummy_observable_class.set_val)

        subj_2 = dummy_subject_factory['TestSubject'].subscribe(
            dummy_observable_class.set_val_2)

        subj_1.dispose()

        dummy_subject_factory['TestSubject'].on_next(1)

        assert dummy_observable_class.check_val is None
        assert dummy_observable_class.func_call_count == 0
        assert dummy_observable_class.check_val_2 == 1
        assert dummy_observable_class.func_call_count_2 == 1

