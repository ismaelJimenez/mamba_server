import pytest
import os
import sys
from tempfile import mkdtemp
from shutil import rmtree

from mamba.core.compose_parser import compose_parser
from mamba.core import utils
from mamba.core.component_base import Component
from mamba.core.testing.utils import get_testenv, cmd_exec
from os.path import join, exists
from mamba.core.context import Context
from mamba.core.exceptions import ComposeFileException


class TestClass:
    project_name = 'test_compose_parser'

    def setup_class(self):
        """ setup_class called once for the class """
        self.temp_path = mkdtemp()
        self.cwd = self.temp_path
        self.proj_path = join(self.temp_path, self.project_name)
        self.env = get_testenv()

        self.current_folder = os.getcwd()
        sys.path.append(join(self.temp_path, self.project_name))

        # Initialize plugin in local folder
        assert cmd_exec(self, 'mamba', 'start', self.project_name) == 0
        self.cwd = join(self.temp_path, self.project_name)
        assert cmd_exec(self, 'mamba', 'generate', 'plugin', 'plugin_1') == 0
        assert exists(join(self.proj_path, 'component', 'plugin', 'plugin_1'))
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

    def test_compose_parser(self):
        compose_file_1 = os.path.join(self.proj_path, 'composer', 'test_1.yml')

        f = open(compose_file_1, 'w')
        f.write("version: '0.1'\n")
        f.write("services:\n")
        f.write("  local_component:\n")
        f.write("    component: plugin_1\n")
        f.close()

        assert compose_parser(compose_file=compose_file_1,
                              mamba_dir=self.mamba_dir,
                              project_dir=self.proj_path) == 0

    def test_get_classes_from_module_components_local(self):
        # Test component load
        classes_dict = utils.get_classes_from_module('component',
                                                     Component)
        assert len(classes_dict) == 1
        assert 'plugin_1' in classes_dict

    def test_get_components_local(self):
        components_dict = utils.get_components(
            {
                'about': {
                    'component': 'about_qt'
                },
                'quit': {
                    'component': 'quit'
                }
            }, ['mamba.component'], Component, Context())
        assert len(components_dict) == 2
        assert 'about' in components_dict
        assert 'quit' in components_dict

        components_dict = utils.get_components(
            {'plugin_1': {
                'component': 'about_qt'
            }}, ['component', 'mamba.component'], Component, Context())
        assert len(components_dict) == 1
        assert 'plugin_1' in components_dict

        components_dict = utils.get_components(
            {
                'about': {
                    'component': 'about_qt'
                },
                'about_1': {
                    'component': 'about_qt'
                },
                'quit': {
                    'component': 'quit'
                },
                'plugin_1': {
                    'component': 'about_qt'
                }
            }, ['mamba.component', 'component'], Component,
            Context())
        assert len(components_dict) == 4
        assert 'about_1' in components_dict
        assert 'about' in components_dict
        assert 'quit' in components_dict
        assert 'plugin_1' in components_dict

    def test_get_components_duplicated_component(self):
        assert cmd_exec(self, 'mamba', 'generate', 'plugin', 'quit') == 0
        assert exists(join(self.proj_path, 'component', 'plugin', 'quit'))

        with pytest.raises(ComposeFileException) as excinfo:
            utils.get_components({'quit': {}},
                                 ['mamba.component', 'component'],
                                 Component, Context())

        assert 'is duplicated' in str(excinfo.value)
        rmtree(join(self.proj_path, 'component', 'plugin', 'quit'))
