"""
This module contains some assorted functions used in tests
"""
import os
from os.path import dirname
from importlib import import_module
import tempfile
import subprocess
import sys


def get_testenv():
    """Return a OS environment dict suitable to fork processes that need to import
    this installation of Mamba, instead of a system installed one.
    """
    env = os.environ.copy()
    env['PYTHONPATH'] = _get_pythonpath()
    return env


def cmd_exec(self, cmd, *new_args, **kwargs):
    with tempfile.TemporaryFile() as out:
        args = (sys.executable, '-m', 'mamba_server.cmdline') + new_args
        return subprocess.call(args,
                               stdout=out,
                               stderr=out,
                               cwd=self.cwd,
                               env=self.env,
                               **kwargs)


# Internal


def _get_pythonpath():
    """Return a PYTHONPATH suitable to use in processes so that they find this
    installation of Mamba"""
    mamba_path = import_module('mamba_server').__path__[0]
    return dirname(mamba_path) + os.pathsep + os.environ.get('PYTHONPATH', '')
