import pytest
import os
import json
import time
from os.path import exists

from mamba.core.context import Context
from mamba.core.msg import Empty
from mamba.component.gui.msg import RunAction
from mamba.component.gui.qt.save_view_qt import SaveViewComponent
from mamba.component.gui.qt import MainWindowQt
from mamba.core.testing.utils import CallbackTestClass


class TestClass:
    project_name = 'testproject'

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
            SaveViewComponent()

        assert "missing 1 required positional argument" in str(excinfo.value)

    def test_component_w_empty_context(self):
        component = SaveViewComponent(self.context)
        component.initialize()

        # Test default configuration
        assert component._configuration == {
            'menu': 'View',
            'name': 'Save View'
        }

        assert component._app is not None
        assert component._views == []

    def test_generate_views_publication(self):
        dummy_test_class = CallbackTestClass()

        self.context.rx['generate_perspective'].subscribe(
            dummy_test_class.test_func_1)

        component = SaveViewComponent(self.context)
        component.initialize()

        # Test default configuration
        assert component._configuration == {
            'menu': 'View',
            'name': 'Save View'
        }

        assert component._app is not None
        assert component._views == []

        self.context.rx['run_plugin'].on_next(
            RunAction(menu_title='View', action_name='Save View'))

        time.sleep(.1)

        assert dummy_test_class.func_1_times_called == 1
        assert isinstance(dummy_test_class.func_1_last_value, Empty)

    def test_save_views(self):
        dummy_test_class = CallbackTestClass()

        component = SaveViewComponent(self.context)
        component.initialize()

        # Test default configuration
        assert component._configuration == {
            'menu': 'View',
            'name': 'Save View'
        }

        assert component._app is not None
        assert component._views == []

        component._process_component_perspective({
            "menu_title": "Utils",
            "action_name": "tc_window",
            "data": {
                "pos_x": 0,
                "pos_y": 0,
                "width": 670,
                "height": 296,
                "services": ["digitizer -> connect", "shutdown -> shutdown"]
            }
        })

        component.save_views('test_view_1.json')

        assert exists('test_view_1.json')

        with open('test_view_1.json', "r") as read_file:
            assert json.load(read_file) == [{
                "menu_title": "Utils",
                "action_name": "tc_window",
                "data": {
                    "pos_x": 0,
                    "pos_y": 0,
                    "width": 670,
                    "height": 296,
                    "services":
                    ["digitizer -> connect", "shutdown -> shutdown"]
                }
            }]

        os.remove('test_view_1.json')
        component.save_views('test_view_2')

        assert exists('test_view_2.json')

        with open('test_view_2.json', "r") as read_file:
            assert json.load(read_file) == [{
                "menu_title": "Utils",
                "action_name": "tc_window",
                "data": {
                    "pos_x": 0,
                    "pos_y": 0,
                    "width": 670,
                    "height": 296,
                    "services":
                    ["digitizer -> connect", "shutdown -> shutdown"]
                }
            }]

        component._process_component_perspective({
            "menu_title": "Utils",
            "action_name": "tm_window",
            "data": {
                "pos_x":
                670,
                "pos_y":
                0,
                "width":
                653,
                "height":
                296,
                "services": [
                    "cyclic_telemetry_tcp -> connected",
                    "digitizer -> connected"
                ]
            }
        })

        os.remove('test_view_2.json')
        component.save_views('test_view_3')

        assert exists('test_view_3.json')

        with open('test_view_3.json', "r") as read_file:
            assert json.load(read_file) == [{
                "menu_title": "Utils",
                "action_name": "tc_window",
                "data": {
                    "pos_x": 0,
                    "pos_y": 0,
                    "width": 670,
                    "height": 296,
                    "services":
                    ["digitizer -> connect", "shutdown -> shutdown"]
                }
            }, {
                'action_name': 'tm_window',
                'data': {
                    'height':
                    296,
                    'pos_x':
                    670,
                    'pos_y':
                    0,
                    'services': [
                        'cyclic_telemetry_tcp -> connected',
                        'digitizer -> connected'
                    ],
                    'width':
                    653
                },
                'menu_title': 'Utils'
            }]
        os.remove('test_view_3.json')

    def test_component_w_menu_window(self):
        main_window = MainWindowQt(self.context)
        main_window.initialize()

        # Test help is not in menu bar
        assert not main_window._exists_menu('&Help')

        component = SaveViewComponent(self.context)
        component.initialize()

        # Test default configuration
        assert component._configuration == {
            'menu': 'View',
            'name': 'Save View'
        }

        assert component._app is not None
        assert component._views == []

        # Test menu is in menu bar
        assert main_window._exists_menu('View')
        assert main_window._is_action_in_menu('View', 'Save View')

        # Force close of any opened windows
        main_window._close(Empty())
        main_window._qt_app.quit()
