from os import listdir
from os.path import join, exists
from mamba_server.commands import MambaCommand

from mamba_server.context_composer import execute

DEFAULT_LAUNCH_FILE = 'mamba_qt'
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
    def run(args, opts, mamba_dir):
        if opts.list:
            _list_launch_files(mamba_dir)
            return
        if opts.dump:
            template_file = _find_launch_file(opts.dump, mamba_dir)
            if template_file:
                with open(template_file, "r") as f:
                    print(f.read())
            return

        if opts.run:
            if _find_launch_file(opts.run, mamba_dir) is not None:
                launch_file = join(mamba_dir, LAUNCH_FILES_DIR,
                                   '{}.launch.json'.format(opts.run))

                execute(launch_file, mamba_dir)


def _find_launch_file(launch_file, mamba_dir):
    launch_file = join(mamba_dir, LAUNCH_FILES_DIR,
                       '{}.launch.json'.format(launch_file))
    if exists(launch_file):
        return launch_file
    print("Unable to find launch file: %s\n" % launch_file)
    print('Use "mamba serve --list" to see all available launch files.')
    return None


def _list_launch_files(mamba_dir):
    print("Available launch files:")
    for filename in sorted(listdir(join(mamba_dir, LAUNCH_FILES_DIR))):
        if filename.endswith('.launch.json'):
            file_name = filename.split('.')[0]
            if file_name == DEFAULT_LAUNCH_FILE:
                file_name += ' [DEFAULT]'

            print("  {}".format(file_name))
