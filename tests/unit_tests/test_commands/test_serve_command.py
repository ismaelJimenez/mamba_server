from tempfile import mkdtemp
from os.path import join
from shutil import rmtree

from mamba.core.testing.utils import get_testenv, cmd_exec, cmd_exec_output


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

    def test_serve_help(self):
        assert cmd_exec(self, 'mamba', 'serve', '-h') == 0
        output = cmd_exec_output(self, 'mamba', 'serve', '-h')
        assert 'usage' in output
        assert 'mamba serve' in output
        assert 'optional arguments' in output
        assert '--help' in output

    def test_serve_non_existing(self):
        assert cmd_exec(self, 'mamba', 'serve', '-l non_existing') == 1
        assert 'Unable to find launch file' in cmd_exec_output(
            self, 'mamba', 'serve', '-l non_existing')
