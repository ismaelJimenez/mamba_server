""" Subject Factory tests """

import pytest

from rx import operators as op

from mamba.core.subject_factory import SubjectFactory as SubjectFactory
from mamba.core.testing.utils import CallbackTestClass


class TestClassSubjectFactoryClass:
    def test_subject_factory_subscribe_to_non_existing_subject(self):
        """ Test SubjectFactory subscribing to non existing subject """
        dummy_subject_factory = SubjectFactory()
        callback_test_class = CallbackTestClass()

        dummy_subject_factory['TestSubject'].subscribe(
            callback_test_class.test_func_1)

        assert callback_test_class.func_1_last_value is None
        assert callback_test_class.func_1_times_called == 0

        dummy_subject_factory['TestSubject'].on_next(1)

        assert callback_test_class.func_1_last_value == 1
        assert callback_test_class.func_1_times_called == 1

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
        callback_test_class = CallbackTestClass()

        dummy_subject_factory['TestSubject'].pipe(
            op.filter(lambda value: value % 2 == 0)).subscribe(
                callback_test_class.test_func_1)

        dummy_subject_factory['TestSubject'].subscribe(
            callback_test_class.test_func_2)

        dummy_subject_factory['TestSubject'].on_next(1)
        assert callback_test_class.func_1_last_value is None
        assert callback_test_class.func_1_times_called == 0
        assert callback_test_class.func_2_last_value == 1
        assert callback_test_class.func_2_times_called == 1

        dummy_subject_factory['TestSubject'].on_next(4)

        assert callback_test_class.func_1_last_value == 4
        assert callback_test_class.func_1_times_called == 1
        assert callback_test_class.func_2_last_value == 4
        assert callback_test_class.func_2_times_called == 2

    def test_subject_factory_dispose(self):
        """ Test unregistering from a subject """
        dummy_subject_factory = SubjectFactory()
        callback_test_class = CallbackTestClass()

        subj_1 = dummy_subject_factory['TestSubject'].subscribe(
            callback_test_class.test_func_1)

        dummy_subject_factory['TestSubject'].subscribe(
            callback_test_class.test_func_2)

        subj_1.dispose()

        dummy_subject_factory['TestSubject'].on_next(1)

        assert callback_test_class.func_1_last_value is None
        assert callback_test_class.func_1_times_called == 0
        assert callback_test_class.func_2_last_value == 1
        assert callback_test_class.func_2_times_called == 1
