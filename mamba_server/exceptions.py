"""
Mamba core exceptions
These exceptions are documented in docs/topics/exceptions.rst. Please don't add
new exceptions here without documenting them there.
"""


class ComponentConfigException(Exception):
    """Indicates a missing configuration situation"""
    pass


class LaunchFileException(Exception):
    """Indicates a wrong launch file situation"""
    pass


# Internal


class ComponentSettingsException(Exception):
    """Indicates a wrongly formed setting situation"""
    pass
