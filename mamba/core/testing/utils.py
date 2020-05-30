""" Common utilities for testing """

from typing import Optional, Any


class CallbackTestClass:
    """ Common class to test Subject callbacks """
    def __init__(self):
        self.func_1_times_called = 0
        self.func_1_last_value = None

    def test_func_1(self, rx_on_set: Optional[Any] = None):
        self.func_1_times_called += 1
        self.func_1_last_value = rx_on_set
