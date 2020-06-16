import os
import pytest

from mamba.core.testing.utils import CallbackTestClass
from mamba.core.context import Context
from mamba.component.gui.common.quit import QuitComponent
from mamba.component.gui.qt import MainWindowQt

from mamba.core.msg.empty import Empty
from mamba.component.gui.msg.run_action import RunAction


class TestClass:
    def setup_method(self):
        """ setup_method called for every method """
        self.context = Context()
        self.context.set(
            'mamba_dir',
            os.path.join(os.path.dirname(__file__), '..', '..', '..', '..',
                         'mamba'))

    def teardown_method(self):
        """ teardown_method called for every method """
        del self.context

    def test_wo_context(self):
        """ Test component behaviour without required context """
        with pytest.raises(TypeError) as excinfo:
            QuitComponent()

        assert "missing 1 required positional argument" in str(excinfo.value)

    def test_component_w_menu_window(self):
        main_window = MainWindowQt(self.context)
        main_window.initialize()

        # Test help is not in menu bar
        assert not main_window._exists_menu('File')

        component = QuitComponent(self.context)
        component.initialize()

        # Test default configuration
        assert component._configuration == {
            'menu': 'File',
            'name': 'Quit',
            'shortcut': 'Ctrl+Q',
            'status_tip': 'Close Mamba Server'
        }

        # Test menu is in menu bar
        assert main_window._exists_menu('File')

    def test_component_run_rx_py(self):
        dummy_test_class = CallbackTestClass()
        main_window = MainWindowQt(self.context)
        main_window.initialize()

        self.context.set('main_window', main_window)
        component = QuitComponent(self.context)

        # Subscribe to the 'quit' that shall be published
        self.context.rx['quit'].subscribe(dummy_test_class.test_func_1)

        # Test execute closes Main Window
        main_window._show()
        assert main_window._app.isVisible()

        # Check it is not activated by another menu
        self.context.rx['run_plugin'].on_next(
            RunAction(menu_title='File_Wrong', action_name='Quit'))

        assert dummy_test_class.func_1_times_called == 0
        assert dummy_test_class.func_1_last_value is None

        # Check it is not activated by another action
        self.context.rx['run_plugin'].on_next(
            RunAction(menu_title='File', action_name='Quit_Wrong'))

        assert dummy_test_class.func_1_times_called == 0
        assert dummy_test_class.func_1_last_value is None

        # Check activation emits 'quit'
        self.context.rx['run_plugin'].on_next(
            RunAction(menu_title='File', action_name='Quit'))

        assert dummy_test_class.func_1_times_called == 1
        assert isinstance(dummy_test_class.func_1_last_value, Empty)

        # Test window is hidden per default
        assert not main_window._app.isVisible()
