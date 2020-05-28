# -*- coding: utf-8 -*-
"""Script for YAML formatting"""

import subprocess
import os

search_folders = [os.path.join(os.getcwd(), '..', 'mamba')]

for search_folder in search_folders:
    subprocess.call([f'pylint {os.path.abspath(search_folder)}'], shell=True)
