import pytest

from mamba_server.context import Context
from mamba_server.exceptions import ComponentConfigException


class TestClassSignal:
    def test_context(self):
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
