from tempfile import mkdtemp
from os.path import join, exists
from shutil import rmtree

from mamba.utils.test import get_testenv, cmd_exec, cmd_exec_output


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

    def test_generate_valid_project_folder(self):
        assert cmd_exec(self, 'mamba.cmdline', 'start',
                        self.project_name) == 0

        self.cwd = join(self.temp_path, self.project_name)

        assert cmd_exec(self, 'mamba.cmdline', 'generate', 'plugin',
                        'plugin_1') == 0
        assert exists(join(self.proj_path, 'components', 'plugin'))
        assert exists(join(self.proj_path, 'components', 'plugin', 'plugin_1'))
        assert exists(
            join(self.proj_path, 'components', 'plugin', 'plugin_1',
                 '__init__.py'))
        assert exists(
            join(self.proj_path, 'components', 'plugin', 'plugin_1',
                 'config.yml'))

        assert cmd_exec(self, 'mamba.cmdline', 'generate', 'main',
                        'main_1') == 0
        assert exists(join(self.proj_path, 'components', 'main'))
        assert exists(join(self.proj_path, 'components', 'main', 'main_1'))
        assert exists(
            join(self.proj_path, 'components', 'main', 'main_1',
                 '__init__.py'))
        assert exists(
            join(self.proj_path, 'components', 'main', 'main_1', 'config.yml'))

    def test_generate_valid_project_folder_duplicated_name(self):
        assert cmd_exec(self, 'mamba.cmdline', 'start',
                        self.project_name) == 0

        self.cwd = join(self.temp_path, self.project_name)

        assert cmd_exec(self, 'mamba.cmdline', 'generate', 'plugin',
                        'plugin_1') == 0

        output = cmd_exec_output(self, 'mamba.cmdline', 'generate',
                                 'plugin', 'plugin_2')
        assert 'Component' in output
        assert 'plugin_2' in output
        assert 'created in' in output

        assert cmd_exec(self, 'mamba.cmdline', 'generate', 'plugin',
                        'plugin_1') == 1

        output = cmd_exec_output(self, 'mamba.cmdline', 'generate',
                                 'plugin', 'plugin_2')
        assert 'error' in output
        assert 'already exists' in output

        assert cmd_exec(self, 'mamba.cmdline', 'generate', 'main',
                        'main_1') == 0

        output = cmd_exec_output(self, 'mamba.cmdline', 'generate',
                                 'main', 'main_2')
        assert 'Component' in output
        assert 'main_2' in output
        assert 'created in' in output

        assert cmd_exec(self, 'mamba.cmdline', 'generate', 'main',
                        'main_1') == 1

        output = cmd_exec_output(self, 'mamba.cmdline', 'generate',
                                 'main', 'main_2')

        assert 'error' in output
        assert 'already exists' in output

        output = cmd_exec_output(self, 'mamba.cmdline', 'generate',
                                 'wrong', 'comp_1')
        assert 'error' in output
        assert 'not a valid component type' in output

    def test_generate_invalid_project(self):
        assert cmd_exec(self, 'mamba.cmdline', 'generate', 'plugin',
                        'plugin_1') == 1

        output = cmd_exec_output(self, 'mamba.cmdline', 'generate',
                                 'plugin', 'plugin_1')
        assert 'error' in output
        assert 'can only be used inside a Mamba Project' in output

        assert cmd_exec(self, 'mamba.cmdline', 'generate', 'main',
                        'main_1') == 1

        output = cmd_exec_output(self, 'mamba.cmdline', 'generate',
                                 'main', 'main_1')
        assert 'error' in output
        assert 'can only be used inside a Mamba Project' in output

    def test_generate_incomplete_arguments(self):
        assert cmd_exec(self, 'mamba.cmdline', 'start',
                        self.project_name) == 0

        self.cwd = join(self.temp_path, self.project_name)

        assert cmd_exec(self, 'mamba.cmdline', 'generate') == 2

        output = cmd_exec_output(self, 'mamba.cmdline', 'generate')
        assert 'error' in output
        assert 'component_type' in output

        assert cmd_exec(self, 'mamba.cmdline', 'generate',
                        'plugin') == 2

        output = cmd_exec_output(self, 'mamba.cmdline', 'generate',
                                 'plugin')
        assert 'error' in output
        assert 'component_name' in output

    def test_generate_help(self):
        assert cmd_exec(self, 'mamba.cmdline', 'generate', '-h') == 0
        output = cmd_exec_output(self, 'mamba.cmdline', 'generate',
                                 '-h')
        assert 'usage' in output
        assert 'mamba generate <component_type> <component_name>' in output
        assert 'positional arguments' in output
        assert 'component_type' in output
        assert 'component_name' in output
        assert 'optional arguments' in output
        assert '--help' in output
        assert '--list' in output

    def test_generate_list(self):
        assert cmd_exec(self, 'mamba.cmdline', 'generate', '-l') == 0
        output = cmd_exec_output(self, 'mamba.cmdline', 'generate',
                                 '-l')

        assert 'Available component types' in output
        assert 'main' in output
        assert 'plugin' in output
