import pytest

from mamba_server.components.gui.main_window.main_qt import MainWindow
from mamba_server.context_mamba import Context
from mamba_server.exceptions import ComponentConfigException

from mamba_server.components.gui.main_window.observer_types.register_action import RegisterAction


def test_main_qt_wo_context():
    with pytest.raises(TypeError) as excinfo:
        MainWindow()

    assert "missing 1 required positional argument" in str(excinfo.value)


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
    widget = MainWindow(Context())

    # Test window is hidden per default
    assert not widget._app.isVisible()

    # Test window show
    widget.show()
    assert widget._app.isVisible()

    widget.close()
    widget._qt_app.quit()


def test_main_qt_hide():
    widget = MainWindow(Context())

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
    widget = MainWindow(Context())

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

    context = Context()
    widget = MainWindow(context)

    assert not widget._is_action_in_menu('test_menu', 'test_action')

    # Add new menu
    context.rx.on_next(
        'register_action',
        RegisterAction(menu_title='test_menu', action_name='test_action'))
    assert widget._is_action_in_menu('test_menu', 'test_action')

    # Attempt to register the same action twice in same menu is not allowed
    with pytest.raises(ComponentConfigException) as excinfo:
        context.rx.on_next(
            'register_action',
            RegisterAction(menu_title='test_menu', action_name='test_action'))

    assert 'already exists in menu' in str(excinfo.value)

    # Test register_action is not called with wrong data type
    try:
        context.rx.on_next('register_action', 'Wrong')
    except:
        pytest.fail("Wrong data type should not raise")

    widget.close()
    widget._qt_app.quit()


def test_main_qt_event_loop_after():
    widget = MainWindow(Context())

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
    widget = MainWindow(Context())

    assert not widget._exists_menu('test_menu')

    # Add new menu
    widget._add_menu('test_menu')
    assert widget._exists_menu('test_menu')

    widget.close()
    widget._qt_app.quit()


def test_internal_main_qt_get_menu():
    widget = MainWindow(Context())

    assert widget._get_menu('test_menu') is None

    # Add new menu
    widget._add_menu('test_menu')
    assert widget._get_menu('test_menu') is not None

    widget.close()
    widget._qt_app.quit()
