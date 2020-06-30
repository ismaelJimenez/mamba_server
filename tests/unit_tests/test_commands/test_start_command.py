from tempfile import mkdtemp
from os.path import join, exists
from shutil import rmtree

from mamba.core.testing.utils import get_testenv, cmd_exec, cmd_exec_output


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

    def test_start_in_new_folder(self):
        assert cmd_exec(self, 'mamba', 'start', self.project_name) == 0

        assert exists(join(self.proj_path, 'mamba.cfg'))
        assert exists(join(self.proj_path, 'composer'))
        assert exists(join(self.proj_path, 'composer', 'project-compose.yml'))
        assert exists(join(self.proj_path, 'component'))
        assert exists(join(self.proj_path, 'component', '__init__.py'))
        assert exists(join(self.proj_path, 'component', 'gui'))
        assert exists(join(self.proj_path, 'component', 'gui', '__init__.py'))
        assert exists(join(self.proj_path, 'component', 'instrument_driver'))
        assert exists(
            join(self.proj_path, 'component', 'instrument_driver',
                 '__init__.py'))
        assert exists(join(self.proj_path, 'log'))
        assert exists(join(self.proj_path, 'log', '__init__.py'))
        assert exists(join(self.proj_path, 'mock'))
        assert exists(join(self.proj_path, 'mock', '__init__.py'))

        output = cmd_exec_output(self, 'mamba', 'start',
                                 self.project_name + '2')

        assert 'New Mamba project' in output
        assert 'launch your default project with' in output

        assert cmd_exec(self, 'mamba', 'start', self.project_name) == 1

        output = cmd_exec_output(self, 'mamba', 'start', self.project_name)
        assert 'Error' in output
        assert 'mamba.cfg already exists' in output

        assert cmd_exec(self, 'mamba', 'start', 'wrong---project---name') == 1

        output = cmd_exec_output(self, 'mamba', 'start',
                                 'wrong---project---name')
        assert 'Error' in output
        assert 'Project names must begin with a letter' in output

    def test_start_help(self):
        assert cmd_exec(self, 'mamba', 'start', '-h') == 0
        output = cmd_exec_output(self, 'mamba', 'start', '-h')
        assert 'usage' in output
        assert 'mamba start <project_name>' in output
        assert 'positional arguments' in output
        assert 'project_name' in output
        assert 'optional arguments' in output
        assert '--help' in output
