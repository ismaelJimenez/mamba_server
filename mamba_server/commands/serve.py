from os import listdir
from os.path import join, exists
from mamba_server.commands import MambaCommand

from mamba_server.context_composer import execute

DEFAULT_LAUNCH_FILE = 'default_qt'
LAUNCH_FILES_DIR = 'launch'


class Command(MambaCommand):
    @staticmethod
    def short_desc():
        return "Start mamba server"

    @staticmethod
    def add_options(parser):
        MambaCommand.add_options(parser)
        parser.add_option("-l",
                          "--list",
                          dest="list",
                          action="store_true",
                          help="List available launch files")
        parser.add_option("-d",
                          "--dump",
                          dest="dump",
                          metavar="store_true",
                          help="Dump launch file to standard output")
        parser.add_option("-r",
                          "--run",
                          dest="run",
                          default=DEFAULT_LAUNCH_FILE,
                          help="Uses a custom launch file.")

    @staticmethod
    def run(args, opts):
        if opts.list:
            _list_launch_files()
            return
        if opts.dump:
            template_file = _find_launch_file(opts.dump)
            if template_file:
                with open(template_file, "r") as f:
                    print(f.read())
            return

        if opts.run:
            if _find_launch_file(opts.run) is not None:
                launch_file = join(LAUNCH_FILES_DIR,
                                   '{}.launch.json'.format(opts.run))

                execute(launch_file)


def _find_launch_file(launch_file):
    launch_file = join(LAUNCH_FILES_DIR, '{}.launch.json'.format(launch_file))
    if exists(launch_file):
        return launch_file
    print("Unable to find launch file: %s\n" % launch_file)
    print('Use "mamba serve --list" to see all available launch files.')
    return None


def _list_launch_files():
    print("Available launch files:")
    for filename in sorted(listdir(LAUNCH_FILES_DIR)):
        if filename.endswith('.launch.json'):
            file_name = filename.split('.')[0]
            if file_name == DEFAULT_LAUNCH_FILE:
                file_name += ' [DEFAULT]'

            print("  {}".format(file_name))
