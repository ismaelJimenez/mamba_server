# -*- coding: utf-8 -*-
"""Script for YAML formatting"""

import subprocess
import os

search_folders = [
    os.getcwd(),
    os.path.join(os.getcwd(), '..', 'mamba_server'),
    os.path.join(os.getcwd(), '..', 'tests')
]

for search_folder in search_folders:
    subprocess.call([
        "yapf --style='{based_on_style: pep8, column_limit: 99}' -ir " +
        os.path.abspath(search_folder)
    ],
                    shell=True)
