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

""" Mamba server start command """

from os.path import join, exists, dirname
from mamba.commands import MambaCommand

from mamba.core.composer_parser import compose_parser, start_mamba_app

DEFAULT_LAUNCH_FILE = 'mamba-qt-default'
LAUNCH_FILES_DIR = 'composer'


class Command(MambaCommand):
    """ Mamba server start command """
    @staticmethod
    def short_desc():
        return "Start mamba server"

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

    @staticmethod
    def run(args, mamba_dir, project_dir):
        if args.load_standalone_composer:
            project_dir = dirname(dirname(args.load_standalone_composer))
            if exists(args.load_standalone_composer) and exists(join(project_dir, 'mamba.cfg')):
                compose_parser(args.load_standalone_composer, mamba_dir, join(project_dir))
            else:
                return 1
        else:
            launch_file = _find_launch_file(DEFAULT_LAUNCH_FILE, mamba_dir, project_dir)
            if launch_file is not None:
                compose_parser(launch_file, mamba_dir, project_dir)
            else:
                return 1

            if args.load_composer:
                project_dir = dirname(dirname(args.load_composer))
                if exists(args.load_composer):
                    if exists(join(project_dir, 'mamba.cfg')):
                        compose_parser(args.load_composer, mamba_dir, join(project_dir))
                    else:
                        print(f'Invalid Mamba Project: {project_dir}')
                        return 1
                else:
                    print(f'Unable to find launch file: {args.load_composer}')
                    return 1

        start_mamba_app()

        return 0


def _find_launch_file(launch_file_name, mamba_dir, project_dir):
    launch_file = join(mamba_dir, LAUNCH_FILES_DIR,
                       f'{launch_file_name}-compose.yml')
    if exists(launch_file):
        return launch_file

    if project_dir is not None:
        launch_file = join(project_dir, LAUNCH_FILES_DIR,
                           f'{launch_file_name}-compose.yml')
        if exists(launch_file):
            return launch_file

    print("Unable to find launch file: %s\n" % launch_file_name)
    print('Use "mamba serve --list" to see all available launch files.')
    return None
