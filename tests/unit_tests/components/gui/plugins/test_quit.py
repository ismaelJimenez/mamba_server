from PySide2.QtGui import QKeySequence
from PySide2.QtWidgets import QMenu

from mamba_server.context import Context
from mamba_server.components.gui.plugins.quit import GuiPlugin
from mamba_server.components.gui.main_window.main_qt import MainWindow


def test_about_gui_plugin_w_menu_window(qtbot):
    main_window = MainWindow()

    # Test help is not in menu bar
    assert not main_window.is_menu_in_bar('&Help')

    context = Context()
    context.set('main_window', main_window)
    widget = GuiPlugin(context)
    qtbot.addWidget(widget)

    # Test default configuration
    assert widget.configuration == {
        'menu': 'File',
        'name': 'Quit',
        'shortcut': 'Ctrl+Q',
        'status_tip': 'Close Mamba Server'
    }

    # Test menu is in menu bar
    assert main_window.is_menu_in_bar('File')
