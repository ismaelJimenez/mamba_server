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

""" Components creation command """

import os
import string

from os.path import join, exists, abspath
from shutil import copytree

from mamba.commands import MambaCommand

TEMPLATES_DIR = "templates"

COMPONENT_TYPES = {
    'gui': {
        'description': 'Mamba graphical component.',
        'folder': 'gui'
    },
    'visa_instrument_driver': {
        'description': 'Application plugin component.',
        'folder': 'instrument_driver'
    }
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

        component_dir = join(project_dir, 'components', module)

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
    return os.path.join(mamba_dir, TEMPLATES_DIR, 'component',
                        component_type)


def _list_component_types():
    print("Available component types:")
    for component_type_key, component_type_value in COMPONENT_TYPES.items():
        print(f"  {component_type_key}: {component_type_value['description']}")


def _sanitize_module_name(module_name):
    """Sanitize the given module name, by replacing dashes and points
    with underscores and prefixing it with a letter if it doesn't start
    with one
    """
    module_name = module_name.replace('-', '_').replace('.', '_')
    if module_name[0] not in string.ascii_letters:
        module_name = "a" + module_name
    return module_name
