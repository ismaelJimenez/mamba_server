import pytest

from mamba.core.context import Context
from mamba.core import utils
from mamba.commands import MambaCommand
from mamba.components import ComponentBase

from mamba.core.exceptions import ComposeFileException


class TestClass:
    project_name = 'test_project_utils'

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
