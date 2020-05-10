from mamba_server.components.gui.main_window.main_tk import MainWindow


def test_is_menu_in_bar(qtbot):
    main_window = MainWindow()

    # Test Menu is not present
    assert not main_window.is_menu_in_bar('menu_test')

    # Test Menu is present
    main_window.add_menu_in_bar('menu_test')
    assert main_window.is_menu_in_bar('menu_test')


def test_get_menu_in_bar(qtbot):
    main_window = MainWindow()

    # Test Menu is not present
    assert main_window.get_menu_in_bar('menu_test') is None

    # Test Menu is present
    main_window.add_menu_in_bar('menu_test')
    assert main_window.get_menu_in_bar('menu_test') is not None
