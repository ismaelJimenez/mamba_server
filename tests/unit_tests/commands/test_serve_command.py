from tempfile import mkdtemp
from os.path import join
from shutil import rmtree

from mamba_server.utils.test import get_testenv, cmd_exec, cmd_exec_output


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
        assert cmd_exec(self, 'mamba_server.cmdline', 'serve', '-h') == 0
        output = cmd_exec_output(self, 'mamba_server.cmdline', 'serve', '-h')
        assert 'Usage' in output
        assert 'mamba serve' in output
        assert 'Options' in output
        assert '--help' in output
        assert '--list' in output

    def test_serve_list(self):
        assert cmd_exec(self, 'mamba_server.cmdline', 'startproject',
                        self.project_name) == 0

        self.cwd = join(self.temp_path, self.project_name)

        assert cmd_exec(self, 'mamba_server.cmdline', 'serve', '-l') == 0
        output = cmd_exec_output(self, 'mamba_server.cmdline', 'serve', '-l')
        assert 'Available launch files' in output
        assert 'mamba_qt' in output
        assert '[DEFAULT]' in output
        assert 'Local' in output
        assert '- default' in output

    def test_serve_non_existing(self):
        assert cmd_exec(self, 'mamba_server.cmdline', 'serve',
                        '-r non_existing') == 1
        assert 'Unable to find launch file' in cmd_exec_output(
            self, 'mamba_server.cmdline', 'serve', '-r non_existing')
