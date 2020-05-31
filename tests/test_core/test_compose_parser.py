import pytest
import os
import sys
from tempfile import mkdtemp
from shutil import rmtree

from mamba.core.compose_parser import compose_parser
from mamba.core.exceptions import ComposeFileException
from mamba.utils.test import get_testenv, cmd_exec
from os.path import join, exists


class TestClass:
    project_name = 'testproject'

    def setup_class(self):
        """ setup_class called once for the class """
        self.temp_path = mkdtemp()
        self.cwd = self.temp_path
        self.proj_path = join(self.temp_path, self.project_name)
        self.env = get_testenv()

        self.current_folder = os.getcwd()
        sys.path.append(join(self.temp_path, self.project_name))

        # Initialize plugin in local folder
        assert cmd_exec(self, 'mamba.cmdline', 'start', self.project_name) == 0
        self.cwd = join(self.temp_path, self.project_name)
        assert cmd_exec(self, 'mamba.cmdline', 'generate', 'plugin',
                        'plugin_1') == 0
        assert exists(join(self.proj_path, 'components', 'plugin', 'plugin_1'))
        assert exists(join(self.proj_path, 'composer'))

        self.mamba_dir = os.path.join(os.path.dirname(__file__), '..', '..',
                         'mamba')

        os.chdir(join(self.temp_path, self.project_name))

    def teardown_class(self):
        """ teardown_class called once for the class """
        os.chdir(self.current_folder)
        rmtree(self.temp_path)
        assert not exists(self.proj_path)
        sys.path.remove(join(self.temp_path, self.project_name))

    def setup_method(self):
        """ setup_method called for every method """
        pass

    def teardown_method(self):
        """ teardown_method called for every method """
        pass

    def dummy(self):
        assert True

    def test_compose_parser(self):
        compose_file_1 = os.path.join(self.proj_path, 'composer', 'test_1.yml')

        f = open(compose_file_1, 'w')
        f.write("version: '0.1'\n")
        f.write("services:\n")
        f.write("  logger:\n")
        f.write("    component: logger\n")
        f.close()

        assert compose_parser(compose_file=compose_file_1,
                              mamba_dir=self.mamba_dir,
                              project_dir=self.proj_path) == 0

        f = open(compose_file_1, 'a+')
        f.write("  local_component:\n")
        f.write("    component: plugin_1\n")
        f.close()

        assert compose_parser(compose_file=compose_file_1,
                              mamba_dir=self.mamba_dir,
                              project_dir=self.proj_path) == 0

    def test_compose_parser_errors(self):
        compose_file = os.path.join(self.proj_path, 'composer', 'test.yml')
        open(compose_file, 'a').close()
        assert exists(compose_file)

        assert compose_parser(compose_file=compose_file,
                              mamba_dir=self.mamba_dir,
                              project_dir=self.proj_path) == 1

        f = open(compose_file, 'a+')
        f.write("version: '0.1'\n")
        f.write("services:\n")
        f.close()

        assert compose_parser(compose_file=compose_file,
                              mamba_dir=self.mamba_dir,
                              project_dir=self.proj_path) == 1

        f = open(compose_file, 'a+')
        f.write("  logger:\n")
        f.close()

        with pytest.raises(ComposeFileException) as excinfo:
            compose_parser(compose_file=compose_file, mamba_dir=self.mamba_dir, project_dir=self.proj_path)

        assert 'logger: missing component property' in str(excinfo.value)

        f = open(compose_file, 'a+')
        f.write("    component: wrong\n")
        f.close()

        with pytest.raises(ComposeFileException) as excinfo:
            compose_parser(compose_file=compose_file, mamba_dir=self.mamba_dir, project_dir=self.proj_path)

        assert "logger: component wrong' is not a valid component identifier" in str(excinfo.value)
