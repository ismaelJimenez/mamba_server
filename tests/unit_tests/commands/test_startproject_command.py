from tempfile import mkdtemp
from os.path import join, exists
from shutil import rmtree

from mamba_server.utils.test import get_testenv, cmd_exec, cmd_exec_output


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
        assert cmd_exec(self, 'mamba_server.cmdline', 'startproject',
                        self.project_name) == 0

        assert exists(join(self.proj_path, 'mamba.cfg'))
        assert exists(join(self.proj_path, 'launch'))
        assert exists(join(self.proj_path, 'launch', 'default.launch.json'))
        assert exists(join(self.proj_path, 'components'))
        assert exists(join(self.proj_path, 'components', '__init__.py'))

        output = cmd_exec_output(self, 'mamba_server.cmdline', 'startproject',
                        self.project_name+'2')

        assert 'New Mamba project' in output
        assert 'launch your default project with' in output

        assert cmd_exec(self, 'mamba_server.cmdline', 'startproject',
                        self.project_name) == 1

        output = cmd_exec_output(
            self, 'mamba_server.cmdline', 'startproject', self.project_name)
        assert 'Error' in output
        assert 'mamba.cfg already exists' in output

        assert cmd_exec(self, 'mamba_server.cmdline', 'startproject',
                        'wrong---project---name') == 1

        output = cmd_exec_output(
            self, 'mamba_server.cmdline', 'startproject', 'wrong---project---name')
        assert 'Error' in output
        assert 'Project names must begin with a letter' in output

    def test_startproject_help(self):
        assert cmd_exec(self, 'mamba_server.cmdline', 'startproject',
                        '-h') == 0
        output = cmd_exec_output(
            self, 'mamba_server.cmdline', 'startproject', '-h')
        assert 'Usage' in output
        assert 'mamba startproject <project_name>' in output
        assert 'Options' in output
        assert '--help' in output
