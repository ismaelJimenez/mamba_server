import pytest
import tkinter as tk

from mamba_server.components.gui.load_screen.splash.splash_tk import LoadScreen
from mamba_server.context import Context


def test_splash_tk_wo_context():
    widget = LoadScreen()

    # Test default configuration
    assert 'mamba-server/artwork/mamba_loading.png' in widget._configuration['image']
    assert 'photo' == widget._image.type()
    assert widget._canvas.winfo_exists()

    # Test window is hidden per default
    assert widget._app.winfo_ismapped() == 0

    widget.close()


def test_splash_tk_w_context():
    widget = LoadScreen(Context())

    # Test default configuration
    assert 'mamba-server/artwork/mamba_loading.png' in widget._configuration['image']
    assert 'photo' == widget._image.type()
    assert widget._canvas.winfo_exists()

    # Test window is hidden per default
    assert widget._app.winfo_ismapped() == 0

    widget.close()


def test_splash_tk_show():
    widget = LoadScreen()

    # Test window is hidden per default
    assert widget._app.winfo_ismapped() == 0

    # Test window show
    widget.show()
    assert widget._app.winfo_ismapped() == 1

    widget.close()


def test_splash_tk_hide():
    widget = LoadScreen()

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


def test_splash_tk_close():
    widget = LoadScreen()

    # Test window show
    widget.show()
    assert widget._app.winfo_ismapped() == 1

    # Test window close
    widget.close()

    with pytest.raises(tk.TclError) as excinfo:
        widget._app.winfo_ismapped()
    assert 'application has been destroyed' in str(excinfo.value)


def test_splash_tk_event_loop_after_close():
    widget = LoadScreen()

    # Close window after 100 milliseconds
    widget.after(100, widget.close)
    widget.start_event_loop()

    with pytest.raises(tk.TclError) as excinfo:
        widget._app.winfo_ismapped()
    assert 'application has been destroyed' in str(excinfo.value)
