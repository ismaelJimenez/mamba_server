import pytest

from mamba_server.components.gui.main_window.main_qt import MainWindow
from mamba_server.context import Context
from mamba_server.exceptions import ComponentConfigException


def test_main_qt_wo_context():
    widget = MainWindow()

    # Test default configuration
    assert widget._configuration == {'title': 'Mamba Server'}

    assert widget._menus == {}
    assert widget._menu_actions == []
    assert widget._action_widgets == []

    # Test window is hidden per default
    assert widget._app.isHidden()

    widget.close()
    widget._qt_app.quit()


def test_main_qt_w_context():
    widget = MainWindow(Context())

    # Test default configuration
    assert widget._configuration == {'title': 'Mamba Server'}

    assert widget._menus == {}
    assert widget._menu_actions == []
    assert widget._action_widgets == []

    # Test window is hidden per default
    assert widget._app.isHidden()

    widget.close()
    widget._qt_app.quit()


def test_main_qt_show():
    widget = MainWindow()

    # Test window is hidden per default
    assert not widget._app.isVisible()

    # Test window show
    widget.show()
    assert widget._app.isVisible()

    widget.close()
    widget._qt_app.quit()


def test_main_qt_hide():
    widget = MainWindow()

    # Test window is hidden per default
    assert not widget._app.isVisible()

    # Test window show
    widget.show()
    assert widget._app.isVisible()

    # Test window hide
    widget.hide()
    assert not widget._app.isVisible()

    # Test window hide does not destroy window
    widget.show()
    assert widget._app.isVisible()

    widget.close()
    widget._qt_app.quit()


def test_main_qt_close():
    widget = MainWindow()

    # Test window show
    widget.show()
    assert widget._app.isVisible()

    # Test window close
    widget.close()
    assert not widget._app.isVisible()

    widget._qt_app.quit()


def test_main_qt_register_action():
    def dummy_func():
        pass

    widget = MainWindow()

    assert not widget._is_action_in_menu('test_menu', 'test_action')

    # Add new menu
    widget.register_action('test_menu', 'test_action', dummy_func)
    assert widget._is_action_in_menu('test_menu', 'test_action')

    # Attempt to register the same action twice in same menu is not allowed
    with pytest.raises(ComponentConfigException) as excinfo:
        widget.register_action('test_menu', 'test_action', dummy_func)

    assert 'already exists in menu' in str(excinfo.value)

    widget.close()
    widget._qt_app.quit()


def test_main_qt_event_loop_after():
    widget = MainWindow()

    # Test window show
    widget.show()
    assert widget._app.isVisible()

    # Close window after 100 milliseconds
    widget.after(100, widget.close)
    widget.start_event_loop()

    # Test window is hidden per default
    assert not widget._app.isVisible()

    widget.close()
    widget._qt_app.quit()


def test_internal_main_qt_add_menu():
    widget = MainWindow()

    assert not widget._exists_menu('test_menu')

    # Add new menu
    widget._add_menu('test_menu')
    assert widget._exists_menu('test_menu')

    widget.close()
    widget._qt_app.quit()


def test_internal_main_qt_get_menu():
    widget = MainWindow()

    assert widget._get_menu('test_menu') is None

    # Add new menu
    widget._add_menu('test_menu')
    assert widget._get_menu('test_menu') is not None

    widget.close()
    widget._qt_app.quit()
