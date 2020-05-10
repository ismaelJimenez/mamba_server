from PySide2.QtWidgets import QApplication, QPushButton, QMainWindow, \
    QWidget, QVBoxLayout, QLabel, QMenu
from PySide2.QtCore import Slot


# Subclass QMainWindow to customise your application's main window
class MainWindow:
    def __init__(self, context=None):
        super(MainWindow, self).__init__()

        self.main_window = QMainWindow()

        self.main_window.setWindowTitle("My Awesome App")

        layout = QVBoxLayout()

        # Create a button, connect it and show it
        self.click_me = QPushButton("Click me")
        self.click_me.clicked.connect(self.say_hello)

        layout.addWidget(self.click_me)

        self.click_me_label = QLabel("Named:")

        layout.addWidget(self.click_me_label)

        widget = QWidget()
        widget.setLayout(layout)

        # Set the central widget of the Window. Widget will expand
        # to take up all the space in the window by default.
        self.main_window.setCentralWidget(widget)

    @Slot()
    def say_hello(self):
        self.click_me_label.setText("Hello!")


    def is_menu_in_bar(self, search_menu):
        """Checks if Menu is already in Main Window Menu bar.

        Args:
            search_menu (str): The searched menu name.
            main_window (QMainWindow): The main window application.

        Returns:
            bool: True if it menu is already in menu bar, otherwise false.
        """
        return search_menu in [
            menu.title() for menu in self.main_window.menuBar().findChildren(QMenu)
        ]

    def show(self):
        self.main_window.show()

    def close(self):
        self.main_window.close()

    def add_menu_in_bar(self, menu_name):
        return self.main_window.menuBar().addMenu(menu_name)

    def get_menu_in_bar(self, search_menu):
        """Returns Menu is already in Main Window Menu bar.

        Args:
            search_menu (str): The searched menu name.
            main_window (QMainWindow): The main window application.

        Returns:
            QMenu: Menu with title "search_menu". None is menu has not been found.
        """
        menu = [
            menu for menu in self.main_window.menuBar().findChildren(QMenu)
            if menu.title() == search_menu
        ]

        if len(menu) > 0:
            return menu[0]

        return None


if __name__ == '__main__':
    # You need one (and only one) QApplication instance per application.
    # Pass in sys.argv to allow command line arguments for your app.
    # If you know you won't use command line arguments
    # QApplication([]) works too.
    app = QApplication([])

    main_window = MainWindow()
    main_window.show()

    # Start the event loop.
    app.exec_()

    # Your application won't reach here until you exit and the event
    # loop has stopped.
