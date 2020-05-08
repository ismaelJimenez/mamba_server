from PySide2.QtWidgets import QApplication, QLabel, QSplashScreen
from PySide2.QtGui import QIcon, QPixmap, QGuiApplication


# Subclass QMainWindow to customise your application's main window
class GuiLoading(QSplashScreen):
    def __init__(self):
        super(GuiLoading, self).__init__()

        pixmap = QPixmap('/home/argos/Workspace/mamba-framework/mamba-server/artwork/mamba_loading.jpg')
        self.setPixmap(pixmap)

        screen = QGuiApplication.primaryScreen().geometry()
        self.move((screen.width() - self.size().width()) / 2, (screen.height() - self.size().height()) / 2)


if __name__ == '__main__':
    # You need one (and only one) QApplication instance per application.
    # Pass in sys.argv to allow command line arguments for your app.
    # If you know you won't use command line arguments
    # QApplication([]) works too.
    app = QApplication([])

    loading = GuiLoading()
    loading.show()

    # Start the event loop.
    app.exec_()

    # Your application won't reach here until you exit and the event
    # loop has stopped.
