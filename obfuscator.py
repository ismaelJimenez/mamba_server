import os
import fileinput
from itertools import chain

rootdir = ['mamba', 'tests']

mapping = ['AppStatus']

for subdir, dirs, files in chain.from_iterable(os.walk(path) for path in rootdir):
    for file in files:
        if not '__pycache__' in subdir and '.py' in file:
            filename = os.path.join(subdir, file)
            print(filename)

            with fileinput.FileInput(filename, inplace=True) as file:
                for line in file:
                    print(line.replace('AppStatus', 'Pepico'), end='')