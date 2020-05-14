from tempfile import mkdtemp
from os.path import join, exists
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

    def test_gencomponent_valid_project_folder(self):
        assert cmd_exec(self, 'mamba_server.cmdline', 'startproject',
                        self.project_name) == 0

        self.cwd = join(self.temp_path, self.project_name)

        assert cmd_exec(self, 'mamba_server.cmdline', 'gencomponent', 'plugin',
                        'plugin_1') == 0
        assert exists(join(self.proj_path, 'components', 'plugin'))
        assert exists(join(self.proj_path, 'components', 'plugin', 'plugin_1'))
        assert exists(
            join(self.proj_path, 'components', 'plugin', 'plugin_1',
                 '__init__.py'))
        assert exists(
            join(self.proj_path, 'components', 'plugin', 'plugin_1',
                 'component.config.json'))

        assert cmd_exec(self, 'mamba_server.cmdline', 'gencomponent', 'main',
                        'main_1') == 0
        assert exists(join(self.proj_path, 'components', 'main'))
        assert exists(join(self.proj_path, 'components', 'main', 'main_1'))
        assert exists(
            join(self.proj_path, 'components', 'main', 'main_1',
                 '__init__.py'))
        assert exists(
            join(self.proj_path, 'components', 'main', 'main_1',
                 'component.config.json'))

        assert cmd_exec(self, 'mamba_server.cmdline', 'gencomponent',
                        'load_screen', 'load_screen_1') == 0
        assert exists(join(self.proj_path, 'components', 'load_screen'))
        assert exists(
            join(self.proj_path, 'components', 'load_screen', 'load_screen_1'))
        assert exists(
            join(self.proj_path, 'components', 'load_screen', 'load_screen_1',
                 '__init__.py'))
        assert exists(
            join(self.proj_path, 'components', 'load_screen', 'load_screen_1',
                 'component.config.json'))

    def test_gencomponent_valid_project_folder_duplicated_name(self):
        assert cmd_exec(self, 'mamba_server.cmdline', 'startproject',
                        self.project_name) == 0

        self.cwd = join(self.temp_path, self.project_name)

        assert cmd_exec(self, 'mamba_server.cmdline', 'gencomponent', 'plugin',
                        'plugin_1') == 0

        output = cmd_exec_output(self, 'mamba_server.cmdline', 'gencomponent',
                                 'plugin', 'plugin_2')
        assert 'Component' in output
        assert 'plugin_2' in output
        assert 'created in' in output

        assert cmd_exec(self, 'mamba_server.cmdline', 'gencomponent', 'plugin',
                        'plugin_1') == 1

        output = cmd_exec_output(self, 'mamba_server.cmdline', 'gencomponent',
                                 'plugin', 'plugin_2')
        assert 'error' in output
        assert 'already exists' in output

        assert cmd_exec(self, 'mamba_server.cmdline', 'gencomponent',
                        'load_screen', 'load_screen_1') == 0

        output = cmd_exec_output(self, 'mamba_server.cmdline', 'gencomponent',
                                 'load_screen', 'load_screen_2')
        assert 'Component' in output
        assert 'load_screen_2' in output
        assert 'created in' in output

        assert cmd_exec(self, 'mamba_server.cmdline', 'gencomponent',
                        'load_screen', 'load_screen_1') == 1

        output = cmd_exec_output(self, 'mamba_server.cmdline', 'gencomponent',
                                 'load_screen', 'load_screen_2')

        assert 'error' in output
        assert 'already exists' in output

        assert cmd_exec(self, 'mamba_server.cmdline', 'gencomponent', 'main',
                        'main_1') == 0

        output = cmd_exec_output(self, 'mamba_server.cmdline', 'gencomponent',
                                 'main', 'main_2')
        assert 'Component' in output
        assert 'main_2' in output
        assert 'created in' in output

        assert cmd_exec(self, 'mamba_server.cmdline', 'gencomponent', 'main',
                        'main_1') == 1

        output = cmd_exec_output(self, 'mamba_server.cmdline', 'gencomponent',
                                 'main', 'main_2')

        assert 'error' in output
        assert 'already exists' in output

        output = cmd_exec_output(self, 'mamba_server.cmdline', 'gencomponent',
                                 'wrong', 'comp_1')
        assert 'error' in output
        assert 'not a valid component type' in output

    def test_gencomponent_invalid_project(self):
        assert cmd_exec(self, 'mamba_server.cmdline', 'gencomponent', 'plugin',
                        'plugin_1') == 1

        output = cmd_exec_output(self, 'mamba_server.cmdline', 'gencomponent',
                                 'plugin', 'plugin_1')
        assert 'error' in output
        assert 'can only be used inside a Mamba Project' in output

        assert cmd_exec(self, 'mamba_server.cmdline', 'gencomponent',
                        'load_screen', 'load_screen_1') == 1

        output = cmd_exec_output(self, 'mamba_server.cmdline', 'gencomponent',
                                 'load_screen', 'load_screen_1')
        assert 'error' in output
        assert 'can only be used inside a Mamba Project' in output

        assert cmd_exec(self, 'mamba_server.cmdline', 'gencomponent', 'main',
                        'main_1') == 1

        output = cmd_exec_output(self, 'mamba_server.cmdline', 'gencomponent',
                                 'main', 'main_1')
        assert 'error' in output
        assert 'can only be used inside a Mamba Project' in output

    def test_gencomponent_incomplete_arguments(self):
        assert cmd_exec(self, 'mamba_server.cmdline', 'gencomponent') == 2

        output = cmd_exec_output(self, 'mamba_server.cmdline', 'gencomponent')
        assert 'error' in output
        assert 'component_type, component_name' in output

        assert cmd_exec(self, 'mamba_server.cmdline', 'gencomponent',
                        'plugin') == 2

        output = cmd_exec_output(self, 'mamba_server.cmdline', 'gencomponent',
                                 'plugin')
        assert 'error' in output
        assert 'component_name' in output

    def test_gencomponent_help(self):
        assert cmd_exec(self, 'mamba_server.cmdline', 'gencomponent',
                        '-h') == 0
        output = cmd_exec_output(self, 'mamba_server.cmdline', 'gencomponent',
                                 '-h')
        assert 'usage' in output
        assert 'mamba gencomponent <component_type> <component_name>' in output
        assert 'positional arguments' in output
        assert 'component_type' in output
        assert 'component_name' in output
        assert 'optional arguments' in output
        assert '--help' in output
        assert '--list' in output
