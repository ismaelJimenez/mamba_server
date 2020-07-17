import tempfile
import subprocess
import os
import shutil
import sys

os.chdir('..')
shutil.rmtree('dist')
shutil.rmtree('build')
shutil.rmtree('Mamba_Server.egg-info')

with tempfile.TemporaryFile() as out:
    script_state = subprocess.call([sys.executable, 'setup.py', 'sdist', 'bdist_wheel'],
                                   stdout=out,
                                   stderr=out)