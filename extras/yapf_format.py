# -*- coding: utf-8 -*-
"""Script for YAML formatting"""

import subprocess
import os

search_folders = [os.getcwd(), os.path.join(os.getcwd(), '..', 'mamba_server')]

for search_folder in search_folders:
    subprocess.call([f'yapf -ir {os.path.abspath(search_folder)}'], shell=True)
