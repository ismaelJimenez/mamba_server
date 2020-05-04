from setuptools import setup
import os
import sys

_here = os.path.abspath(os.path.dirname(__file__))

if sys.version_info[0] < 3:
    with open(os.path.join(_here, 'README.rst')) as f:
        long_description = f.read()
else:
    with open(os.path.join(_here, 'README.rst'), encoding='utf-8') as f:
        long_description = f.read()

version = {}
with open(os.path.join(_here, 'mamba_controller', 'version.py')) as f:
    exec(f.read(), version)

setup(
    name='mamba_controller',
    version=version['__version__'],
    description=('Show how to structure a Python project.'),
    long_description=long_description,
    author='Mamba Framework',
    author_email='mamba.framework@gmail.com',
    url='https://github.com/mamba-framework/mamba-controller',
    license='MIT',
    packages=['mamba_controller'],
#   no dependencies in this example
#   install_requires=[
#       'dependency==1.2.3',
#   ],
#   no scripts in this example
#   scripts=['bin/a-script'],
    include_package_data=True,
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Science/Research',
        'Programming Language :: Python :: 3.7'],
    )
