import pytest

from mamba_server.context import Context
from mamba_server.utils import misc
from mamba_server.commands import MambaCommand
from mamba_server.components.gui.plugins.interface import GuiPluginInterface
from mamba_server.components.gui.load_screen.interface import LoadScreenInterface

from mamba_server.exceptions import LaunchFileException


class TestClass:
    def setup_class(self):
        """ setup_class called once for the class """
        pass

    def teardown_class(self):
        """ teardown_class called once for the class """
        pass

    def setup_method(self):
        """ setup_method called for every method """
        pass

    def teardown_method(self):
        """ teardown_method called for every method """
        pass

    def test_get_classes_from_module_commands(self):
        cmds = misc.get_classes_from_module('mamba_server.commands', MambaCommand)
        assert len(cmds) == 2
        assert 'serve' in cmds
        assert 'startproject' in cmds

    def test_get_classes_from_module_commands_class_gui_plugin(self):
        assert misc.get_classes_from_module('mamba_server.commands',
                                            GuiPluginInterface) == {}

    def test_get_classes_from_module_components_class_gui_plugin_recursive(self):
        classes_dict = misc.get_classes_from_module('mamba_server.components.gui',
                                                    GuiPluginInterface)
        assert len(classes_dict) == 3
        assert 'about_qt' in classes_dict
        assert 'about_tk' in classes_dict
        assert 'quit' in classes_dict

    def test_get_classes_from_module_components_class_gui_plugin_subfolder(self):
        classes_dict = misc.get_classes_from_module(
            'mamba_server.components.gui.plugins.about.about_qt',
            GuiPluginInterface)
        assert len(classes_dict) == 1
        assert 'about_qt' in classes_dict

    def test_get_component_valid_id_and_type(self):
        components_dict = misc.get_component(
            'about_qt', 'mamba_server.components.gui.plugins', GuiPluginInterface,
            Context())
        assert components_dict is not None

    def test_get_component_valid_id_wrong_type(self):
        with pytest.raises(LaunchFileException) as excinfo:
            misc.get_component('about_qt', 'mamba_server.components.gui.plugins',
                               LoadScreenInterface, Context())

        assert 'not a valid component identifier' in str(excinfo.value)

    def test_get_components_valid_id_and_type(self):
        components_dict = misc.get_components(
            ['about_qt', 'quit'], 'mamba_server.components.gui.plugins',
            GuiPluginInterface, Context())
        assert len(components_dict) == 2
        assert 'about_qt' in components_dict
        assert 'quit' in components_dict

    def test_get_components_invalid_id(self):
        with pytest.raises(LaunchFileException) as excinfo:
            misc.get_components(['about_qt', 'about_tk_fail'],
                                'mamba_server.components.gui.plugins',
                                GuiPluginInterface, Context())

        assert 'not a valid component identifier' in str(excinfo.value)
