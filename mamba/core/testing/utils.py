""" Common utilities for testing """

from typing import Optional, Any


class CallbackTestClass:
    """ Common class to test Subject callbacks """
    def __init__(self) -> None:
        self.func_1_times_called = 0
        self.func_1_last_value = None
        self.func_2_times_called = 0
        self.func_2_last_value = None

    def test_func_1(self, rx_on_next: Optional[Any] = None):
        self.func_1_times_called += 1
        self.func_1_last_value = rx_on_next

    def test_func_2(self, rx_on_next: Optional[Any] = None):
        self.func_2_times_called += 1
        self.func_2_last_value = rx_on_next
