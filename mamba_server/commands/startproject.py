import os
import re

from os.path import join, exists, abspath
from os import getcwd
from importlib import import_module
from shutil import ignore_patterns, copy2, copystat

from mamba_server.commands import MambaCommand
from mamba_server.exceptions import UsageError

TEMPLATES_DIR = "templates"
IGNORE = ignore_patterns('*.pyc', '.svn')


class Command(MambaCommand):
    @staticmethod
    def syntax():
        return "<project_name>"

    @staticmethod
    def short_desc():
        return "Create new project"

    @staticmethod
    def templates_dir(mamba_dir):
        return os.path.join(mamba_dir, TEMPLATES_DIR, 'project')

    @staticmethod
    def _copytree(src, dst):
        """
        Since the original function always creates the directory, to resolve
        the issue a new function had to be created. It's a simple copy and
        was reduced for this case.
        """
        ignore = IGNORE
        names = os.listdir(src)
        ignored_names = ignore(src, names)

        if not os.path.exists(dst):
            os.makedirs(dst)

        for name in names:
            if name in ignored_names:
                continue

            srcname = os.path.join(src, name)
            dstname = os.path.join(dst, name)
            if os.path.isdir(srcname):
                Command._copytree(srcname, dstname)
            else:
                copy2(srcname, dstname)
        copystat(src, dst)

    @staticmethod
    def add_arguments(parser):
        MambaCommand.add_arguments(parser)
        parser.add_argument("project_name", help="New project folder name")

    @staticmethod
    def run(args, mamba_dir, project_dir):
        project_name = args.project_name

        project_dir = join(getcwd(), project_name)

        if exists(join(project_dir, 'mamba.cfg')):
            print('Error: mamba.cfg already exists in {}'.format(
                abspath(project_dir)))
            return 1

        if not Command._is_valid_name(project_name):
            return 1

        templates_dir = Command.templates_dir(mamba_dir)
        Command._copytree(templates_dir, abspath(project_dir))

        print("New Mamba project '{}', using template directory '{}', "
              "created in:".format(project_name, templates_dir))
        print("    {}\n".format(abspath(project_dir)))
        print("You can launch your default project with:")
        print("    cd {}".format(project_dir))
        print("    mamba serve -r default")

    @staticmethod
    def _is_valid_name(project_name):
        def _module_exists(module_name):
            try:
                import_module(module_name)
                return True
            except ImportError:
                return False

        if not re.search(r'^[_a-zA-Z]\w*$', project_name):
            print('Error: Project names must begin with a letter and contain'
                  ' only\nletters, numbers and underscores')
        elif _module_exists(project_name):
            print('Error: Module %r already exists' % project_name)
        else:
            return True
        return False
