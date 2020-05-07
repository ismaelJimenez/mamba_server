import sys
import optparse
import inspect

import mamba_server
from mamba_server.commands import MambaCommand
from mamba_server.utils.misc import walk_modules


def _iter_command_classes(module_name):
    for module in walk_modules(module_name):
        for obj in vars(module).values():
            if inspect.isclass(obj) and \
                    issubclass(obj, MambaCommand) and \
                    obj.__module__ == module.__name__ and \
                    not obj == MambaCommand:
                yield obj


def _get_commands_from_module(module):
    d = {}
    for cmd in _iter_command_classes(module):
        cmdname = cmd.__module__.split('.')[-1]
        d[cmdname] = cmd()
    return d


def _get_commands_dict():
    cmds = _get_commands_from_module('mamba_server.commands')
    return cmds


def _pop_command_name(argv):
    i = 0
    for arg in argv[1:]:
        if not arg.startswith('-'):
            del argv[i]
            return arg
        i += 1


def _print_header():
    print(f"Mamba {mamba_server.__version__}\n")


def _print_commands():
    _print_header()
    print("Usage:")
    print("  mamba <command> [args]\n")
    print("Available commands:")
    cmds = _get_commands_dict()
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

    cmds = _get_commands_dict()
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
    opts, args = parser.parse_args(args=argv[1:])

    cmd.run(argv[1:])


if __name__ == '__main__':
    execute()
