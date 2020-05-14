import os
import pytest
import tkinter as tk

from mamba_server.components.gui.load_screen.splash.splash_tk import LoadScreen
from mamba_server.context import Context
from mamba_server.exceptions import ComponentConfigException


class TestClass:
    def setup_class(self):
        """ setup_class called once for the class """
        pass

    def teardown_class(self):
        """ teardown_class called once for the class """
        pass

    def setup_method(self):
        """ setup_method called for every method """
        context = Context()
        context.set('mamba_dir', os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', '..', 'mamba_server'))
        self.widget = LoadScreen(context)

    def teardown_method(self):
        """ teardown_method called for every method """
        pass

    def test_splash_tk_w_context(self):
        # Test default configuration
        assert 'mamba_loading.png' in self.widget._configuration['image']
        assert 'photo' == self.widget._image.type()
        assert self.widget._canvas.winfo_exists()

        # Test window is hidden per default
        assert self.widget._app.winfo_ismapped() == 0

        self.widget.close()

    def test_splash_tk_show(self):
        # Test window is hidden per default
        assert self.widget._app.winfo_ismapped() == 0

        # Test window show
        self.widget.show()
        assert self.widget._app.winfo_ismapped() == 1

        self.widget.close()

    def test_splash_tk_hide(self):
        # Test window is hidden per default
        assert self.widget._app.winfo_ismapped() == 0

        # Test window show
        self.widget.show()
        assert self.widget._app.winfo_ismapped() == 1

        # Test window hide
        self.widget.hide()
        assert self.widget._app.winfo_ismapped() == 0

        # Test window hide does not destroy window
        self.widget.show()
        assert self.widget._app.winfo_ismapped() == 1

        self.widget.close()

    def test_splash_tk_close(self):
        # Test window show
        self.widget.show()
        assert self.widget._app.winfo_ismapped() == 1

        # Test window close
        self.widget.close()

        with pytest.raises(tk.TclError) as excinfo:
            self.widget._app.winfo_ismapped()
        assert 'application has been destroyed' in str(excinfo.value)

    def test_splash_tk_event_loop_after_close(self):
        # Close window after 100 milliseconds
        self.widget.after(100, self.widget.close)
        self.widget.start_event_loop()

        with pytest.raises(tk.TclError) as excinfo:
            self.widget._app.winfo_ismapped()
        assert 'application has been destroyed' in str(excinfo.value)


def test_splash_tk_wo_context():
    with pytest.raises(ComponentConfigException) as excinfo:
        LoadScreen()

    assert 'Image file' in str(excinfo.value)
    assert 'not found' in str(excinfo.value)