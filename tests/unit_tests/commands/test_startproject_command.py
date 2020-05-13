import tempfile
from tempfile import mkdtemp
from os.path import join, dirname, exists
from shutil import rmtree
import os
import sys
import subprocess

from importlib import import_module


def get_pythonpath():
    """Return a PYTHONPATH suitable to use in processes so that they find this
    installation of Scrapy"""
    scrapy_path = import_module('mamba_server').__path__[0]
    return dirname(scrapy_path) + os.pathsep + os.environ.get('PYTHONPATH', '')


def get_testenv():
    """Return a OS environment dict suitable to fork processes that need to import
    this installation of Scrapy, instead of a system installed one.
    """
    env = os.environ.copy()
    env['PYTHONPATH'] = get_pythonpath()
    return env


def call(self, *new_args, **kwargs):
    with tempfile.TemporaryFile() as out:
        args = (sys.executable, '-m', 'mamba_server.cmdline') + new_args
        return subprocess.call(args,
                               stdout=out,
                               stderr=out,
                               cwd=self.cwd,
                               env=self.env,
                               **kwargs)


class TestClass:
    project_name = 'testproject'

    def setup_class(self):
        """ setup_class called once for the class """
        self.temp_path = mkdtemp()
        self.cwd = self.temp_path
        self.proj_path = join(self.temp_path, self.project_name)
        self.env = get_testenv()

    def teardown_class(self):
        """ teardown_class called once for the class """
        rmtree(self.temp_path)

    def setup_method(self):
        """ setup_method called for every method """
        pass

    def teardown_method(self):
        """ teardown_method called for every method """
        pass

    def test_startproject(self):
        assert call(self, 'startproject', self.project_name) == 0

        assert exists(join(self.proj_path, 'mamba.cfg'))
        assert exists(join(self.proj_path, 'components'))
        assert exists(join(self.proj_path, 'components', '__init__.py'))

        assert call(self, 'startproject', self.project_name) == 1