import sys

from mamba_server.commands import startproject, serve


def execute(argv=None):
    if argv is None:
        argv = sys.argv

    cmd = argv[1]

    if cmd == 'serve':
        serve.run(argv[2:])
    elif cmd == 'startproject':
        startproject.run(argv[2:])


if __name__ == '__main__':
    execute()

