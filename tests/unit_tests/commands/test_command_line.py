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

    def test_command_line_help(self):
        assert cmd_exec(self, 'mamba_server.cmdline', '-h') == 0
        output = cmd_exec_output(self, 'mamba_server.cmdline', '-h')
        assert 'Usage' in output
        assert 'mamba <command>' in output
        assert 'generate' in output
        assert 'serve' in output
        assert 'start' in output

        assert cmd_exec(self, 'mamba_server.cmdline') == 0
        output = cmd_exec_output(self, 'mamba_server.cmdline')
        assert 'Usage' in output
        assert 'mamba <command>' in output
        assert 'generate' in output
        assert 'serve' in output
        assert 'start' in output

        assert cmd_exec(self, 'mamba_server.cmdline', 'wrong_command') == 2
        output = cmd_exec_output(self, 'mamba_server.cmdline', 'wrong_command')
        assert 'Unknown command' in output