import tempfile
import subprocess
import os
import shutil
import sys

os.chdir('..')

if os.path.exists('dist'):
    shutil.rmtree('dist')

if os.path.exists('build'):
    shutil.rmtree('build')

if os.path.exists('Mamba_Server.egg-info'):
    shutil.rmtree('Mamba_Server.egg-info')

if os.path.exists('mamba/mamba_config.json'):
    os.remove('mamba/mamba_config.json')

with tempfile.TemporaryFile() as out:
    script_state = subprocess.call([sys.executable, 'setup.py', 'sdist', 'bdist_wheel'],
                                   stdout=out,
                                   stderr=out)