import pytest
import os

from mamba_server.context import Context
from mamba_server.components.plugins.about.about_qt import GuiPlugin
from mamba_server.components.main.main_qt import MainWindow


class TestClass:
    def setup_class(self):
        """ setup_class called once for the class """
        pass

    def teardown_class(self):
        """ teardown_class called once for the class """
        pass

    def setup_method(self):
        """ setup_method called for every method """
        self.context = Context()
        self.context.set(
            'mamba_dir',
            os.path.join(os.path.dirname(__file__), '..', '..', '..', '..',
                         'mamba_server'))

    def teardown_method(self):
        """ teardown_method called for every method """
        del self.context

    def test_about_gui_plugin_wo_context(self):
        with pytest.raises(TypeError) as excinfo:
            GuiPlugin()

        assert "missing 1 required positional argument" in str(excinfo.value)

    def test_about_gui_plugin_w_empty_context(self):
        widget = GuiPlugin(Context())
        widget.initialize()

        # Test default configuration
        assert widget._configuration == {
            'menu': '&Help',
            'name': '&About',
            'status_tip': "Show the application's About box",
            'message_box_title': 'About Mamba Server'
        }

        assert "Mamba Server v" in widget._box_message
        assert widget._version != ""

    def test_about_gui_plugin_w_menu_window(self):
        main_window = MainWindow(self.context)
        main_window.initialize()

        # Test help is not in menu bar
        assert not main_window._exists_menu('&Help')

        self.context.set('main_window', main_window)
        widget = GuiPlugin(self.context)
        widget.initialize()

        # Test default configuration
        assert widget._configuration == {
            'menu': '&Help',
            'name': '&About',
            'status_tip': "Show the application's About box",
            'message_box_title': 'About Mamba Server'
        }

        assert "Mamba Server v" in widget._box_message
        assert widget._version != ""

        # Test menu is in menu bar
        assert main_window._exists_menu('&Help')
        assert main_window._is_action_in_menu('&Help', '&About')
