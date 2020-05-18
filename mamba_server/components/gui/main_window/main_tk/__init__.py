""" Main window implemented with TkInter """

import os
import tkinter as tk
import time

from mamba_server.components.component_base import ComponentBase
from mamba_server.exceptions import ComponentConfigException
from mamba_server.utils.misc import path_from_string
from mamba_server.components.observable_types.empty import Empty
from mamba_server.components.observable_types.app_status import AppStatus
from mamba_server.components.gui.main_window.observable_types.register_action\
    import RegisterAction
from mamba_server.components.gui.main_window.observable_types.run_action\
    import RunAction


class MainWindow(ComponentBase):
    """ Main window implemented with TkInter """
    def __init__(self, context, local_config=None):
        super(MainWindow, self).__init__(os.path.dirname(__file__), context,
                                         local_config)

        # Initialize custom variables
        self._load_app = None
        self._app = None
        self._menu_bar = None
        self._menus = None
        self._menu_actions = None

        # Initialize Splash screen, if any
        self._splash_show()

        # Initialize observers
        self._register_observers()

    def initialize(self):
        """ Entry point for component initialization """

        # Create new main window
        self._app = tk.Tk()
        self._app.protocol("WM_DELETE_WINDOW", self._close)
        self._app.title(self._configuration['title'])

        # Main window shall be hidden per default
        self._hide()

        # Initialize main window menu bar
        self._menu_bar = tk.Menu(self._app)
        self._app.config(menu=self._menu_bar)
        self._menus = {}
        self._menu_actions = []

    # Internal functions

    def _register_observers(self):
        """ Entry point for registering component observers """

        # Quit is sent to command App finalization
        self._context.rx.subscribe(subject_name='quit',
                                   on_next=self._close,
                                   op_filter=lambda rx: isinstance(rx, Empty))

        # App_status.Running is sent by the context composer after services
        # initialization
        self._context.rx.subscribe(
            subject_name='app_status',
            on_next=self._run,
            op_filter=lambda rx: isinstance(rx, AppStatus
                                            ) and rx == AppStatus.Running)

        # Register_action is sent by the plugins to register a new menu
        # bar action
        self._context.rx.subscribe(
            subject_name='register_action',
            on_next=self._register_action,
            op_filter=lambda rx: isinstance(rx, RegisterAction))

    def _splash_show(self):
        """ Entry point for showing load splash screen """

        # Show load screen only if it is defined in the configuration
        if 'load_screen' in self._configuration:
            # Initial time is used in case a minimum visualization
            # time is defined
            self._init_timestamp = time.time()

            # Check splash image is valid
            if 'image' not in self._configuration['load_screen']:
                raise ComponentConfigException(
                    "Load Screen image file not defined")

            try:
                image_file = os.path.join(
                    self._context.get('mamba_dir'),
                    path_from_string(
                        self._configuration['load_screen']['image']))

                if not os.path.exists(image_file):
                    raise AttributeError()
            except AttributeError:
                image = \
                    path_from_string(
                        self._configuration['load_screen']['image']
                    )
                raise ComponentConfigException(f"Image file "
                                               f"'{image}' "
                                               f"not found")

            if 'time' in self._configuration[
                    'load_screen'] and not self._configuration['load_screen'][
                        'time'] is None and not isinstance(
                            self._configuration['load_screen']['time'],
                            int) and not isinstance(
                                self._configuration['load_screen']['time'],
                                float):
                raise ComponentConfigException(
                    "Load Screen time is not a valid number")

            # Create new splash window
            self._load_app = tk.Tk()
            self._load_app.overrideredirect(True)
            self._splash_image = tk.PhotoImage(file=image_file)

            # Customize splash window size
            screen_width = self._load_app.winfo_screenwidth()
            screen_height = self._load_app.winfo_screenheight()
            self._load_app.geometry(
                '%dx%d+%d+%d' %
                (self._splash_image.width(), self._splash_image.height(),
                 (screen_width - self._splash_image.width()) / 2,
                 (screen_height - self._splash_image.height()) / 2))

            self._canvas = tk.Canvas(self._load_app,
                                     height=self._splash_image.height(),
                                     width=self._splash_image.width(),
                                     bg="brown")
            self._canvas.create_image(self._splash_image.width() / 2,
                                      self._splash_image.height() / 2,
                                      image=self._splash_image)
            self._canvas.pack()

            self._load_app.update()
            self._load_app.deiconify()

    def _register_action(self, rx_value):
        """ Entry point for registering a new menu bar action.

            Args:
                rx_value (RegisterAction): The value published by
                                           the subject.
        """
        # Create menu in menu bar if it doesnt exist yet
        if not self._exists_menu(rx_value.menu_title):
            menu = self._add_menu(rx_value.menu_title)
        else:
            menu = self._get_menu(rx_value.menu_title)

        # If it not allowed to have two actions with the same name in one menu
        if self._is_action_in_menu(rx_value.menu_title, rx_value.action_name):
            raise ComponentConfigException(
                f"Another action '{rx_value.menu_title}' already exists"
                f" in menu '{rx_value.action_name}'")

        # Register callback when command is selected from the menu
        menu.add_command(label=rx_value.action_name,
                         command=lambda: self._context.rx.on_next(
                             'run_plugin',
                             RunAction(menu_title=rx_value.menu_title,
                                       action_name=rx_value.action_name)))
        self._menu_actions.append(
            f'{rx_value.menu_title}_{rx_value.action_name}')

    def _run(self, rx_value):
        """ Entry point for running the window

            Args:
                rx_value (AppStatus): The value published by the subject.
        """
        # Delay Main window show in case a minimum splash time is defined
        if self._load_app is not None and 'time' in self._configuration[
                'load_screen'] and self._configuration['load_screen'][
                    'time'] is not None:
            self._after(
                self._configuration['load_screen']['time'] * 1000 -
                (time.time() - self._init_timestamp),
                self._transition_load_to_main)
        else:
            self._transition_load_to_main()

        # Start application event loop
        self._start_event_loop()

    def _transition_load_to_main(self):
        """ Entry point for showing the main window and closing load screen """
        # Close load splash if any
        if self._load_app is not None:
            self._load_app.destroy()
            self._load_app = None

        # Show main window
        self._show()

    def _show(self):
        """ Entry point for showing main screen """
        self._app.update()
        self._app.deiconify()

    def _hide(self):
        """ Entry point for hiding main screen """
        self._app.withdraw()
        self._app.update()

    def _close(self, rx_value=None):
        """ Entry point for closing application

            Args:
                rx_value (Empty): The value published by the subject.
        """
        # INFO: quit() stops the TCL interpreter, so the Tkinter - app will
        # stop. destroy() just terminates the mainloop and deletes all
        # widgets.

        if self._load_app is not None:
            self._load_app.destroy()
            self._load_app.quit()

        self._app.destroy()
        self._app.quit()

        self._load_app = None
        self._app = None

    def _start_event_loop(self):
        """
        Enters the main event loop and waits until close() is called.

        It is necessary to call this function to start event handling.The
        main event loop receives events from the window system and dispatches
        these to the application widgets.

        Generally, no user interaction can take place before calling
        start_event_loop().
        """
        self._app.mainloop()

    def _after(self, time_msec, action):
        """ Make the application perform an action after a time delay.

        Args:
            time_msec (int): The time in milliseconds to delay he action.
            action (function): The action to execute after time_msec delay.
        """
        self._app.after(int(time_msec), action)

    def _exists_menu(self, search_menu):
        """Checks if Menu is already in Main Window Menu bar.

        Args:
            search_menu (str): The searched menu name.

        Returns:
            bool: True if it menu is already in menu bar, otherwise false.
        """
        return search_menu in self._menus

    def _add_menu(self, menu_name):
        """Add a new top level menu in main window menu bar.

        Args:
            menu_name (str): The new menu name.

        Returns:
            tk.Menu: A reference to the newly created menu.
        """
        menu = tk.Menu(self._menu_bar, tearoff=0)
        self._menu_bar.add_cascade(label=menu_name, menu=menu)
        self._menus[menu_name] = menu
        return menu

    def _get_menu(self, search_menu):
        """Returns Menu is already in Main Window Menu bar.

        Args:
            search_menu (str): The searched menu name.

        Returns:
            tk.Menu: Menu with title "search_menu". None is menu has
                     not been found.
        """
        if search_menu in self._menus:
            return self._menus[search_menu]

        return None

    def _is_action_in_menu(self, search_menu, search_action):
        """Checks if action is already in Menu.

        Args:
            search_menu (str): The searched menu name.
            search_action (str): The searched action name.

        Returns:
            bool: True if it action is already in menu, otherwise false.
        """
        return f'{search_menu}_{search_action}' in self._menu_actions
