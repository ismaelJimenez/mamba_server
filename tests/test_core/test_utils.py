import pytest
import os
import sys
from tempfile import mkdtemp
from shutil import rmtree

from mamba.core.context import Context
from mamba.core import utils
from mamba.commands import MambaCommand
from mamba.components import ComponentBase

from mamba.core.exceptions import ComposeFileException
from mamba.utils.test import get_testenv, cmd_exec
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
        assert cmd_exec(self, 'mamba.cmdline', 'start', self.project_name) == 0
        self.cwd = join(self.temp_path, self.project_name)
        assert cmd_exec(self, 'mamba.cmdline', 'generate', 'plugin',
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
        cmds = utils.get_classes_from_module('mamba.commands', MambaCommand)
        assert len(cmds) == 3
        assert 'serve' in cmds
        assert 'start' in cmds
        assert 'generate' in cmds

    def test_get_classes_from_module_commands_class_gui_plugin(self):
        components = utils.get_classes_from_module('mamba.commands',
                                                   ComponentBase)
        assert len(components) == 2
        assert 'main' in components
        assert 'plugin' in components

    def test_get_classes_from_module_components_class_gui_plugin_recursive(
            self):
        classes_dict = utils.get_classes_from_module(
            'mamba.components.plugins', ComponentBase)
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
        classes_dict = utils.get_classes_from_module(
            'mamba.components.plugins.about.about_qt', ComponentBase)
        assert len(classes_dict) == 1
        assert 'about_qt' in classes_dict

    def test_get_classes_from_module_components_local(self):
        # Test component load
        classes_dict = utils.get_classes_from_module('components',
                                                     ComponentBase)
        assert len(classes_dict) == 1
        assert 'plugin_1' in classes_dict

    def test_get_components_duplicated_component(self):
        assert cmd_exec(self, 'mamba.cmdline', 'generate', 'plugin',
                        'quit') == 0
        assert exists(join(self.proj_path, 'components', 'plugin', 'quit'))

        with pytest.raises(ComposeFileException) as excinfo:
            utils.get_components('quit',
                                 ['mamba.components.plugins', 'components'],
                                 ComponentBase, Context())

        assert 'is duplicated' in str(excinfo.value)
        rmtree(join(self.proj_path, 'components', 'plugin', 'quit'))

    def test_get_components_local(self):
        components_dict = utils.get_components(
            {
                'about': {
                    'component': 'about_qt'
                },
                'quit': {
                    'component': 'quit'
                }
            }, ['mamba.components.plugins'], ComponentBase, Context())
        assert len(components_dict) == 2
        assert 'about' in components_dict
        assert 'quit' in components_dict

        components_dict = utils.get_components(
            {'plugin_1': {
                'component': 'about_qt'
            }}, ['components', 'mamba.components'], ComponentBase, Context())
        assert len(components_dict) == 1
        assert 'plugin_1' in components_dict

        components_dict = utils.get_components(
            {
                'about': {
                    'component': 'about_qt'
                },
                'about_1': {
                    'component': 'about_qt'
                },
                'quit': {
                    'component': 'quit'
                },
                'plugin_1': {
                    'component': 'about_qt'
                }
            }, ['mamba.components.plugins', 'components'], ComponentBase,
            Context())
        assert len(components_dict) == 4
        assert 'about_1' in components_dict
        assert 'about' in components_dict
        assert 'quit' in components_dict
        assert 'plugin_1' in components_dict

    def test_get_components_duplicated_component(self):
        assert cmd_exec(self, 'mamba.cmdline', 'generate', 'plugin',
                        'quit') == 0
        assert exists(join(self.proj_path, 'components', 'plugin', 'quit'))

        with pytest.raises(ComposeFileException) as excinfo:
            utils.get_components(['quit'],
                                 ['mamba.components.plugins', 'components'],
                                 ComponentBase, Context())

        assert 'is duplicated' in str(excinfo.value)
        rmtree(join(self.proj_path, 'components', 'plugin', 'quit'))

    def test_get_components_valid_id_and_type(self):
        components_dict = utils.get_components(
            {
                'about': {
                    'component': 'about_qt'
                },
                'quit': {
                    'component': 'quit'
                }
            }, ['mamba.components.plugins'], ComponentBase, Context())
        assert len(components_dict) == 2
        assert 'about' in components_dict
        assert 'quit' in components_dict

    def test_get_components_invalid_id(self):
        with pytest.raises(ComposeFileException) as excinfo:
            utils.get_components({
                'about_qt': None,
                'about_tk_fail': None
            }, ['mamba.components.plugins'], ComponentBase, Context())

        assert 'about_qt: missing component property' in str(excinfo.value)

        with pytest.raises(ComposeFileException) as excinfo:
            utils.get_components({'about_qt': {
                'component': 'wrong'
            }}, ['mamba.components.plugins'], ComponentBase, Context())

        assert "about_qt: component wrong' is not a valid component " \
               "identifier" in str(excinfo.value)

    def test_path_from_string(self):
        assert "../artwork/mamba_loading.png" == utils.path_from_string(
            "..\\artwork\\mamba_loading.png")
        assert "C:/artwork/mamba_loading.png" == utils.path_from_string(
            "C:\\artwork\\mamba_loading.png")
        assert "/home/artwork/mamba_loading.png" == utils.path_from_string(
            "/home/artwork/mamba_loading.png")
        assert "../artwork/mamba_loading.png" == utils.path_from_string(
            "../artwork/mamba_loading.png")
