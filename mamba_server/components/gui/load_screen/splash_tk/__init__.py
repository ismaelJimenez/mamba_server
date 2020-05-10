import os

import tkinter as tk

from mamba_server.components.gui.load_screen.interface import LoadScreenInterface


class LoadScreen(LoadScreenInterface):
    def __init__(self, context=None):
        super(LoadScreen, self).__init__(os.path.dirname(__file__), context)

        self.app = tk.Tk()

    def execute(self):
        image_file = self.configuration['image']
        self.image = tk.PhotoImage(file=image_file)

        # show no frame
        self.app.overrideredirect(True)
        screen_width = self.app.winfo_screenwidth()
        screen_height = self.app.winfo_screenheight()
        self.app.geometry('%dx%d+%d+%d' % (self.image.width(), self.image.height(),
                                       (screen_width - self.image.width()) / 2,
                                       (screen_height - self.image.height()) / 2))

        canvas = tk.Canvas(self.app,
                           height=self.image.height(),
                           width=self.image.width(),
                           bg="brown")
        canvas.create_image(self.image.width() / 2, self.image.height() / 2, image=self.image)
        canvas.pack()

        self.app.update()

    def close(self):
        self.app.destroy()

    def after(self, time_msec, action):
        self.app.after(int(time_msec), action)

    def start_event_loop(self):
        self.app.mainloop()


if __name__ == '__main__':
    load_screen = LoadScreen()
    load_screen.execute()
    load_screen.start_event_loop()

