import pytest
import os
from tempfile import mkdtemp

from mamba.core.context import Context
from mamba.core.msg import Empty, LogLevel, Log
from mamba.component.gui.qt.new_project_qt import NewProjectComponent
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
            NewProjectComponent()

        assert "missing 1 required positional argument" in str(excinfo.value)

    def test_component_w_empty_context(self):
        component = NewProjectComponent(self.context)
        component.initialize()

        # Test default configuration
        assert component._configuration == {
            'menu': '&File',
            'name': 'New Project',
            'shortcut': 'Ctrl+N'
        }

        assert component._app is not None

    def test_new_project_generation(self):
        dummy_test_class = CallbackTestClass()

        self.context.rx['log'].subscribe(dummy_test_class.test_func_1)

        component = NewProjectComponent(self.context)
        component.initialize()

        # Test default configuration
        assert component._configuration == {
            'menu': '&File',
            'name': 'New Project',
            'shortcut': 'Ctrl+N'
        }

        assert component._app is not None

        self.temp_path = mkdtemp()

        project_path = os.path.join(self.temp_path, 'test_folder')
        os.makedirs(project_path)

        component.generate_new_project(project_path)

        assert os.path.exists(os.path.join(project_path, 'mamba.cfg'))

        assert dummy_test_class.func_1_times_called == 0
        assert dummy_test_class.func_1_last_value is None

        component.generate_new_project(project_path)

        assert os.path.exists(os.path.join(project_path, 'mamba.cfg'))

        assert dummy_test_class.func_1_times_called == 1
        assert dummy_test_class.func_1_last_value.level == LogLevel.Error
        assert 'Error: mamba.cfg already exists in ' in dummy_test_class.func_1_last_value.msg
        assert '/test_folder' in dummy_test_class.func_1_last_value.msg
        assert dummy_test_class.func_1_last_value.src == 'new_project'

    def test_component_w_menu_window(self):
        main_window = MainWindowQt(self.context)
        main_window.initialize()

        # Test help is not in menu bar
        assert not main_window._exists_menu('&Help')

        component = NewProjectComponent(self.context)
        component.initialize()

        # Test default configuration
        assert component._configuration == {
            'menu': '&File',
            'name': 'New Project',
            'shortcut': 'Ctrl+N'
        }

        assert component._app is not None

        # Test menu is in menu bar
        assert main_window._exists_menu('&File')
        assert main_window._is_action_in_menu('&File', 'New Project')

        # Force close of any opened windows
        main_window._close(Empty())
        main_window._qt_app.quit()
