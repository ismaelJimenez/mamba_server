################################################################################################
##
##  Copyright (c) Mamba Developers. All rights reserved.
##  Licensed under the MIT License. See License.txt in the project root for license information.
##
################################################################################################

""" Create a new Mamba project folder """

import os
import re

from os.path import join, exists, abspath
from os import getcwd
from importlib import import_module
from shutil import ignore_patterns

from mamba.commands import MambaCommand
from mamba.core.utils import copytree

TEMPLATES_DIR = "templates"
IGNORE = ignore_patterns('*.pyc', '.svn')


class Command(MambaCommand):
    """ Create a new Mamba project folder """
    @staticmethod
    def syntax():
        return "<project_name>"

    @staticmethod
    def short_desc():
        return "Create new project"

    @staticmethod
    def add_arguments(parser):
        MambaCommand.add_arguments(parser)
        parser.add_argument("project_name", help="New project folder name")

    @staticmethod
    def run(args, mamba_dir, project_dir, error_logger=None):
        project_name = args.project_name

        if os.path.isabs(project_name):
            project_dir = project_name
            project_id = os.path.basename(project_name)
        else:
            project_dir = join(getcwd(), project_name)
            project_id = project_name

        if exists(join(project_dir, 'mamba.cfg')):
            msg = f'Error: mamba.cfg already exists in {abspath(project_dir)}'
            if error_logger is None:
                print(msg)
            else:
                error_logger(msg)

            return 1

        if not Command._is_valid_name(project_id, error_logger):
            return 1

        templates_dir = _templates_dir(mamba_dir)
        copytree(templates_dir, abspath(project_dir), IGNORE)

        print(f"New Mamba project '{project_id}', created in:")
        print(f"    {abspath(project_dir)}\n")
        print("You can launch your default project with:")
        print(f"    cd {project_dir}")
        print("    mamba serve -r project")

        return 0

    @staticmethod
    def _is_valid_name(project_name, error_logger):
        def _module_exists(module_name):
            try:
                import_module(module_name)
                return True
            except ImportError:
                return False

        if not re.search(r'^[_a-zA-Z]\w*$', project_name):
            msg = 'Error: Project names must begin with a letter and contain' \
                  ' only\nletters, numbers and underscores'

            if error_logger is None:
                print(msg)
            else:
                error_logger(msg)

        elif _module_exists(project_name):
            msg = f'Error: Module {project_name} already exists'

            if error_logger is None:
                print(msg)
            else:
                error_logger(msg)
        else:
            return True
        return False


def _templates_dir(mamba_dir):
    return os.path.join(mamba_dir, TEMPLATES_DIR, 'project')
