"""
This module contains some assorted functions used in tests
"""
import os
from os.path import dirname
from importlib import import_module


def get_testenv():
    """Return a OS environment dict suitable to fork processes that need to import
    this installation of Mamba, instead of a system installed one.
    """
    env = os.environ.copy()
    env['PYTHONPATH'] = _get_pythonpath()
    return env


# Internal


def _get_pythonpath():
    """Return a PYTHONPATH suitable to use in processes so that they find this
    installation of Mamba"""
    mamba_path = import_module('mamba_server').__path__[0]
    return dirname(mamba_path) + os.pathsep + os.environ.get('PYTHONPATH', '')
