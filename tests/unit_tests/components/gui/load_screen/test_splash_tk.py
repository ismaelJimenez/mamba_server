import os
import pytest
import tkinter as tk

from mamba_server.components.gui.load_screen.splash.splash_tk import LoadScreen
from mamba_server.context import Context


class TestClass:
    def setup_class(self):
        """ setup_class called once for the class """
        os.chdir(
            os.path.join(os.path.dirname(__file__), '..', '..', '..', '..'))

    def teardown_class(self):
        """ teardown_class called once for the class """
        pass

    def setup_method(self):
        """ setup_method called for every method """
        pass

    def teardown_method(self):
        """ teardown_method called for every method """
        pass

    def test_splash_tk_wo_context(self):
        widget = LoadScreen()

        # Test default configuration
        assert 'mamba_loading.png' in widget._configuration['image']
        assert 'photo' == widget._image.type()
        assert widget._canvas.winfo_exists()

        # Test window is hidden per default
        assert widget._app.winfo_ismapped() == 0

        widget.close()

    def test_splash_tk_w_context(self):
        widget = LoadScreen(Context())

        # Test default configuration
        assert 'mamba_loading.png' in widget._configuration['image']
        assert 'photo' == widget._image.type()
        assert widget._canvas.winfo_exists()

        # Test window is hidden per default
        assert widget._app.winfo_ismapped() == 0

        widget.close()

    def test_splash_tk_show(self):
        widget = LoadScreen()

        # Test window is hidden per default
        assert widget._app.winfo_ismapped() == 0

        # Test window show
        widget.show()
        assert widget._app.winfo_ismapped() == 1

        widget.close()

    def test_splash_tk_hide(self):
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

    def test_splash_tk_close(self):
        widget = LoadScreen()

        # Test window show
        widget.show()
        assert widget._app.winfo_ismapped() == 1

        # Test window close
        widget.close()

        with pytest.raises(tk.TclError) as excinfo:
            widget._app.winfo_ismapped()
        assert 'application has been destroyed' in str(excinfo.value)

    def test_splash_tk_event_loop_after_close(self):
        widget = LoadScreen()

        # Close window after 100 milliseconds
        widget.after(100, widget.close)
        widget.start_event_loop()

        with pytest.raises(tk.TclError) as excinfo:
            widget._app.winfo_ismapped()
        assert 'application has been destroyed' in str(excinfo.value)
