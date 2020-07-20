#############################################################################
##
## Copyright (C) 2020 The Mamba Company.
## Contact: themambacompany@gmail.com
##
## This file is part of Mamba Server.
##
## $MAMBA_BEGIN_LICENSE:LGPL$
## Commercial License Usage
## Licensees holding valid commercial Mamba licenses may use this file in
## accordance with the commercial license agreement provided with the
## Software or, alternatively, in accordance with the terms contained in
## a written agreement between you and The Mamba Company. For licensing terms
## and conditions see LICENSE. For further information contact us at
## themambacompany@gmail.com.
##
## GNU Lesser General Public License Usage
## Alternatively, this file may be used under the terms of the GNU Lesser
## General Public License version 3 as published by the Free Software
## Foundation and appearing in the file LICENSE.LGPL3 included in the
## packaging of this file. Please review the following information to
## ensure the GNU Lesser General Public License version 3 requirements
## will be met: https://www.gnu.org/licenses/lgpl-3.0.html.
##
## GNU General Public License Usage
## Alternatively, this file may be used under the terms of the GNU
## General Public License version 2.0 or (at your option) the GNU General
## Public license version 3 or any later version approved by the KDE Free
## Qt Foundation. The licenses are as published by the Free Software
## Foundation and appearing in the file LICENSE.GPL2 and LICENSE.GPL3
## included in the packaging of this file. Please review the following
## information to ensure the GNU General Public License requirements will
## be met: https://www.gnu.org/licenses/gpl-2.0.html and
## https://www.gnu.org/licenses/gpl-3.0.html.
##
## $MAMBA_END_LICENSE$
##
#############################################################################

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
