import os
import string

from os.path import join, exists, abspath
from shutil import copytree

from mamba_server.commands import MambaCommand
from mamba_server.exceptions import UsageError

TEMPLATES_DIR = "templates"

COMPONENT_TYPES = {
    'main': "Application main graphical component.",
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
    def add_arguments(parser):
        MambaCommand.add_arguments(parser)
        parser.add_argument("-l",
                          "--list",
                          dest="list",
                          action="store_true",
                          help="List available component types")
        parser.add_argument("component_type", help="Component type template")
        parser.add_argument("component_name", help="New component name")

    @staticmethod
    def templates_dir(mamba_dir, component_type):
        return os.path.join(mamba_dir, TEMPLATES_DIR, 'components',
                            component_type)

    @staticmethod
    def run(args, mamba_dir, project_dir):
        if project_dir is None:
            print(
                "error: 'mamba gencomponent' can only be used inside a Mamba Project"
            )
            return 1

        if args.list:
            _list_component_types()
            return

        component_type = args.component_type
        component_name = args.component_name
        module = _sanitize_module_name(component_name)

        if component_type not in COMPONENT_TYPES:
            print("error: '{}' is not a valid component type".format(
                component_type))
            return 1

        component_dir = join(project_dir, 'components', component_type, module)

        if exists(component_dir):
            print('error: component {} already exists in {}'.format(
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
