import os
import pytest
import time

from mamba.core.testing.utils import CallbackTestClass
from mamba.core.context import Context
from mamba.component.utils.remote_shutdown import RemoteShutdown
from mamba.core.msg import Empty, ServiceRequest, ParameterType

component_path = os.path.join('component', 'utils', 'remote_shutdown')


class TestClass:
    def setup_method(self):
        """ setup_method called for every method """
        self.context = Context()

    def teardown_method(self):
        """ teardown_method called for every method """
        del self.context

    def test_wo_context(self):
        """ Test component behaviour without required context """
        with pytest.raises(TypeError) as excinfo:
            RemoteShutdown()

        assert "missing 1 required positional argument" in str(excinfo.value)

    def test_component_w_empty_context(self):
        component = RemoteShutdown(Context())
        component.initialize()

        # Test default configuration
        assert component._configuration == {'name': 'mamba_remote_shutdown'}

    def test_component_observer(self):
        dummy_test_class = CallbackTestClass()
        component = RemoteShutdown(self.context)
        component.initialize()

        # Subscribe to the 'tc' that shall be published
        self.context.rx['quit'].subscribe(dummy_test_class.test_func_1)

        self.context.rx['io_service_request'].on_next(
            ServiceRequest(provider='mamba_remote_shutdown',
                           id='shutdown',
                           type=ParameterType.set,
                           args=[]))

        time.sleep(.1)

        assert dummy_test_class.func_1_times_called == 1
        assert isinstance(dummy_test_class.func_1_last_value, Empty)
