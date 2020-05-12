from mamba_server.components.gui.load_screen.splash.splash_qt import LoadScreen
from mamba_server.context import Context


def test_splash_tk_wo_context():
    widget = LoadScreen()

    # Test default configuration
    assert 'mamba-server/artwork/mamba_loading.png' in widget._configuration['image']
    assert not widget._app.pixmap().isNull()

    # Test window is hidden per default
    assert widget._app.isHidden()

    widget.close()


def test_splash_tk_w_context():
    widget = LoadScreen(Context())

    # Test default configuration
    assert 'mamba-server/artwork/mamba_loading.png' in widget._configuration['image']
    assert not widget._app.pixmap().isNull()

    # Test window is hidden per default
    assert widget._app.isHidden()

    widget.close()


def test_splash_qt_show():
    widget = LoadScreen()

    # Test window is hidden per default
    assert not widget._app.isVisible()

    # Test window show
    widget.show()
    assert widget._app.isVisible()

    widget.close()


def test_splash_qt_hide():
    widget = LoadScreen()

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


def test_splash_qt_close():
    widget = LoadScreen()

    # Test window show
    widget.show()
    assert widget._app.isVisible()

    # Test window close
    widget.close()
    assert not widget._app.isVisible()


def test_main_qt_event_loop_after():
    widget = LoadScreen()

    # Test window show
    widget.show()
    assert widget._app.isVisible()

    # Close window after 100 milliseconds
    widget.after(100, widget._qt_app.quit)
    widget.start_event_loop()

    # If it gets here it worked
    assert True
