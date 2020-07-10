#!/usr/bin/python
import sys


def dump_to_file():
    if len(sys.argv) > 2:
        file_name = sys.argv[1]
        args = sys.argv[2:]

        file = open(file_name, 'w')
        file.write(' '.join(args))
        file.close()

        return sys.exit(0)
    else:
        return sys.exit(1)


if __name__ == '__main__':
    dump_to_file()
