"""
Mamba - a framework for controlling ground equipment
"""
import sys

__all__ = ['__version__', 'version_info']

# Mamba version
import pkgutil

version_file = pkgutil.get_data(__package__, 'VERSION')

if version_file is not None:
    __version__ = version_file.decode('ascii').strip()
else:
    __version__ = "0.0.0"

version_info = tuple(
    int(v) if v.isdigit() else v for v in __version__.split('.'))
del pkgutil

# Check minimum required Python version
if sys.version_info < (3, 6):
    print("Mamba %s requires Python 3.6" % __version__)
    sys.exit(1)
