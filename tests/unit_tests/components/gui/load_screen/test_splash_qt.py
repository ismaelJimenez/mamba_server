import os
import pytest

from mamba_server.components.gui.load_screen.splash.splash_qt import LoadScreen
from mamba_server.exceptions import ComponentConfigException
from mamba_server.context_mamba import Context


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
        context.set(
            'mamba_dir',
            os.path.join(os.path.dirname(__file__), '..', '..', '..', '..',
                         '..', 'mamba_server'))
        self.widget = LoadScreen(context)

    def teardown_method(self):
        """ teardown_method called for every method """
        self.widget.close()

    def test_splash_tk_wo_context(self):
        with pytest.raises(TypeError) as excinfo:
            LoadScreen()

        assert "missing 1 required positional argument" in str(excinfo.value)

    def test_splash_tk_w_context(self):
        # Test default configuration
        assert 'mamba_loading.png' in self.widget._configuration['image']
        assert not self.widget._app.pixmap().isNull()

        # Test window is hidden per default
        assert self.widget._app.isHidden()

    def test_splash_qt_show(self):
        # Test window is hidden per default
        assert not self.widget._app.isVisible()

        # Test window show
        self.widget.show()
        assert self.widget._app.isVisible()

    def test_splash_qt_hide(self):
        # Test window is hidden per default
        assert not self.widget._app.isVisible()

        # Test window show
        self.widget.show()
        assert self.widget._app.isVisible()

        # Test window hide
        self.widget.hide()
        assert not self.widget._app.isVisible()

        # Test window hide does not destroy window
        self.widget.show()
        assert self.widget._app.isVisible()

    def test_splash_qt_close(self):
        # Test window show
        self.widget.show()
        assert self.widget._app.isVisible()

        # Test window close
        self.widget.close()
        assert not self.widget._app.isVisible()

    def test_main_qt_event_loop_after(self):
        # Test window show
        self.widget.show()
        assert self.widget._app.isVisible()

        # Close window after 100 milliseconds
        self.widget.after(100, self.widget._qt_app.quit)
        self.widget.start_event_loop()

        # If it gets here it worked
        assert True
