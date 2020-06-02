""" Common utilities for testing """
import os
from os.path import dirname
from importlib import import_module
import tempfile
import subprocess
import sys

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

def get_testenv():
    """Return a OS environment dict suitable to fork processes that need
    to import this installation of Mamba, instead of a system installed one.
    """
    env = os.environ.copy()
    env['PYTHONPATH'] = _get_pythonpath()
    return env


def cmd_exec(self, cmd, *new_args, **kwargs):
    """ Execute external command and return output status """
    with tempfile.TemporaryFile() as out:
        args = (sys.executable, '-m', cmd) + new_args
        return subprocess.call(args,
                               stdout=out,
                               stderr=out,
                               cwd=self.cwd,
                               env=self.env,
                               **kwargs)


def cmd_exec_output(self, cmd, *new_args, **kwargs):
    """ Execute external command and return terminal output """
    with tempfile.TemporaryFile() as out:
        args = (sys.executable, '-m', cmd) + new_args
        subprocess.call(args,
                        stdout=out,
                        stderr=out,
                        cwd=self.cwd,
                        env=self.env,
                        **kwargs)
        out.seek(0)
        return out.read().decode('utf-8')


# Internal


def _get_pythonpath():
    """Return a PYTHONPATH suitable to use in processes so that they find this
    installation of Mamba"""
    mamba_path = import_module('mamba').__path__[0]
    return dirname(mamba_path) + os.pathsep + os.environ.get('PYTHONPATH', '')