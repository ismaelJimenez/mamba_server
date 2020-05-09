from PySide2.QtGui import QKeySequence
from PySide2.QtWidgets import QMenu

from mamba_server.context import Context
from mamba_server.components.gui.plugins.quit import GuiPlugin
from mamba_server.components.gui.main.window.window import MainWindow
from mamba_server.utils.component import is_menu_in_bar


def test_about_gui_plugin_w_menu_window(qtbot):
    main_window = MainWindow()

    # Test help is not in menu bar
    assert not is_menu_in_bar('&Help', main_window)

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
    assert len(main_window.menuBar().findChildren(QMenu)) == 1
    assert is_menu_in_bar('&File', main_window)

    # Test action has been added to menu
    assert len(widget.menu.actions()) == 1
    assert widget.menu.actions()[0].text() == '&Quit'
