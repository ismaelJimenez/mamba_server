from mamba_server.context_mamba import Context as Context_Mamba
from mamba_server.context_rx import Context as Context_Rx
from mamba_server.components.plugins.quit import GuiPlugin
from mamba_server.components.gui.main_window.main_qt import MainWindow

from mamba_server.components.observer_types.empty import Empty
from mamba_server.components.gui.main_window.observer_types.run_action import RunAction


def test_about_gui_plugin_w_menu_window():
    context = Context_Mamba()
    main_window = MainWindow(context)

    # Test help is not in menu bar
    assert not main_window._exists_menu('File')

    context.set('main_window', main_window)
    widget = GuiPlugin(context)
    widget.initialize()

    # Test default configuration
    assert widget._configuration == {
        'menu': 'File',
        'name': 'Quit',
        'shortcut': 'Ctrl+Q',
        'status_tip': 'Close Mamba Server'
    }

    # Test menu is in menu bar
    assert main_window._exists_menu('File')

    # Test execute closes Main Window
    main_window._show()
    assert main_window._app.isVisible()

    # Execute Quit Widget
    widget.run(Empty())

    # Test window is hidden per default
    assert not main_window._app.isVisible()


class DummyTestClass:
    def __init__(self):
        super(DummyTestClass, self).__init__()
        self.times_called = 0
        self.last_value = None

    def test_function(self, rx_on_set=None):
        self.times_called += 1
        self.last_value = rx_on_set


def test_about_gui_plugin_run_rx_mamba():
    context = Context_Mamba()
    dummy_test_class = DummyTestClass()
    main_window = MainWindow(context)

    context.set('main_window', main_window)
    widget = GuiPlugin(context)

    # Subscribe to the 'quit' that shall be published
    context.rx.subscribe('quit', dummy_test_class.test_function)

    # Check it is not activated by another menu
    context.rx.on_next('run_plugin',
                       RunAction(menu_title='File_Wrong', action_name='Quit'))

    assert dummy_test_class.times_called == 0
    assert dummy_test_class.last_value is None

    # Check it is not activated by another action
    context.rx.on_next('run_plugin',
                       RunAction(menu_title='File', action_name='Quit_Wrong'))

    assert dummy_test_class.times_called == 0
    assert dummy_test_class.last_value is None

    # Check activation emits 'quit'
    context.rx.on_next('run_plugin',
                       RunAction(menu_title='File', action_name='Quit'))

    assert dummy_test_class.times_called == 1
    assert isinstance(dummy_test_class.last_value, Empty)


def test_about_gui_plugin_run_rx_py():
    context = Context_Rx()
    dummy_test_class = DummyTestClass()
    main_window = MainWindow(context)

    context.set('main_window', main_window)
    widget = GuiPlugin(context)

    # Subscribe to the 'quit' that shall be published
    context.rx.subscribe('quit', dummy_test_class.test_function)

    # Check it is not activated by another menu
    context.rx.on_next('run_plugin',
                       RunAction(menu_title='File_Wrong', action_name='Quit'))

    assert dummy_test_class.times_called == 0
    assert dummy_test_class.last_value is None

    # Check it is not activated by another action
    context.rx.on_next('run_plugin',
                       RunAction(menu_title='File', action_name='Quit_Wrong'))

    assert dummy_test_class.times_called == 0
    assert dummy_test_class.last_value is None

    # Check activation emits 'quit'
    context.rx.on_next('run_plugin',
                       RunAction(menu_title='File', action_name='Quit'))

    assert dummy_test_class.times_called == 1
    assert isinstance(dummy_test_class.last_value, Empty)
