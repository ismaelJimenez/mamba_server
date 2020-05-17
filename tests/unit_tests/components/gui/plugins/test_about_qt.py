import pytest

from mamba_server.context_mamba import Context
from mamba_server.components.gui.plugins.about.about_qt import GuiPlugin
from mamba_server.components.gui.main_window.main_qt import MainWindow


def test_about_gui_plugin_wo_context():
    with pytest.raises(TypeError) as excinfo:
        GuiPlugin()

    assert "missing 1 required positional argument" in str(excinfo.value)


def test_about_gui_plugin_w_empty_context():
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


def test_about_gui_plugin_w_menu_window():
    context = Context()
    main_window = MainWindow(context)

    # Test help is not in menu bar
    assert not main_window._exists_menu('&Help')

    context.set('main_window', main_window)
    widget = GuiPlugin(context)
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
