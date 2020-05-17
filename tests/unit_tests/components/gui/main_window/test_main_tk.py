import pytest
import tkinter as tk

from mamba_server.components.gui.main_window.main_tk import MainWindow
from mamba_server.context import Context
from mamba_server.exceptions import ComponentConfigException


def test_main_tk_wo_context():
    with pytest.raises(TypeError) as excinfo:
        MainWindow()

    assert "missing 1 required positional argument" in str(excinfo.value)


def test_main_tk_w_context():
    widget = MainWindow(Context())

    # Test default configuration
    assert widget._configuration == {'title': 'Mamba Server'}

    assert widget._menus == {}
    assert widget._menu_actions == []

    # Test window is hidden per default
    assert widget._app.winfo_ismapped() == 0

    widget.close()
    widget._app.destroy()


def test_main_tk_show():
    widget = MainWindow(Context())

    # Test window is hidden per default
    assert widget._app.winfo_ismapped() == 0

    # Test window show
    widget.show()
    assert widget._app.winfo_ismapped() == 1

    widget.close()
    widget._app.destroy()


def test_main_tk_hide():
    widget = MainWindow(Context())

    # Test window is hidden per default
    assert widget._app.winfo_ismapped() == 0

    # Test window show
    widget.show()
    assert widget._app.winfo_ismapped() == 1

    # Test window hide
    widget.hide()
    assert widget._app.winfo_ismapped() == 0

    # Test window hide does not destroy window
    widget.show()
    assert widget._app.winfo_ismapped() == 1

    widget.close()
    widget._app.destroy()


def test_main_tk_close():
    widget = MainWindow(Context())

    # Test window show
    widget.show()
    assert widget._app.winfo_ismapped() == 1

    # Test window close
    widget.close()

    # Commented out because tk quit() does not generate an exception,
    # only destroy() does.
    #with pytest.raises(tk.TclError) as excinfo:
    #    widget._app.winfo_ismapped()
    #assert 'application has been destroyed' in str(excinfo.value)

    widget._app.destroy()


def test_main_tk_register_action():
    def dummy_func():
        pass

    widget = MainWindow(Context())

    assert not widget._is_action_in_menu('test_menu', 'test_action')

    # Add new menu
    widget.register_action('test_menu', 'test_action', dummy_func)
    assert widget._is_action_in_menu('test_menu', 'test_action')

    # Attempt to register the same action twice in same menu is not allowed
    with pytest.raises(ComponentConfigException) as excinfo:
        widget.register_action('test_menu', 'test_action', dummy_func)

    assert 'already exists in menu' in str(excinfo.value)

    widget.close()
    widget._app.destroy()


def test_main_tk_event_loop_after():
    widget = MainWindow(Context())

    # Close window after 100 milliseconds
    widget.after(100, widget.close)
    widget.start_event_loop()

    assert widget._app.winfo_ismapped() == 0

    widget.close()
    widget._app.destroy()


def test_internal_main_tk_add_menu():
    widget = MainWindow(Context())

    assert not widget._exists_menu('test_menu')

    # Add new menu
    widget._add_menu('test_menu')
    assert widget._exists_menu('test_menu')

    widget.close()
    widget._app.destroy()


def test_internal_main_tk_get_menu():
    widget = MainWindow(Context())

    assert widget._get_menu('test_menu') is None

    # Add new menu
    widget._add_menu('test_menu')
    assert widget._get_menu('test_menu') is not None

    widget.close()
    widget._app.destroy()
