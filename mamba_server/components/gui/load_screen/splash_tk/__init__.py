import os
import tkinter as tk

from mamba_server.components.gui.load_screen.interface import LoadScreenInterface


class LoadScreen(LoadScreenInterface):
    def __init__(self, context=None):
        super(LoadScreen, self).__init__(os.path.dirname(__file__), context)

        self._app = tk.Tk()
        self._app.overrideredirect(True)
        self.hide()

        image_file = self.configuration['image']
        self._image = tk.PhotoImage(file=image_file)

        screen_width = self._app.winfo_screenwidth()
        screen_height = self._app.winfo_screenheight()
        self._app.geometry('%dx%d+%d+%d' %
                          (self._image.width(), self._image.height(),
                           (screen_width - self._image.width()) / 2,
                           (screen_height - self._image.height()) / 2))

        self._canvas = tk.Canvas(self._app,
                           height=self._image.height(),
                           width=self._image.width(),
                           bg="brown")
        self._canvas.create_image(self._image.width() / 2,
                            self._image.height() / 2,
                            image=self._image)
        self._canvas.pack()

    def show(self):
        """
        Entry point for showing main screen
        """
        self._app.update()
        self._app.deiconify()

    def hide(self):
        """
        Entry point for hiding main screen
        """
        self._app.withdraw()
        self._app.update()

    def close(self):
        """
        Entry point for closing main screen
        """

        # INFO: quit() stops the TCL interpreter, so the Tkinter - app will
        # stop. destroy() just terminates the mainloop and deletes all
        # widgets.

        self._app.destroy()

    def start_event_loop(self):
        """
        Enters the main event loop and waits until close() is called.

        It is necessary to call this function to start event handling.The
        main event loop receives events from the window system and dispatches
        these to the application widgets.

        Generally, no user interaction can take place before calling
        start_event_loop().
        """
        self._app.mainloop()

    def after(self, time_msec, action):
        """ Make the application perform an action after a time delay.

        Args:
            time_msec (int): The time in milliseconds to delay he action.
            action (function): The action to execute after time_msec delay.
        """
        self._app.after(int(time_msec), action)

