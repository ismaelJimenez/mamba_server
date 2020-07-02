import pytest
import os
import time

from PySide2.QtWidgets import QMdiSubWindow

from mamba.core.context import Context
from mamba.component.instrument_driver.digitizer import DigitizerKsm8131A
from mamba.component.gui.qt.parameter_setter_window_qt import ParameterSetterComponent
from mamba.component.gui.msg import RunAction, RegisterAction
from mamba.core.msg import Empty
from mamba.component.gui.qt import MainWindowQt
from mamba.core.testing.utils import CallbackTestClass


class TestClass:
    def setup_method(self):
        """ setup_method called for every method """
        self.context = Context()
        self.context.set(
            'mamba_dir',
            os.path.join(os.path.dirname(__file__), '..', '..', '..', '..',
                         '..', 'mamba'))

    def teardown_method(self):
        """ teardown_method called for every method """
        del self.context

    def test_component_wo_context(self):
        with pytest.raises(TypeError) as excinfo:
            ParameterSetterComponent()

        assert "missing 1 required positional argument" in str(excinfo.value)

    def test_component_w_empty_context(self):
        dummy_test_class = CallbackTestClass()

        self.context.rx['register_action'].subscribe(
            dummy_test_class.test_func_1)

        component = ParameterSetterComponent(self.context)
        component.initialize()

        time.sleep(.1)

        # Test default configuration
        assert component._configuration == {
            'menu': 'Utils',
            'name': 'Parameter Setter'
        }

        assert component._app is not None
        assert component._io_services == {}

        assert dummy_test_class.func_1_times_called == 1
        assert isinstance(dummy_test_class.func_1_last_value, RegisterAction)
        assert dummy_test_class.func_1_last_value.menu_title == 'Utils'
        assert dummy_test_class.func_1_last_value.action_name == 'Parameter Setter'
        assert dummy_test_class.func_1_last_value.shortcut is None
        assert dummy_test_class.func_1_last_value.status_tip is None

    def test_component_run_no_perspective(self):
        dummy_test_class = CallbackTestClass()

        component = ParameterSetterComponent(self.context)
        component.initialize()

        self.context.rx['register_window'].subscribe(
            dummy_test_class.test_func_1)

        self.context.rx['run_plugin'].on_next(
            RunAction(menu_title='Utils', action_name='Parameter Setter'))

        time.sleep(.1)

        assert dummy_test_class.func_1_times_called == 1
        assert isinstance(dummy_test_class.func_1_last_value, QMdiSubWindow)

        self.context.rx['component_perspective'].subscribe(
            dummy_test_class.test_func_2)

        self.context.rx['generate_perspective'].on_next(Empty())

        time.sleep(.1)

        assert dummy_test_class.func_2_times_called == 1
        assert dummy_test_class.func_2_last_value[
            'action_name'] == 'Parameter Setter'
        assert dummy_test_class.func_2_last_value['data']['services'] == []
        assert dummy_test_class.func_2_last_value['data']['pos_x'] == 0
        assert dummy_test_class.func_2_last_value['data']['pos_y'] == 0
        assert dummy_test_class.func_2_last_value['menu_title'] == 'Utils'

        component._app.shutdown()

    def test_component_run_w_perspective(self):
        dummy_test_class = CallbackTestClass()

        component = ParameterSetterComponent(self.context)
        component.initialize()

        digitizer = DigitizerKsm8131A(self.context)
        digitizer.initialize()

        time.sleep(.1)

        self.context.rx['register_window'].subscribe(
            dummy_test_class.test_func_1)

        self.context.rx['run_plugin'].on_next(
            RunAction(menu_title='Utils',
                      action_name='Parameter Setter',
                      perspective={
                          'services': [
                              'keysight_m8131a_digitizer -> clear',
                              'keysight_m8131a_digitizer -> connect'
                          ],
                          'width':
                          100,
                          'height':
                          100,
                          'pos_x':
                          0,
                          'pos_y':
                          0
                      }))

        time.sleep(.1)

        assert dummy_test_class.func_1_times_called == 1
        assert isinstance(dummy_test_class.func_1_last_value, QMdiSubWindow)

        self.context.rx['component_perspective'].subscribe(
            dummy_test_class.test_func_2)

        self.context.rx['generate_perspective'].on_next(Empty())

        time.sleep(.1)

        assert dummy_test_class.func_2_times_called == 1
        assert dummy_test_class.func_2_last_value[
            'action_name'] == 'Parameter Setter'
        assert dummy_test_class.func_2_last_value['data']['services'] == [
            'keysight_m8131a_digitizer -> clear',
            'keysight_m8131a_digitizer -> connect'
        ]
        assert dummy_test_class.func_2_last_value['data']['pos_x'] == 0
        assert dummy_test_class.func_2_last_value['data']['pos_y'] == 0
        assert dummy_test_class.func_2_last_value['menu_title'] == 'Utils'

        component._app.shutdown()

    def test_component_w_menu_window(self):
        main_window = MainWindowQt(self.context)
        main_window.initialize()

        # Test help is not in menu bar
        assert not main_window._exists_menu('Utils')

        component = ParameterSetterComponent(self.context)
        component.initialize()

        # Test menu is in menu bar
        assert main_window._exists_menu('Utils')
        assert main_window._is_action_in_menu('Utils', 'Parameter Setter')

        # Force close of any opened windows
        main_window._close(Empty())
        main_window._qt_app.quit()
        component._app.shutdown()
