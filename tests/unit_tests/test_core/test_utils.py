import pytest

from mamba.core.context import Context
from mamba.core import utils
from mamba.commands import MambaCommand
from mamba.core.component_base import Component

from mamba.core.exceptions import ComposeFileException


class TestClass:
    project_name = 'test_project_utils'

    def test_get_classes_from_module_commands(self):
        cmds = utils.get_classes_from_module('mamba.commands', MambaCommand)
        assert len(cmds) == 4
        assert 'serve' in cmds
        assert 'start' in cmds
        assert 'generate' in cmds
        assert 'dump_if' in cmds

    def test_get_classes_from_module_commands_class_gui_plugin(self):
        components = utils.get_classes_from_module('mamba.commands', Component)
        assert len(components) == 2
        assert 'gui' in components
        assert 'visa_instrument_driver' in components

    def test_get_classes_from_module_components_class_gui_plugin_recursive(
            self):
        classes_dict = utils.get_classes_from_module('mamba.component.gui',
                                                     Component)
        assert len(classes_dict) == 17  # One class is the base
        assert 'main_window_qt' in classes_dict
        assert 'parameter_setter_window_qt' in classes_dict
        assert 'parameter_setter_window_tk' in classes_dict
        assert 'parameter_getter_window_qt' in classes_dict
        assert 'parameter_getter_window_tk' in classes_dict
        assert 'main_window_tk' in classes_dict
        assert 'new_project_qt' in classes_dict
        assert 'open_project_qt' in classes_dict
        assert 'log_window_qt' in classes_dict
        assert 'log_window_tk' in classes_dict
        assert 'load_view_qt' in classes_dict
        assert 'load_view_tk' in classes_dict
        assert 'save_view_qt' in classes_dict
        assert 'save_view_tk' in classes_dict
        assert 'about_qt' in classes_dict
        assert 'about_tk' in classes_dict
        assert 'quit' in classes_dict

    def test_get_classes_from_module_components_class_gui_plugin_subfolder(
            self):
        classes_dict = utils.get_classes_from_module(
            'mamba.component.gui.qt.about_qt', Component)
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
            }, ['mamba.component'], Component, Context())
        assert len(components_dict) == 2
        assert 'about' in components_dict
        assert 'quit' in components_dict

    def test_get_components_invalid_id(self):
        with pytest.raises(ComposeFileException) as excinfo:
            utils.get_components({
                'about_qt': {},
                'about_tk_fail': {}
            }, ['mamba.component.gui'], Component, Context())

        assert 'about_qt: missing component property' in str(excinfo.value)

        with pytest.raises(ComposeFileException) as excinfo:
            utils.get_components({'about_qt': {
                'component': 'wrong'
            }}, ['mamba.component.gui'], Component, Context())

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

    def test_merge_dicts(self):
        # Test behaviour with no conflict
        assert utils.merge_dicts({
            1: {
                "a": "A"
            },
            2: {
                "b": "B"
            }
        }, {
            2: {
                "c": "C"
            },
            3: {
                "d": "D"
            }
        }) == {
            1: {
                'a': 'A'
            },
            2: {
                'b': 'B',
                'c': 'C'
            },
            3: {
                'd': 'D'
            }
        }

        # Test behaviour with None
        assert utils.merge_dicts({
            1: {
                "a": "A"
            },
            2: {
                "b": "B"
            }
        }, None) == {
            1: {
                'a': 'A'
            },
            2: {
                'b': 'B'
            }
        }

        assert utils.merge_dicts(None, {
            1: {
                "a": "A"
            },
            2: {
                "b": "B"
            }
        }) == {
            1: {
                'a': 'A'
            },
            2: {
                'b': 'B'
            }
        }

        assert utils.merge_dicts({
            1: {
                "a": None
            },
            2: {
                "b": "B"
            }
        }, {
            1: {
                "a": "A"
            },
            2: {
                "b": "C"
            }
        }) == {
            1: {
                'a': None
            },
            2: {
                'b': 'B'
            }
        }

        # Test behaviour with conflict
        assert utils.merge_dicts({
            1: {
                "a": "A"
            },
            2: {
                "b": "B"
            }
        }, {
            1: {
                "a": "A"
            },
            2: {
                "b": "C"
            }
        }) == {
            1: {
                'a': 'A'
            },
            2: {
                'b': 'B'
            }
        }
