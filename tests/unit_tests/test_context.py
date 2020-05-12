from mamba_server.context import Context


def test_context():
    context = Context()

    # Initial status
    assert context.get('param_1') is None

    # Set new parameter
    context.set('param_1', 1)
    assert context.get('param_1') is 1

    # Update existing parameter
    context.set('param_1', [0, 1, 2])
    assert context.get('param_1') == [0, 1, 2]


def test_context_memory_not_static():
    context_1 = Context()

    context_1.set('param_1', 1)
    assert context_1.get('param_1') is 1

    context_2 = Context()
    assert context_2.get('param_1') is None
