import pytest
import os
import sys
from tempfile import mkdtemp
from shutil import rmtree

from mamba_server.context import Context
from mamba_server.utils import misc
from mamba_server.commands import MambaCommand
from mamba_server.components import ComponentBase

from mamba_server.exceptions import LaunchFileException
from mamba_server.utils.test import get_testenv, cmd_exec
from os.path import join, exists


class TestClass:
    project_name = 'testproject'

    def setup_class(self):
        """ setup_class called once for the class """
        self.temp_path = mkdtemp()
        self.cwd = self.temp_path
        self.proj_path = join(self.temp_path, self.project_name)
        self.env = get_testenv()

        self.current_folder = os.getcwd()
        sys.path.append(join(self.temp_path, self.project_name))

        # Initialize plugin in local folder
        assert cmd_exec(self, 'mamba_server.cmdline', 'start',
                        self.project_name) == 0
        self.cwd = join(self.temp_path, self.project_name)
        assert cmd_exec(self, 'mamba_server.cmdline', 'generate', 'plugin',
                        'plugin_1') == 0
        assert exists(join(self.proj_path, 'components', 'plugin', 'plugin_1'))

        os.chdir(join(self.temp_path, self.project_name))

    def teardown_class(self):
        """ teardown_class called once for the class """
        os.chdir(self.current_folder)
        rmtree(self.temp_path)
        sys.path.remove(join(self.temp_path, self.project_name))

    def setup_method(self):
        """ setup_method called for every method """
        pass

    def teardown_method(self):
        """ teardown_method called for every method """
        pass

    def test_get_classes_from_module_commands(self):
        cmds = misc.get_classes_from_module('mamba_server.commands',
                                            MambaCommand)
        assert len(cmds) == 3
        assert 'serve' in cmds
        assert 'start' in cmds
        assert 'generate' in cmds

    def test_get_classes_from_module_commands_class_gui_plugin(self):
        assert misc.get_classes_from_module('mamba_server.commands',
                                            ComponentBase) == {}

    def test_get_classes_from_module_components_class_gui_plugin_recursive(
            self):
        classes_dict = misc.get_classes_from_module(
            'mamba_server.components.plugins', ComponentBase)
        assert len(classes_dict) == 14  # One class is the base
        assert 'tm_window_tk' in classes_dict
        assert 'tc_window_tk' in classes_dict
        assert 'load_perspective_tk' in classes_dict
        assert 'save_perspective_tk' in classes_dict
        assert 'log_window_tk' in classes_dict
        assert 'load_perspective_qt' in classes_dict
        assert 'save_perspective_qt' in classes_dict
        assert 'tm_window_qt' in classes_dict
        assert 'tc_window_qt' in classes_dict
        assert 'log_window_qt' in classes_dict
        assert 'about_qt' in classes_dict
        assert 'about_tk' in classes_dict
        assert 'quit' in classes_dict

    def test_get_classes_from_module_components_class_gui_plugin_subfolder(
            self):
        classes_dict = misc.get_classes_from_module(
            'mamba_server.components.plugins.about.about_qt', ComponentBase)
        assert len(classes_dict) == 1
        assert 'about_qt' in classes_dict

    def test_get_classes_from_module_components_local(self):
        # Test component load
        classes_dict = misc.get_classes_from_module('components',
                                                    ComponentBase)
        assert len(classes_dict) == 1
        assert 'plugin_1' in classes_dict

    def test_get_components_duplicated_component(self):
        assert cmd_exec(self, 'mamba_server.cmdline', 'generate', 'plugin',
                        'quit') == 0
        assert exists(join(self.proj_path, 'components', 'plugin', 'quit'))

        with pytest.raises(LaunchFileException) as excinfo:
            misc.get_components(
                'quit', ['mamba_server.components.plugins', 'components'],
                ComponentBase, Context())

        assert 'is duplicated' in str(excinfo.value)
        rmtree(join(self.proj_path, 'components', 'plugin', 'quit'))

    def test_get_components_local(self):
        components_dict = misc.get_components({
            'about_qt': None,
            'quit': None
        }, ['mamba_server.components.plugins'], ComponentBase, Context())
        assert len(components_dict) == 2
        assert 'about_qt' in components_dict
        assert 'quit' in components_dict

        components_dict = misc.get_components(
            {'plugin_1': None}, ['components', 'mamba_server.components'],
            ComponentBase, Context())
        assert len(components_dict) == 1
        assert 'plugin_1' in components_dict

        components_dict = misc.get_components(
            {
                'about_qt': None,
                'quit': None,
                'plugin_1': None
            }, ['mamba_server.components.plugins', 'components'],
            ComponentBase, Context())
        assert len(components_dict) == 3
        assert 'about_qt' in components_dict
        assert 'quit' in components_dict
        assert 'plugin_1' in components_dict

    def test_get_components_duplicated_component(self):
        assert cmd_exec(self, 'mamba_server.cmdline', 'generate', 'plugin',
                        'quit') == 0
        assert exists(join(self.proj_path, 'components', 'plugin', 'quit'))

        with pytest.raises(LaunchFileException) as excinfo:
            misc.get_components(
                ['quit'], ['mamba_server.components.plugins', 'components'],
                ComponentBase, Context())

        assert 'is duplicated' in str(excinfo.value)
        rmtree(join(self.proj_path, 'components', 'plugin', 'quit'))

    def test_get_components_valid_id_and_type(self):
        components_dict = misc.get_components({
            'about_qt': None,
            'quit': None
        }, ['mamba_server.components.plugins'], ComponentBase, Context())
        assert len(components_dict) == 2
        assert 'about_qt' in components_dict
        assert 'quit' in components_dict

    def test_get_components_invalid_id(self):
        with pytest.raises(LaunchFileException) as excinfo:
            misc.get_components({
                'about_qt': None,
                'about_tk_fail': None
            }, ['mamba_server.components.plugins'], ComponentBase, Context())

        assert 'not a valid component identifier' in str(excinfo.value)

    def test_path_from_string(self):
        assert "../artwork/mamba_loading.png" == misc.path_from_string(
            "..\\artwork\\mamba_loading.png")
        assert "C:/artwork/mamba_loading.png" == misc.path_from_string(
            "C:\\artwork\\mamba_loading.png")
        assert "/home/artwork/mamba_loading.png" == misc.path_from_string(
            "/home/artwork/mamba_loading.png")
        assert "../artwork/mamba_loading.png" == misc.path_from_string(
            "../artwork/mamba_loading.png")
