import sys
from os import path, getcwd
from os.path import exists, join
import optparse

sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))

#pylint: disable=wrong-import-position
import mamba_server
from mamba_server.commands import MambaCommand
from mamba_server.utils.misc import get_classes_from_module
#pylint: enable=wrong-import-position


def _pop_command_name(argv):
    i = 0
    for arg in argv[1:]:
        if not arg.startswith('-'):
            del argv[i]
            return arg
        i += 1


def _print_header():
    print("Mamba {}\n".format(mamba_server.__version__))


def _print_commands():
    _print_header()
    print("Usage:")
    print("  mamba <command> [args]\n")
    print("Available commands:")
    cmds = get_classes_from_module('mamba_server.commands', MambaCommand)
    for cmdname, cmdclass in sorted(cmds.items()):
        print("  %-13s %s" % (cmdname, cmdclass.short_desc()))
    print()
    print('Use "mamba <command> -h" to see more info about a command')


def _print_unknown_command(cmdname):
    _print_header()
    print("Unknown command: %s\n" % cmdname)
    print('Use "mamba" to see available commands')


def execute(argv=None):
    if argv is None:
        argv = sys.argv

    cmds = get_classes_from_module('mamba_server.commands', MambaCommand)
    cmdname = _pop_command_name(argv)
    parser = optparse.OptionParser(formatter=optparse.TitledHelpFormatter(),
                                   conflict_handler='resolve')

    if not cmdname:
        _print_commands()
        sys.exit(0)
    elif cmdname not in cmds:
        _print_unknown_command(cmdname)
        sys.exit(2)

    cmd = cmds[cmdname]
    parser.usage = "mamba %s %s" % (cmdname, cmd.syntax())
    parser.description = cmd.long_desc()
    cmd.add_options(parser)
    opts, args = parser.parse_args(args=argv[1:])

    mamba_dir = path.dirname(path.abspath(__file__))

    project_dir = getcwd() if exists(join(getcwd(), 'mamba.cfg')) else None
    sys.exit(cmd.run(args, opts, mamba_dir, project_dir))


if __name__ == '__main__':
    execute()
