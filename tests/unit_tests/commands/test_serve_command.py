import tempfile
from tempfile import mkdtemp
from os import chdir
from os.path import join, exists
from shutil import rmtree
import sys
import subprocess

from mamba_server.utils.test import get_testenv


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
        pass

    def teardown_class(self):
        """ teardown_class called once for the class """
        pass

    def setup_method(self):
        """ setup_method called for every method """
        self.temp_path = mkdtemp()
        self.cwd = self.temp_path
        self.proj_path = join(self.temp_path, self.project_name)
        self.env = get_testenv()

    def teardown_method(self):
        """ teardown_method called for every method """
        rmtree(self.temp_path)

    def test_serve_non_existing(self):
        assert call(self, 'serve', '-r non_existing') == 1
