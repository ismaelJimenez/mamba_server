############################################################################
#
# Copyright (c) Mamba Developers. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#
############################################################################
""" Main window implemented with TkInter """

import os
import tkinter as tk

from typing import Callable

from mamba.core.utils import path_from_string
from mamba.core.component_base import MainWindow
from mamba.core.msg import Empty
from mamba.component.gui.msg import RegisterAction, RunAction


class MainWindowTk(MainWindow):
    """ Main window implemented with TkInter """
    def __init__(self, context, local_config=None):
        super().__init__(os.path.dirname(__file__), context, local_config)

    # Functions to be adapted

    def _create_main_window(self) -> None:
        """ Entry point for initializing the main window
            Note: It should be hidden per default.
        """
        self._app = tk.Toplevel()
        self._app.protocol("WM_DELETE_WINDOW", self._close)
        self._app.title(self._configuration['title'])

        screen_width = self._app.winfo_screenwidth()
        screen_height = self._app.winfo_screenheight()
        self._app.geometry('%dx%d+%d+%d' %
                           (screen_width / 2, screen_height / 2,
                            screen_width / 15, screen_height / 15))

        self.app_file = os.path.join(
            self._context.get('mamba_dir'),
            path_from_string(self._configuration['background']))

        self._app_image = tk.PhotoImage(file=self.app_file)

        self._canvas = tk.Canvas(self._app,
                                 height=self._app_image.height(),
                                 width=self._app_image.width(),
                                 bg="brown")
        self._canvas.create_image(self._app_image.width() / 2,
                                  self._app_image.height() / 2,
                                  image=self._app_image)
        self._canvas.pack()

    def _create_menu_bar(self) -> None:
        """ Entry point for creating the top menu bar """
        self._menu_bar = tk.Menu(self._app)
        if self._app is not None:
            self._app.config(menu=self._menu_bar)

    def _create_splash_window(self) -> None:
        """ Entry point for creating and showing the load screen """
        # Create new splash window
        self._load_app = tk.Tk()
        self._load_app.overrideredirect(True)
        self._splash_image = tk.PhotoImage(file=self.image_file)

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

    def _menu_add_action(self, menu: tk.Menu,
                         rx_value: RegisterAction) -> None:
        """ Entry point for adding an action to a given menu

            Args:
                menu: The given menu.
                rx_value (RegisterAction): The value published by the subject.
        """
        menu.add_command(
            label=rx_value.action_name,
            command=lambda: self._context.rx['run_plugin'].on_next(
                RunAction(menu_title=rx_value.menu_title,
                          action_name=rx_value.action_name)))

    def _close_load_screen(self) -> None:
        """ Entry point for closing the load screen """
        if self._load_app is not None:
            self._load_app.withdraw()
            self._load_app.update()

    def _show(self) -> None:
        """ Entry point for showing main screen """
        if self._app is not None:
            self._app.update()
            self._app.deiconify()

    def _hide(self) -> None:
        """ Entry point for hiding main screen """
        if self._app is not None:
            self._app.withdraw()
            self._app.update()

    def _close(self, rx_value: Empty) -> None:
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
        elif self._app is not None:
            self._app.destroy()
            self._app.quit()

        self._load_app = None
        self._app = None

    def _start_event_loop(self) -> None:
        """
        Enters the main event loop and waits until close() is called.

        It is necessary to call this function to start event handling.The
        main event loop receives events from the window system and dispatches
        these to the application widgets.

        Generally, no user interaction can take place before calling
        start_event_loop().
        """
        if self._app is not None:
            self._app.mainloop()

    def _after(self, time_msec: int, action: Callable) -> None:
        """ Make the application perform an action after a time delay.

        Args:
            time_msec (int): The time in milliseconds to delay he action.
            action (callable): The action to execute after time_msec delay.
        """
        if self._app is not None:
            self._app.after(int(time_msec), action)

    def _add_menu(self, menu_name: str) -> tk.Menu:
        """Add a new top level menu in main window menu bar.

        Args:
            menu_name (str): The new menu name.

        Returns:
            tk.Menu: A reference to the newly created menu.
        """
        if not isinstance(self._menu_bar, tk.Menu):
            raise RuntimeError("Missing Menu Bar")

        menu = tk.Menu(self._menu_bar, tearoff=0)
        self._menu_bar.add_cascade(label=menu_name, menu=menu)
        self._menus[menu_name] = menu
        return menu
