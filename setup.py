
from os.path import dirname, join
from pkg_resources import parse_version
from setuptools import setup, find_packages, __version__ as setuptools_version


with open(join(dirname(__file__), 'mamba/VERSION'), 'rb') as f:
    version = f.read().decode('ascii').strip()


def has_environment_marker_platform_impl_support():
    """Code extracted from 'pytest/setup.py'
    https://github.com/pytest-dev/pytest/blob/7538680c/setup.py#L31
    The first known release to support environment marker with range operators
    it is 18.5, see:
    https://setuptools.readthedocs.io/en/latest/history.html#id235
    """
    return parse_version(setuptools_version) >= parse_version('18.5')


extras_require = {}

if has_environment_marker_platform_impl_support():
    extras_require[':platform_python_implementation == "PyPy"'] = [
        'PyPyDispatcher>=2.1.0',
    ]


setup(
    name='Mamba-Server',
    version=version,
    url='https://github.com/mamba-framework/mamba-server',
    project_urls={
        'Documentation': 'https://github.com/mamba-framework/mamba-server',
        'Source': 'https://github.com/mamba-framework/mamba-server',
        'Tracker': 'https://github.com/mamba-framework/mamba-server/issues',
    },
    description='Framework for controlling ground equipment',
    long_description=open('README.rst').read(),
    author='Mamba-Server developers',
    maintainer='The Mamba Company',
    maintainer_email='mamba.framework@gmail.com',
    packages=find_packages(exclude=('extras', 'extras.*', 'tests', 'tests.*')),
    include_package_data=True,
    zip_safe=False,
    entry_points={
        "console_scripts": ["mamba = mamba.__main__:execute"]
    },
    classifiers=[
        'Development Status :: 1 - Planning',
        'Environment :: Console',
        'Environment :: MacOS X',
        'Environment :: Win32 (MS Windows)',
        'Environment :: X11 Applications :: Qt ',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)',
        'License :: Other/Proprietary License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',
        'Topic :: Scientific/Engineering',
        'Topic :: Software Development :: Libraries :: Application Frameworks',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    python_requires='>=3.6',
    install_requires=[
        'PySide2==5.14.2.2',
        'Rx>=3.1.0',
        'PyVISA>=1.10.1',
        'PyVISA-sim>=0.3',
        'PyVISA-py>=0.4.0',
        'Flask>=1.1.2'
    ],
    extras_require=extras_require,
)
