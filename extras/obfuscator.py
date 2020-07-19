import os
import string
import random
import fileinput
from itertools import chain


def get_random_alphanumeric_string():
    length = random.randint(5, 10)
    letters_and_digits = string.ascii_letters + string.digits
    return random.choice(string.ascii_letters) + ''.join((random.choice(letters_and_digits) for i in range(length)))


rootdir = ['mamba/core', 'mamba/commands', 'tests']

blank_mapping = [
    ' -> None',
    ': Context',
    ': Optional[Dict[str, dict]]',
    ': RunAction',
    ': str',
    ': type',
    '-> Iterator[Callable]',
    '-> List[ModuleType]',
    ': Dict[str, dict]',
    ': List[str]',
    ': Optional[str]',
    '-> int',
    ': Any',
    ': List[ParameterInfo]',
    ': Menu',
    ': RegisterAction',
    ': Empty',
    '-> Menu',
    ': AppStatus',
    '-> bool',
    '-> Any'
]

random_mapping = [
    'rx_value',
    'get_components',
    'merge_dicts',
    '_walk_modules',
    'component_type',
    ('mamba_dir', ["'mamba_dir'"]),
    ('project_dir', ["'project_dir'"]),
    'compose_parser',
    'compose_file'
]

instance_random_mapping = []
for map in random_mapping:
    instance_random_mapping.append((map, get_random_alphanumeric_string()))

for subdir, dirs, files in chain.from_iterable(os.walk(path) for path in rootdir):
    for file in files:
        if not '__pycache__' in subdir and '.py' in file:
            filename = os.path.join(subdir, file)
            print(filename)

            with fileinput.FileInput(filename, inplace=True) as file:
                in_comment = False
                for line in file:
                    if '# ' in line:
                        new_line = line.split('#', 1)[0].rstrip()
                        if new_line != '':
                            print(new_line, end='\n')

                        continue

                    if '"""' in line:
                        if line.rstrip()[-3:] == '"""':
                            new_line = line.split('"""', 1)[0].rstrip()
                            if not in_comment and new_line != '':
                                print(new_line, end='\n')

                            if line.count('"') == 6 or in_comment:
                                in_comment = False
                            else:
                                in_comment = True

                            continue
                        else:
                            in_comment = True

                    if in_comment:
                        continue

                    for map in blank_mapping:
                        line = line.replace(map, '')

                    for map in instance_random_mapping:
                        if isinstance(map[0], tuple):
                            exclude = False
                            for exclude_str in map[0][1]:
                                if exclude_str in line:
                                    exclude = True
                            if not exclude:
                                line = line.replace(map[0][0], map[1])
                        else:
                            line = line.replace(map[0], map[1])

                    print(line, end='')
