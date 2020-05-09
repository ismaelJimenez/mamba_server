"""
Mamba - a framework for controlling ground equipment
"""
import sys

__all__ = ['__version__', 'version_info']

# Mamba version
import pkgutil
__version__ = pkgutil.get_data(__package__, 'VERSION').decode('ascii').strip()
version_info = tuple(
    int(v) if v.isdigit() else v for v in __version__.split('.'))
del pkgutil

# Check minimum required Python version
if sys.version_info < (3, 5):
    print("Mamba %s requires Python 3.5" % __version__)
    sys.exit(1)
