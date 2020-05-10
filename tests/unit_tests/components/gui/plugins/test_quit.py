from PySide2.QtGui import QKeySequence
from PySide2.QtWidgets import QMenu

from mamba_server.context import Context
from mamba_server.components.gui.plugins.quit import GuiPlugin
from mamba_server.components.gui.main.window.window import MainWindow


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
        'menu': '&File',
        'name': '&Quit',
        'shortcut': 'Ctrl+Q',
        'status_tip': 'Close Mamba Server'
    }

    # Test action or menu attributes have been created
    assert hasattr(widget, 'action')
    assert hasattr(widget, 'menu')

    # Test QAction text
    assert widget.action.text() == '&Quit'
    assert widget.action.statusTip() == "Close Mamba Server"
    assert widget.action.shortcut() == QKeySequence(67108945, 0, 0, 0)
    assert widget.action.isEnabled()

    # Test menu is in menu bar
    assert main_window.is_menu_in_bar('&File')

    # Test action has been added to menu
    assert len(widget.menu.actions()) == 1
    assert widget.menu.actions()[0].text() == '&Quit'
