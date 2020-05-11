from mamba_server.context import Context
from mamba_server.components.gui.plugins.quit import GuiPlugin
from mamba_server.components.gui.main_window.main_qt import MainWindow


def test_about_gui_plugin_w_menu_window():
    main_window = MainWindow()

    # Test help is not in menu bar
    assert not main_window._exists_menu('File')

    context = Context()
    context.set('main_window', main_window)
    widget = GuiPlugin(context)

    # Test default configuration
    assert widget._configuration == {
        'menu': 'File',
        'name': 'Quit',
        'shortcut': 'Ctrl+Q',
        'status_tip': 'Close Mamba Server'
    }

    # Test menu is in menu bar
    assert main_window._exists_menu('File')

    # Test execute closes Main Window
    main_window.show()
    assert main_window._app.isVisible()

    # Execute Quit Widget
    widget.execute()

    # Test window is hidden per default
    assert not main_window._app.isVisible()
