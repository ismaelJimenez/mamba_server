""" Mamba server start command """

from os import listdir
from os.path import join, exists
from mamba.commands import MambaCommand

from mamba.core.compose_parser import compose_parser

DEFAULT_LAUNCH_FILE = 'mamba-qt'
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
                            "--list",
                            dest="list",
                            action="store_true",
                            help="List available launch files")
        parser.add_argument("-d",
                            "--dump",
                            dest="dump",
                            metavar="store_true",
                            help="Dump launch file to standard output")
        parser.add_argument("-r",
                            "--run",
                            dest="run",
                            default=DEFAULT_LAUNCH_FILE,
                            help="Uses a custom launch file.")

    @staticmethod
    def run(args, mamba_dir, project_dir):
        if args.list:
            _list_launch_files(mamba_dir, project_dir)
            return 0
        if args.dump:
            template_file = _find_launch_file(args.dump, mamba_dir,
                                              project_dir)
            if template_file:
                with open(template_file, "r") as file:
                    print(file.read())
            return 0

        if args.run:
            launch_file = _find_launch_file(args.run, mamba_dir, project_dir)
            if launch_file is not None:
                compose_parser(launch_file, mamba_dir, project_dir)
            else:
                return 1

        return 1


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


def _list_launch_files(mamba_dir, project_dir):
    print("Available launch files:")
    print("  Mamba:")
    for filename in sorted(listdir(join(mamba_dir, LAUNCH_FILES_DIR))):
        if filename.endswith('-compose.yml'):
            file_name = filename.split('-compose.yml')[0]
            if file_name == DEFAULT_LAUNCH_FILE:
                file_name += ' [DEFAULT]'

            print(f"    - {file_name}")

    if project_dir is not None:
        print("  Local:")
        for filename in sorted(listdir(join(project_dir, LAUNCH_FILES_DIR))):
            if filename.endswith('-compose.yml'):
                file_name = filename.split('-compose.yml')[0]
                if file_name == DEFAULT_LAUNCH_FILE:
                    file_name += ' [DEFAULT]'

                print(f"    - {file_name}")
