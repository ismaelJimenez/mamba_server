############################################################################
#
# Copyright (c) Mamba Developers. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#
############################################################################
""" Mamba server dump IF command """

from os.path import join, exists, dirname
from mamba.commands import MambaCommand

from mamba.core.interface_dump import interface_dump
from mamba.commands.serve import _find_launch_file

DEFAULT_LAUNCH_FILE = 'mamba-qt-default'
DEFAULT_IF_DUMP_FILE = 'mamba_if.json'
LAUNCH_FILES_DIR = 'composer'


class Command(MambaCommand):
    """ Mamba server dump IF command """
    @staticmethod
    def short_desc():
        return "Dump mamba server IF"

    @staticmethod
    def add_arguments(parser):
        MambaCommand.add_arguments(parser)

        parser.add_argument("-l",
                            "--load_composer",
                            dest="load_composer",
                            help="Load a Mamba composer file.")

        parser.add_argument("-ls",
                            "--load_standalone_composer",
                            dest="load_standalone_composer",
                            help="Load an standalone Mamba composer file.")

        parser.add_argument("-o",
                            "--output",
                            dest="output",
                            default=DEFAULT_IF_DUMP_FILE,
                            help="Output file.")

    @staticmethod
    def run(args, mamba_dir, project_dir):
        if args.load_standalone_composer:
            project_dir = dirname(dirname(args.load_standalone_composer))
            if exists(args.load_standalone_composer) and exists(
                    join(project_dir, 'mamba.cfg')):
                interface_dump(args.load_standalone_composer, mamba_dir,
                               args.output, project_dir)
            else:
                return 1
        else:
            launch_file = _find_launch_file(DEFAULT_LAUNCH_FILE, mamba_dir,
                                            project_dir)
            if launch_file is not None:
                interface_dump(launch_file, mamba_dir, args.output,
                               project_dir)
            else:
                return 1

            if args.load_composer:
                project_dir = dirname(dirname(args.load_composer))
                if exists(args.load_composer):
                    if exists(join(project_dir, 'mamba.cfg')):
                        interface_dump(args.load_composer, mamba_dir,
                                       args.output, project_dir)
                    else:
                        print(f'Invalid Mamba Project: {project_dir}')
                        return 1
                else:
                    print(f'Unable to find launch file: {args.load_composer}')
                    return 1

        return 0
