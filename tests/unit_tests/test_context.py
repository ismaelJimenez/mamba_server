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