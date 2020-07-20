############################################################################
#
# Copyright (c) Mamba Developers. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#
############################################################################
""" Main window base """

import os
import time

from typing import Callable, Optional, Dict, List, Any
from mamba.core.typing import Menu
from rx import operators as op

from mamba.core.component_base import Component
from mamba.core.context import Context
from mamba.core.exceptions import ComponentConfigException
from mamba.core.utils import path_from_string
from mamba.core.msg import Empty, AppStatus
from mamba.component.gui.msg import RegisterAction


class MainWindow(Component):
    """ Main window base class """
    def __init__(self,
                 config_folder: str,
                 context: Context,
                 local_config: Optional[Dict[str, dict]] = None) -> None:
        super().__init__(config_folder, context, local_config)

        # Initialize custom variables
        self._load_app: Optional[Any] = None
        self._app: Optional[Any] = None
        self._menu_bar: Optional[Any] = None
        self._menus: Dict[str, Menu] = {}
        self._menu_actions: List[str] = []

        # Initialize Splash screen, if any
        self._splash_show()

        # Initialize observers
        self._register_observers()

    # Functions to be adapted

    def _create_main_window(self) -> None:
        """ Entry point for initializing the main window
            Note: It should be hidden per default.
        """
        raise NotImplementedError

    def _create_menu_bar(self) -> None:
        """ Entry point for creating the top menu bar """
        raise NotImplementedError

    def _create_splash_window(self) -> None:
        """ Entry point for creating and showing the load screen """
        raise NotImplementedError

    def _menu_add_action(self, menu: Menu, rx_value: RegisterAction) -> None:
        """ Entry point for adding an action to a given menu

            Args:
                menu: The given menu.
                rx_value: The value published by the subject.
        """
        raise NotImplementedError

    def _close_load_screen(self) -> None:
        """ Entry point for closing the load screen """
        raise NotImplementedError

    def _show(self) -> None:
        """ Entry point for showing main screen """
        raise NotImplementedError

    def _hide(self) -> None:
        """ Entry point for hiding main screen """
        raise NotImplementedError

    def _close(self, rx_value: Empty) -> None:
        """ Entry point for closing application

            Args:
                rx_value (Empty): The value published by the subject.
        """
        raise NotImplementedError

    def _start_event_loop(self) -> None:
        """
        Enters the main event loop and waits until close() is called.

        It is necessary to call this function to start event handling.The
        main event loop receives events from the window system and dispatches
        these to the application widgets.

        Generally, no user interaction can take place before calling
        start_event_loop().
        """
        raise NotImplementedError

    def _after(self, time_msec: int, action: Callable) -> None:
        """ Make the application perform an action after a time delay.

        Args:
            time_msec (int): The time in milliseconds to delay he action.
            action (function): The action to execute after time_msec delay.
        """
        raise NotImplementedError

    def _add_menu(self, menu_name: str) -> Menu:
        """Add a new top level menu in main window menu bar.

        Args:
            menu_name (str): The new menu name.

        Returns:
            Menu: A reference to the newly created menu.
        """
        raise NotImplementedError

    # Common functions

    def initialize(self) -> None:
        """ Entry point for component initialization """

        # Create new main window
        self._create_main_window()

        # Main window shall be hidden per default
        self._hide()

        # Initialize main window menu bar
        self._create_menu_bar()

    def _register_observers(self) -> None:
        """ Entry point for registering component observers """

        # Quit is sent to command App finalization
        self._context.rx['quit'].pipe(
            op.filter(lambda value: isinstance(value, Empty))).subscribe(
                on_next=self._close)

        # App_status.Running is sent by the context composer after services
        # initialization
        self._context.rx['app_status'].pipe(
            op.filter(lambda value: isinstance(value, AppStatus) and value ==
                      AppStatus.Running)).subscribe(on_next=self._run)

        # Register_action is sent by the gui plugins to register a new menu
        # bar action
        self._context.rx['register_action'].pipe(
            op.filter(lambda value: isinstance(value, RegisterAction))
        ).subscribe(on_next=self._register_action)

    def _splash_show(self) -> None:
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
                self.image_file = os.path.join(
                    self._context.get('mamba_dir'),
                    path_from_string(
                        self._configuration['load_screen']['image']))

                if not os.path.exists(self.image_file):
                    raise AttributeError()
            except AttributeError:
                image = \
                    path_from_string(
                        self._configuration['load_screen']['image']
                    )
                raise ComponentConfigException(f"Image file "
                                               f"'{image}' "
                                               f"not found")

            if ('time' in self._configuration['load_screen']) and (
                    self._configuration['load_screen']['time'] is not None
            ) and (not isinstance(self._configuration['load_screen']['time'],
                                  int)
                   and not isinstance(
                       self._configuration['load_screen']['time'], float)):
                raise ComponentConfigException(
                    "Load Screen time is not a valid number")

            self._create_splash_window()

    def _register_action(self, rx_value: RegisterAction) -> None:
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

        self._menu_add_action(menu, rx_value)

        self._menu_actions.append(
            f'{rx_value.menu_title}_{rx_value.action_name}')

    def _run(self, rx_value: AppStatus) -> None:
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

    def _transition_load_to_main(self) -> None:
        """ Entry point for showing the main window and closing load screen """
        # Close load splash if any
        if self._load_app is not None:
            self._close_load_screen()

        # Show main window
        self._show()

    def _exists_menu(self, search_menu: str) -> bool:
        """Checks if Menu is already in Main Window Menu bar.

        Args:
            search_menu (str): The searched menu name.

        Returns:
            bool: True if it menu is already in menu bar, otherwise false.
        """
        return search_menu in self._menus

    def _get_menu(self, search_menu: str) -> Menu:
        """Returns Menu is already in Main Window Menu bar.

        Args:
            search_menu (str): The searched menu name.

        Returns:
            Menu: Menu with title "search_menu". None is menu has
                  not been found.
        """
        if search_menu in self._menus:
            return self._menus[search_menu]

        return None

    def _is_action_in_menu(self, search_menu: str, search_action: str) -> bool:
        """Checks if action is already in Menu.

        Args:
            search_menu (str): The searched menu name.
            search_action (str): The searched action name.

        Returns:
            bool: True if it action is already in menu, otherwise false.
        """
        return f'{search_menu}_{search_action}' in self._menu_actions
