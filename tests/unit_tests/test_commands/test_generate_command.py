from tempfile import mkdtemp
from os.path import join, exists
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

    def test_generate_valid_project_folder(self):
        assert cmd_exec(self, 'mamba', 'start', self.project_name) == 0

        self.cwd = join(self.temp_path, self.project_name)

        assert cmd_exec(self, 'mamba', 'generate', 'visa_instrument_driver',
                        'instrument_driver_1') == 0
        assert exists(join(self.proj_path, 'components'))
        assert exists(
            join(self.proj_path, 'components', 'instrument_driver_1'))
        assert exists(
            join(self.proj_path, 'components',
                 'instrument_driver_1', '__init__.py'))
        assert exists(
            join(self.proj_path, 'components',
                 'instrument_driver_1', 'config.yml'))

        assert cmd_exec(self, 'mamba', 'generate', 'gui', 'gui_1') == 0
        assert exists(join(self.proj_path, 'components',))
        assert exists(join(self.proj_path, 'components', 'gui_1'))
        assert exists(
            join(self.proj_path, 'components', 'gui_1', '__init__.py'))
        assert exists(
            join(self.proj_path, 'components', 'gui_1', 'config.yml'))

    def test_generate_valid_project_folder_duplicated_name(self):
        assert cmd_exec(self, 'mamba', 'start', self.project_name) == 0

        self.cwd = join(self.temp_path, self.project_name)

        assert cmd_exec(self, 'mamba', 'generate', 'visa_instrument_driver',
                        'instrument_driver_1') == 0

        output = cmd_exec_output(self, 'mamba', 'generate',
                                 'visa_instrument_driver',
                                 'instrument_driver_2')
        assert 'Component' in output
        assert 'instrument_driver_2' in output
        assert 'created in' in output

        assert cmd_exec(self, 'mamba', 'generate', 'visa_instrument_driver',
                        'instrument_driver_1') == 1

        output = cmd_exec_output(self, 'mamba', 'generate',
                                 'visa_instrument_driver',
                                 'instrument_driver_2')
        assert 'error' in output
        assert 'already exists' in output

        assert cmd_exec(self, 'mamba', 'generate', 'gui', 'gui_1') == 0

        output = cmd_exec_output(self, 'mamba', 'generate', 'gui', 'gui_2')
        assert 'Component' in output
        assert 'gui_2' in output
        assert 'created in' in output

        assert cmd_exec(self, 'mamba', 'generate', 'gui', 'gui_1') == 1

        output = cmd_exec_output(self, 'mamba', 'generate', 'gui', 'gui_2')

        assert 'error' in output
        assert 'already exists' in output

        output = cmd_exec_output(self, 'mamba', 'generate', 'wrong', 'comp_1')
        assert 'error' in output
        assert 'not a valid component type' in output

    def test_generate_invalid_project(self):
        assert cmd_exec(self, 'mamba', 'generate', 'instrument_driver',
                        'instrument_driver_1') == 1

        output = cmd_exec_output(self, 'mamba', 'generate',
                                 'instrument_driver', 'instrument_driver_1')
        assert 'error' in output
        assert 'can only be used inside a Mamba Project' in output

        assert cmd_exec(self, 'mamba', 'generate', 'gui', 'gui_1') == 1

        output = cmd_exec_output(self, 'mamba', 'generate', 'gui', 'gui_1')
        assert 'error' in output
        assert 'can only be used inside a Mamba Project' in output

    def test_generate_incomplete_arguments(self):
        assert cmd_exec(self, 'mamba', 'start', self.project_name) == 0

        self.cwd = join(self.temp_path, self.project_name)

        assert cmd_exec(self, 'mamba', 'generate') == 2

        output = cmd_exec_output(self, 'mamba', 'generate')
        assert 'error' in output
        assert 'component_type' in output

        assert cmd_exec(self, 'mamba', 'generate', 'instrument_driver') == 2

        output = cmd_exec_output(self, 'mamba', 'generate',
                                 'instrument_driver')
        assert 'error' in output
        assert 'component_name' in output

    def test_generate_help(self):
        assert cmd_exec(self, 'mamba', 'generate', '-h') == 0
        output = cmd_exec_output(self, 'mamba', 'generate', '-h')
        assert 'usage' in output
        assert 'mamba generate <component_type> <component_name>' in output
        assert 'positional arguments' in output
        assert 'component_type' in output
        assert 'component_name' in output
        assert 'optional arguments' in output
        assert '--help' in output
        assert '--list' in output

    def test_generate_list(self):
        assert cmd_exec(self, 'mamba', 'generate', '-l') == 0
        output = cmd_exec_output(self, 'mamba', 'generate', '-l')

        assert 'Available component types' in output
        assert 'gui' in output
        assert 'instrument_driver' in output
