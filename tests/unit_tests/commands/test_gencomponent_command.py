from tempfile import mkdtemp
from os.path import join, exists
from shutil import rmtree

from mamba_server.utils.test import get_testenv, cmd_exec


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
        assert cmd_exec(self, 'mamba_server.cmdline', 'startproject', self.project_name) == 0

        self.cwd = join(self.temp_path, self.project_name)

        assert cmd_exec(self, 'mamba_server.cmdline', 'gencomponent', 'plugin', 'plugin_1') == 0
        assert exists(join(self.proj_path, 'components', 'plugin'))
        assert exists(join(self.proj_path, 'components', 'plugin', 'plugin_1'))
        assert exists(
            join(self.proj_path, 'components', 'plugin', 'plugin_1',
                 '__init__.py'))
        assert exists(
            join(self.proj_path, 'components', 'plugin', 'plugin_1',
                 'component.config.json'))

        assert cmd_exec(self, 'mamba_server.cmdline', 'gencomponent', 'main', 'main_1') == 0
        assert exists(join(self.proj_path, 'components', 'main'))
        assert exists(join(self.proj_path, 'components', 'main', 'main_1'))
        assert exists(
            join(self.proj_path, 'components', 'main', 'main_1',
                 '__init__.py'))
        assert exists(
            join(self.proj_path, 'components', 'main', 'main_1',
                 'component.config.json'))

        assert cmd_exec(self, 'mamba_server.cmdline', 'gencomponent', 'load_screen', 'load_screen_1') == 0
        assert exists(join(self.proj_path, 'components', 'load_screen'))
        assert exists(join(self.proj_path, 'components', 'load_screen', 'load_screen_1'))
        assert exists(
            join(self.proj_path, 'components', 'load_screen', 'load_screen_1',
                 '__init__.py'))
        assert exists(
            join(self.proj_path, 'components', 'load_screen', 'load_screen_1',
                 'component.config.json'))

    def test_gencomponent_valid_project_folder_duplicated_name(self):
        assert cmd_exec(self, 'mamba_server.cmdline', 'startproject', self.project_name) == 0

        self.cwd = join(self.temp_path, self.project_name)

        assert cmd_exec(self, 'mamba_server.cmdline', 'gencomponent', 'plugin', 'plugin_1') == 0
        assert cmd_exec(self, 'mamba_server.cmdline', 'gencomponent', 'plugin', 'plugin_1') == 1

        assert cmd_exec(self, 'mamba_server.cmdline', 'gencomponent', 'load_screen', 'load_screen_1') == 0
        assert cmd_exec(self, 'mamba_server.cmdline', 'gencomponent', 'load_screen', 'load_screen_1') == 1

        assert cmd_exec(self, 'mamba_server.cmdline', 'gencomponent', 'main', 'main_1') == 0
        assert cmd_exec(self, 'mamba_server.cmdline', 'gencomponent', 'main', 'main_1') == 1

    def test_gencomponent_invalid_project(self):
        assert cmd_exec(self, 'mamba_server.cmdline', 'gencomponent', 'plugin', 'plugin_1') == 1
        assert cmd_exec(self, 'mamba_server.cmdline', 'gencomponent', 'load_screen', 'load_screen_1') == 1
        assert cmd_exec(self, 'mamba_server.cmdline', 'gencomponent', 'main', 'main_1') == 1
