import os
import string

from os.path import join, exists, abspath
from shutil import copytree

from mamba_server.commands import MambaCommand
from mamba_server.exceptions import UsageError

TEMPLATES_DIR = "templates"

COMPONENT_TYPES = {
    'app': "Application main graphical component.",
    'plugin': "Application plugin component.",
    'load_screen': "Load screen component.",
}


class Command(MambaCommand):
    @staticmethod
    def syntax():
        return "<component_type> <component_name>"

    @staticmethod
    def short_desc():
        return "Create new component"

    @staticmethod
    def add_options(parser):
        MambaCommand.add_options(parser)
        parser.add_option("-l",
                          "--list",
                          dest="list",
                          action="store_true",
                          help="List available component types")

    @staticmethod
    def templates_dir(mamba_dir, component_type):
        return os.path.join(mamba_dir, TEMPLATES_DIR, 'components',
                            component_type)

    @staticmethod
    def run(args, opts, mamba_dir, project_dir):
        if project_dir is None:
            print(
                "Mamba: 'mamba gencomponent' can only be used inside a Mamba Project"
            )
            return 1

        if opts.list:
            _list_component_types()
            return

        if len(args) != 2:
            raise UsageError(
                "Incorrect number of arguments for 'mamba gencomponent'")

        component_type, component_name = args[0:2]
        module = _sanitize_module_name(component_name)

        if component_type not in COMPONENT_TYPES:
            print("Mamba: '{}' is not a valid component type".format(
                component_type))
            return 1

        component_dir = join(project_dir, 'components', component_type, module)

        if exists(component_dir):
            print('Error: component {} already exists in {}'.format(
                module, abspath(component_dir)))
            return 1

        templates_dir = Command.templates_dir(mamba_dir, component_type)
        copytree(templates_dir, abspath(component_dir))

        print("Component '{}', using template '{}', "
              "created in:".format(module, component_type))
        print("    {}\n".format(abspath(component_dir)))
        print(
            "To use the component, please add it to the project launch file.")


def _list_component_types():
    print("Available component types:")
    for component_type_key, component_type_value in COMPONENT_TYPES.items():
        print("  {}: {}".format(component_type_key, component_type_value))


def _sanitize_module_name(module_name):
    """Sanitize the given module name, by replacing dashes and points
    with underscores and prefixing it with a letter if it doesn't start
    with one
    """
    module_name = module_name.replace('-', '_').replace('.', '_')
    if module_name[0] not in string.ascii_letters:
        module_name = "a" + module_name
    return module_name
