from mamba_server.utils import misc
from mamba_server.commands import MambaCommand
from mamba_server.components.gui.plugins import GuiPlugin


def test_get_classes_from_module_commands():
    cmds = misc.get_classes_from_module('mamba_server.commands', MambaCommand)
    assert len(cmds) == 2
    assert 'serve' in cmds
    assert 'startproject' in cmds


def test_get_classes_from_module_commands_class_gui_plugin():
    assert misc.get_classes_from_module('mamba_server.commands',
                                        GuiPlugin) == {}


def test_get_classes_from_module_components_class_gui_plugin_recursive():
    classes_dict = misc.get_classes_from_module('mamba_server.components',
                                                GuiPlugin)
    assert len(classes_dict) == 2
    assert 'about' in classes_dict
    assert 'quit' in classes_dict


def test_get_classes_from_module_components_class_gui_plugin_subfolder():
    classes_dict = misc.get_classes_from_module(
        'mamba_server.components.gui.plugins.about', GuiPlugin)
    assert len(classes_dict) == 1
    assert 'about' in classes_dict
