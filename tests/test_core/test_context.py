from mamba.core.context import Context
from mamba.core.subject_factory import SubjectFactory
from mamba.core.testing.utils import CallbackTestClass


class TestClassSignal:
    def test_context_get_set(self):
        context = Context()

        # Initial status
        assert context.get('param_1') is None

        # Set new parameter
        context.set('param_1', 1)
        assert context.get('param_1') is 1

        # Update existing parameter
        context.set('param_1', [0, 1, 2])
        assert context.get('param_1') == [0, 1, 2]

    def test_context_memory_not_static(self):
        context_1 = Context()

        context_1.set('param_1', 1)
        assert context_1.get('param_1') is 1

        context_2 = Context()
        assert context_2.get('param_1') is None

    def test_context_rx(self):
        context = Context()
        callback_test = CallbackTestClass()

        assert isinstance(context.rx, SubjectFactory)

        context.rx['test_1'].subscribe(on_next=callback_test.test_func_1)

        assert callback_test.func_1_times_called == 0
        assert callback_test.func_1_last_value is None

        context.rx['test_1'].on_next(2)

        assert callback_test.func_1_times_called == 1
        assert callback_test.func_1_last_value == 2

        context.rx['test_1'].on_next([1, 2, 3])

        assert callback_test.func_1_times_called == 2
        assert callback_test.func_1_last_value == [1, 2, 3]
