from PySide2.QtGui import QKeySequence
from PySide2.QtWidgets import QMenu, QMessageBox

from mamba_server.context import Context
from mamba_server.components.gui.plugins.about import GuiPlugin
from mamba_server.components.gui.main.window.window import MainWindow
from mamba_server.utils.component import is_menu_in_bar


def test_about_gui_plugin_wo_context(qtbot):
    widget = GuiPlugin()
    qtbot.addWidget(widget)

    # Test default configuration
    assert widget.configuration == {
        'menu': '&Help',
        'name': '&About',
        'shortcut': None,
        'status_tip': "Show the application's About box",
        'message_box_title': 'About Mamba Server'
    }

    # Test no action or menu attributes have been created
    assert not hasattr(widget, 'action')
    assert not hasattr(widget, 'menu')


def test_about_gui_plugin_w_empty_context(qtbot):
    widget = GuiPlugin(Context())
    qtbot.addWidget(widget)

    # Test default configuration
    assert widget.configuration == {
        'menu': '&Help',
        'name': '&About',
        'shortcut': None,
        'status_tip': "Show the application's About box",
        'message_box_title': 'About Mamba Server'
    }

    # Test no action or menu attributes have been created
    assert not hasattr(widget, 'action')
    assert not hasattr(widget, 'menu')


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
        'menu': '&Help',
        'name': '&About',
        'shortcut': None,
        'status_tip': "Show the application's About box",
        'message_box_title': 'About Mamba Server'
    }

    # Test action or menu attributes have been created
    assert hasattr(widget, 'action')
    assert hasattr(widget, 'menu')

    # Test QAction text
    assert widget.action.text() == '&About'
    assert widget.action.statusTip() == "Show the application's About box"
    assert widget.action.shortcut() == QKeySequence(0, 0, 0, 0)
    assert widget.action.isEnabled()

    # Test menu is in menu bar
    assert len(main_window.menuBar().findChildren(QMenu)) == 1
    assert is_menu_in_bar('&Help', main_window)

    # Test action has been added to menu
    assert len(widget.menu.actions()) == 1
    assert widget.menu.actions()[0].text() == '&About'


def test_about_gui_plugin_w_menu_window_menu_already_existing(
        qtbot, monkeypatch):
    main_window = MainWindow()

    main_window.menuBar().addMenu('&Help')
    # Test help is in menu bar
    assert is_menu_in_bar('&Help', main_window)

    context = Context()
    context.set('main_window', main_window)
    widget = GuiPlugin(context)
    qtbot.addWidget(widget)

    # Test default configuration
    assert widget.configuration == {
        'menu': '&Help',
        'name': '&About',
        'shortcut': None,
        'status_tip': "Show the application's About box",
        'message_box_title': 'About Mamba Server'
    }

    # Test action or menu attributes have been created
    assert hasattr(widget, 'action')
    assert hasattr(widget, 'menu')

    # Test QAction text
    assert widget.action.text() == '&About'
    assert widget.action.statusTip() == "Show the application's About box"
    assert widget.action.shortcut() == QKeySequence(0, 0, 0, 0)
    assert widget.action.isEnabled()

    # Test menu is in menu bar
    assert len(main_window.menuBar().findChildren(QMenu)) == 1
    assert is_menu_in_bar('&Help', main_window)

    # Test action has been added to menu
    assert len(widget.menu.actions()) == 1
    assert widget.menu.actions()[0].text() == '&About'

    # Test message
    assert 'Mamba' in widget.box_message
    assert widget.version == ""

    monkeypatch.setattr(QMessageBox, "about", lambda *args: QMessageBox.Yes)
    widget.show()

    assert widget.version != ""
