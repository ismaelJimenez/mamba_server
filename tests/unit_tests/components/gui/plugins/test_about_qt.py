from mamba_server.context import Context
from mamba_server.components.gui.plugins.about.about_qt import GuiPlugin
from mamba_server.components.gui.main_window.main_qt import MainWindow


def test_about_gui_plugin_wo_context():
    widget = GuiPlugin()

    # Test default configuration
    assert widget._configuration == {
        'menu': '&Help',
        'name': '&About',
        'shortcut': None,
        'status_tip': "Show the application's About box",
        'message_box_title': 'About Mamba Server'
    }

    assert widget._box_message == "Mamba Server v{}"
    assert widget._version != ""


def test_about_gui_plugin_w_empty_context():
    widget = GuiPlugin()

    # Test default configuration
    assert widget._configuration == {
        'menu': '&Help',
        'name': '&About',
        'shortcut': None,
        'status_tip': "Show the application's About box",
        'message_box_title': 'About Mamba Server'
    }

    assert widget._box_message == "Mamba Server v{}"
    assert widget._version != ""


def test_about_gui_plugin_w_menu_window():
    main_window = MainWindow()

    # Test help is not in menu bar
    assert not main_window._exists_menu('&Help')

    context = Context()
    context.set('main_window', main_window)
    widget = GuiPlugin(context)

    # Test default configuration
    assert widget._configuration == {
        'menu': '&Help',
        'name': '&About',
        'shortcut': None,
        'status_tip': "Show the application's About box",
        'message_box_title': 'About Mamba Server'
    }

    assert widget._box_message == "Mamba Server v{}"
    assert widget._version != ""

    # Test menu is in menu bar
    assert main_window._exists_menu('&Help')
    assert main_window._is_action_in_menu('&Help', '&About')
