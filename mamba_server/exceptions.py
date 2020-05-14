"""
Mamba core exceptions
These exceptions are documented in docs/topics/exceptions.rst. Please don't add
new exceptions here without documenting them there.
"""


class ComponentConfigException(Exception):
    """Indicates a missing configuration situation"""


class LaunchFileException(Exception):
    """Indicates a wrong launch file situation"""


# Commands


class UsageError(Exception):
    """To indicate a command-line usage error"""
    def __init__(self, *a, **kw):
        self.print_help = kw.pop('print_help', True)
        super(UsageError, self).__init__(*a, **kw)


# Internal


class ComponentSettingsException(Exception):
    """Indicates a wrongly formed setting situation"""
