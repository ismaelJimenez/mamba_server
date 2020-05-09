from PySide2.QtWidgets import QApplication, QLabel, QSplashScreen
from PySide2.QtGui import QIcon, QPixmap, QGuiApplication


class LoadScreen(QSplashScreen):
    def __init__(self):
        super(LoadScreen, self).__init__()

        pixmap = QPixmap(
            '/home/argos/Workspace/mamba-framework/mamba-server/'
            'artwork/mamba_loading.jpg'
        )
        self.setPixmap(pixmap)

        screen = QGuiApplication.primaryScreen().geometry()
        self.move((screen.width() - self.size().width()) / 2,
                  (screen.height() - self.size().height()) / 2)


if __name__ == '__main__':
    app = QApplication([])

    load_screen = LoadScreen()
    load_screen.show()

    app.exec_()
