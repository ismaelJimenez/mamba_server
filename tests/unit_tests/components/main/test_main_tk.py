import pytest
import os

from mamba_server.components.main.main_tk import MainWindow
from mamba_server.context_mamba import Context
from mamba_server.exceptions import ComponentConfigException

from mamba_server.components.main.observable_types.register_action import RegisterAction
from mamba_server.components.observable_types.app_status import AppStatus
from mamba_server.components.observable_types.empty import Empty


class TestClass:
    def setup_class(self):
        """ setup_class called once for the class """
        pass

    def teardown_class(self):
        """ teardown_class called once for the class """
        pass

    def setup_method(self):
        """ setup_method called for every method """
        self.context = Context()
        self.context.set(
            'mamba_dir',
            os.path.join(os.path.dirname(__file__), '..', '..', '..', '..',
                         'mamba_server'))

    def teardown_method(self):
        """ teardown_method called for every method """
        del self.context

    def test_wo_context(self):
        """ Test component behaviour without required context """
        with pytest.raises(TypeError) as excinfo:
            MainWindow()

        assert "missing 1 required positional argument" in str(excinfo.value)

    def test_w_default_context_component_creation(self):
        """ Test component creation behaviour with default context """
        component = MainWindow(self.context)

        # Test default configuration load
        assert component._configuration == {
            'load_screen': {
                'image': 'artwork/mamba_loading.png',
                'time': 5
            },
            'title': 'Mamba Server'
        }

        # Test custom variables default values
        assert component._app is None
        assert component._menu_bar is None
        assert component._menus is None
        assert component._menu_actions is None

        # Test countdown started
        assert component._init_timestamp is not None

        # Test load window is shown on component creation
        assert component._load_app.winfo_ismapped() == 1

        # Force close of any opened windows
        component._load_app.quit()
        component._load_app.destroy()

    def test_w_default_context_component_initialization(self):
        """ Test component initialization behaviour with default context """
        component = MainWindow(self.context)
        component_creation_ts = component._init_timestamp

        component.initialize()

        # Test default configuration load
        assert component._configuration == {
            'load_screen': {
                'image': 'artwork/mamba_loading.png',
                'time': 5
            },
            'title': 'Mamba Server'
        }

        # Test countdown timestamp has not been modified
        assert component_creation_ts == component._init_timestamp

        # Test load window is still shown after component initialization
        assert component._load_app.winfo_ismapped() == 1

        # Test main window is hidden after component initialization
        assert component._app.winfo_ismapped() == 0

        # Test custom variables initialization values
        assert component._menu_bar is not None
        assert component._menus == {}
        assert component._menu_actions == []

        # Force close of any opened windows
        component._load_app.quit()
        component._load_app.destroy()

    def test_w_custom_context(self):
        """ Test component creation behaviour with default context """
        component = MainWindow(self.context,
                               local_config={
                                   'load_screen': {
                                       'time': 1
                                   },
                                   'title': 'Mamba Server Custom',
                                   'unused': 12
                               })

        # Test default configuration load
        assert component._configuration == {
            'load_screen': {
                'image': 'artwork/mamba_loading.png',
                'time': 1
            },
            'title': 'Mamba Server Custom',
            'unused': 12
        }

        # Force close of any opened windows
        component._load_app.quit()
        component._load_app.destroy()

    def test_w_wrong_custom_context(self):
        """ Test component creation behaviour with default context """

        with pytest.raises(ComponentConfigException) as excinfo:
            MainWindow(self.context,
                       local_config={
                           'load_screen': {
                               'image': 'Non-existent',
                               'time': 1
                           }
                       })

        assert "Image file 'Non-existent' not found" in str(excinfo.value)

        with pytest.raises(ComponentConfigException) as excinfo:
            MainWindow(self.context,
                       local_config={'load_screen': {
                           'time': 'Not-a-number'
                       }})

        assert "Load Screen time is not a valid number" in str(excinfo.value)

    def test_app_status_observer(self):
        """ Test component creation behaviour with default context """
        component = MainWindow(self.context,
                               local_config={'load_screen': {
                                   'time': None
                               }})
        component.initialize()

        # Test load window is shown
        assert component._load_app.winfo_ismapped() == 1

        component._after(1000, component._close)
        self.context.rx.on_next('app_status', AppStatus.Running)

        # Test load screen has been closed
        assert component._load_app is None

    def test_quit_observer_on_load(self):
        """ Test component creation behaviour with default context """
        component = MainWindow(self.context,
                               local_config={'load_screen': {
                                   'time': 10
                               }})
        component.initialize()

        # Test quit while on load window
        assert component._load_app.winfo_ismapped() == 1
        component._after(1000,
                         lambda: self.context.rx.on_next('quit', Empty()))
        self.context.rx.on_next('app_status', AppStatus.Running)

        # Test load screen has been closed
        assert component._load_app is None
        assert component._app is None

    def test_quit_observer_on_main(self):
        """ Test component creation behaviour with default context """
        component = MainWindow(self.context,
                               local_config={'load_screen': {
                                   'time': None
                               }})
        component.initialize()

        # Test quit while on main window
        assert component._load_app.winfo_ismapped() == 1
        component._after(1000,
                         lambda: self.context.rx.on_next('quit', Empty()))
        self.context.rx.on_next('app_status', AppStatus.Running)

        # Test load screen has been closed
        assert component._load_app is None
        assert component._app is None

    def test_register_observer_on_menu(self):
        """ Test component creation behaviour with default context """
        component = MainWindow(self.context,
                               local_config={'load_screen': {
                                   'time': None
                               }})
        component.initialize()

        component._after(
            1000, lambda: self.context.rx.on_next(
                'register_action',
                RegisterAction(menu_title='Test Menu 1',
                               action_name='Test Action 1',
                               shortcut='Crl+T',
                               status_tip='Custom status')))

        component._after(
            1000, lambda: self.context.rx.on_next(
                'register_action',
                RegisterAction(menu_title='Test Menu 2',
                               action_name='Test Action 2')))

        component._after(
            1000, lambda: self.context.rx.on_next(
                'register_action',
                RegisterAction(menu_title='Test Menu 3',
                               action_name='Test Action 1')))

        component._after(
            1000, lambda: self.context.rx.on_next(
                'register_action',
                RegisterAction(menu_title='Test Menu 1',
                               action_name='Test Action 2')))

        component._after(1500,
                         lambda: self.context.rx.on_next('quit', Empty()))

        self.context.rx.on_next('app_status', AppStatus.Running)

        assert component._is_action_in_menu('Test Menu 1', 'Test Action 1')
        assert component._is_action_in_menu('Test Menu 2', 'Test Action 2')
        assert component._is_action_in_menu('Test Menu 3', 'Test Action 1')
        assert component._is_action_in_menu('Test Menu 1', 'Test Action 2')

    def test_register_observer_on_load(self):
        """ Test component creation behaviour with default context """
        component = MainWindow(self.context,
                               local_config={'load_screen': {
                                   'time': 10
                               }})
        component.initialize()

        # Test register while on load window
        assert component._load_app.winfo_ismapped() == 1

        self.context.rx.on_next(
            'register_action',
            RegisterAction(menu_title='Test Menu 1',
                           action_name='Test Action 1',
                           shortcut='Crl+T',
                           status_tip='Custom status'))

        self.context.rx.on_next(
            'register_action',
            RegisterAction(menu_title='Test Menu 2',
                           action_name='Test Action 2'))

        self.context.rx.on_next(
            'register_action',
            RegisterAction(menu_title='Test Menu 3',
                           action_name='Test Action 1'))

        self.context.rx.on_next(
            'register_action',
            RegisterAction(menu_title='Test Menu 1',
                           action_name='Test Action 2'))

        assert component._is_action_in_menu('Test Menu 1', 'Test Action 1')
        assert component._is_action_in_menu('Test Menu 2', 'Test Action 2')
        assert component._is_action_in_menu('Test Menu 3', 'Test Action 1')
        assert component._is_action_in_menu('Test Menu 1', 'Test Action 2')

        with pytest.raises(ComponentConfigException) as excinfo:
            self.context.rx.on_next(
                'register_action',
                RegisterAction(menu_title='Test Menu 1',
                               action_name='Test Action 1'))

        assert "Another action 'Test Menu 1' already exists in menu " \
               "'Test Action 1" in str(excinfo.value)

        # Force close of any opened windows
        component._load_app.quit()
        component._load_app.destroy()

    def test_internal_show(self):
        component = MainWindow(self.context)
        component.initialize()

        # Test window is hidden per default
        assert component._app.winfo_ismapped() == 0

        # Test window show
        component._show()
        assert component._app.winfo_ismapped() == 1

        # Force close of any opened windows
        component._load_app.quit()
        component._load_app.destroy()

    def test_main_tk_hide(self):
        component = MainWindow(self.context)
        component.initialize()

        # Test window is hidden per default
        assert component._app.winfo_ismapped() == 0

        # Test window show
        component._show()
        assert component._app.winfo_ismapped() == 1

        # Test window hide
        component._hide()
        assert component._app.winfo_ismapped() == 0

        # Test window hide does not destroy window
        component._show()
        assert component._app.winfo_ismapped() == 1

        # Force close of any opened windows
        component._load_app.quit()
        component._load_app.destroy()

    def test_internal_event_loop_after(self):
        component = MainWindow(self.context)
        component.initialize()

        # Close window after 100 milliseconds
        component._after(100, component._close)
        component._start_event_loop()

        assert component._app is None

    def test_internal_add_menu(self):
        component = MainWindow(self.context)
        component.initialize()

        assert not component._exists_menu('test_menu')

        # Add new menu
        component._add_menu('test_menu')
        assert component._exists_menu('test_menu')

        # Force close of any opened windows
        component._load_app.quit()
        component._load_app.destroy()

    def test_internal_get_menu(self):
        component = MainWindow(self.context)
        component.initialize()

        assert component._get_menu('test_menu') is None

        # Add new menu
        component._add_menu('test_menu')
        assert component._get_menu('test_menu') is not None

        # Force close of any opened windows
        component._load_app.quit()
        component._load_app.destroy()
