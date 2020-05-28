""" Components creation command """
import os
import string

from os.path import join, exists, abspath
from shutil import copytree

from mamba.commands import MambaCommand

TEMPLATES_DIR = "templates"

COMPONENT_TYPES = {
    'main': "Application main graphical component.",
    'plugin': "Application plugin component."
}


class Command(MambaCommand):
    """ Components creation command """
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
        parser.add_argument("component_type",
                            nargs='?',
                            help="Component type template")
        parser.add_argument("component_name",
                            nargs='?',
                            help="New component name")

    @staticmethod
    def run(args, mamba_dir, project_dir):
        if args.list:
            _list_component_types()
            return 0

        if project_dir is None:
            print("error: 'mamba generate' can only be used inside a "
                  "Mamba Project")
            return 1

        if not args.component_type:
            print("error: 'mamba generate' component_type missing")
            return 2

        if not args.component_name:
            print("error: 'mamba generate' component_name missing")
            return 2

        component_type = args.component_type
        component_name = args.component_name
        module = _sanitize_module_name(component_name)

        if component_type not in COMPONENT_TYPES:
            print(f"error: '{component_type}' is not a valid component type")
            return 1

        component_dir = join(project_dir, 'components', component_type, module)

        if exists(component_dir):
            print(f'error: component {module} already exists in '
                  f'{abspath(component_dir)}')
            return 1

        templates_dir = _templates_dir(mamba_dir, component_type)
        copytree(templates_dir, abspath(component_dir))

        print(f"Component '{module}', using template '{component_type}', "
              f"created in:")
        print(f"    {abspath(component_dir)}\n")
        print(
            "To use the component, please add it to the project launch file.")

        return 0


def _templates_dir(mamba_dir, component_type):
    return os.path.join(mamba_dir, TEMPLATES_DIR, 'components', component_type)


def _list_component_types():
    print("Available component types:")
    for component_type_key, component_type_value in COMPONENT_TYPES.items():
        print(f"  {component_type_key}: {component_type_value}")


def _sanitize_module_name(module_name):
    """Sanitize the given module name, by replacing dashes and points
    with underscores and prefixing it with a letter if it doesn't start
    with one
    """
    module_name = module_name.replace('-', '_').replace('.', '_')
    if module_name[0] not in string.ascii_letters:
        module_name = "a" + module_name
    return module_name
