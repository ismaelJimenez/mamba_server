import tempfile
from tempfile import mkdtemp
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

    def test_startproject_in_new_folder(self):
        assert call(self, 'startproject', self.project_name) == 0

        assert exists(join(self.proj_path, 'mamba.cfg'))
        assert exists(join(self.proj_path, 'launch'))
        assert exists(join(self.proj_path, 'launch', 'default.launch.json'))
        assert exists(join(self.proj_path, 'components'))
        assert exists(join(self.proj_path, 'components', '__init__.py'))
        assert exists(join(self.proj_path, 'components', 'drivers'))
        assert exists(join(self.proj_path, 'components', 'drivers', '__init__.py'))
        assert exists(join(self.proj_path, 'components', 'gui'))
        assert exists(join(self.proj_path, 'components', 'gui', '__init__.py'))

        assert call(self, 'startproject', self.project_name) == 1
        assert call(self, 'startproject', 'wrong---project---name') == 1
